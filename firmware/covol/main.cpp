/*
 * MIT License
 * Copyright (c) 2026 VZtec / Chris Williams / SeaDubs (ICIO500 Partitioned Convolution)
 */
#include "icio500_hw.h"
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace icio500::convol {

// Portable Radix-2 Complex FFT / IFFT (No external library dependency required)
template <size_t N>
class Radix2FFT {
    static_assert((N & (N - 1)) == 0, "FFT size N must be a power of two");

public:
    static void Transform(std::array<float, 2 * N>& data, bool inverse) noexcept {
        // Bit-reversal permutation
        size_t j = 0;
        for (size_t i = 0; i < N; ++i) {
            if (i < j) {
                std::swap(data[2 * i], data[2 * j]);
                std::swap(data[2 * i + 1], data[2 * j + 1]);
            }
            size_t m = N >> 1;
            while (m >= 1 && j >= m) {
                j -= m;
                m >>= 1;
            }
            j += m;
        }

        // Danielson-Lanczos butterflies
        const float sign = inverse ? 1.0f : -1.0f;
        for (size_t step = 1; step < N; step <<= 1) {
            const size_t jump  = step << 1;
            const float  delta = sign * 3.14159265358979323846f / static_cast<float>(step);
            const float  s_half = std::sin(0.5f * delta);
            const float  wp_r   = -2.0f * s_half * s_half;
            const float  wp_i   = std::sin(delta);
            float        w_r    = 1.0f;
            float        w_i    = 0.0f;

            for (size_t group = 0; group < step; ++group) {
                for (size_t pair = group; pair < N; pair += jump) {
                    const size_t match = pair + step;
                    const float  tr    = w_r * data[2 * match] - w_i * data[2 * match + 1];
                    const float  ti    = w_r * data[2 * match + 1] + w_i * data[2 * match];

                    data[2 * match]     = data[2 * pair] - tr;
                    data[2 * match + 1] = data[2 * pair + 1] - ti;
                    data[2 * pair]     += tr;
                    data[2 * pair + 1] += ti;
                }
                const float tmp_r = w_r;
                w_r += tmp_r * wp_r - w_i * wp_i;
                w_i += tmp_r * wp_i + w_i * wp_r;
            }
        }

        if (inverse) {
            constexpr float kInvN = 1.0f / static_cast<float>(N);
            for (size_t i = 0; i < 2 * N; ++i) {
                data[i] *= kInvN;
            }
        }
    }
};

// Uniform Partitioned Overlap-Save (UPOLS) Convolution Engine
class PartitionedConvolver {
public:
    static constexpr size_t kBlockSize     = 64;
    static constexpr size_t kFftSize       = 2 * kBlockSize; // 128-pt complex FFT
    static constexpr size_t kNumPartitions = 128;            // 8,192-tap IR (~170ms dense early+tail)

    void Init(float sample_rate) noexcept {
        for (auto& p : fdl_) {
            p.fill(0.0f);
        }
        for (auto& h : ir_spectra_) {
            h.fill(0.0f);
        }
        time_buf_.fill(0.0f);
        overlap_in_.fill(0.0f);
        out_fifo_.fill(0.0f);
        accum_spec_.fill(0.0f);
        fdl_idx_    = 0;
        sample_pos_ = 0;

        SynthesizeDefaultHallIR(sample_rate);
    }

    void SetParams(const Params& p) noexcept {
        mix_ = ClampUnit(p.mix);
    }

    inline void ProcessSample(float in_l, float in_r, float& out_l, float& out_r) noexcept {
        const float mono_in                  = 0.5f * (in_l + in_r);
        overlap_in_[kBlockSize + sample_pos_] = mono_in;

        const float wet = out_fifo_[sample_pos_];
        out_l           = in_l * (1.0f - mix_) + wet * mix_;
        out_r           = in_r * (1.0f - mix_) + wet * mix_;

        ++sample_pos_;
        if (sample_pos_ >= kBlockSize) {
            sample_pos_ = 0;
            ProcessPartitionBlock();
        }
    }

private:
    void SynthesizeDefaultHallIR(float sample_rate) noexcept {
        uint32_t rng = 0x13579BDFU;
        const float tau = 0.35f * (sample_rate > 8000.0f ? sample_rate : 48000.0f);

        for (size_t p = 0; p < kNumPartitions; ++p) {
            time_buf_.fill(0.0f);
            for (size_t n = 0; n < kBlockSize; ++n) {
                rng = rng * 1664525U + 1013904223U;
                const float noise = static_cast<float>(static_cast<int32_t>(rng)) * 4.65661287e-10f;
                const float t     = static_cast<float>(p * kBlockSize + n);
                const float env   = std::exp(-t / tau) * 0.04f;
                time_buf_[2 * n]  = noise * env;
            }
            Radix2FFT<kFftSize>::Transform(time_buf_, false);
            ir_spectra_[p] = time_buf_;
        }
    }

    void ProcessPartitionBlock() noexcept {
        // 1. Pack 2B sliding input window into complex FFT buffer
        for (size_t i = 0; i < kFftSize; ++i) {
            time_buf_[2 * i]     = overlap_in_[i];
            time_buf_[2 * i + 1] = 0.0f;
        }
        // Shift overlap input history
        for (size_t i = 0; i < kBlockSize; ++i) {
            overlap_in_[i] = overlap_in_[i + kBlockSize];
        }

        // 2. Forward FFT into Frequency-Domain Delay Line (FDL)
        Radix2FFT<kFftSize>::Transform(time_buf_, false);
        fdl_[fdl_idx_] = time_buf_;

        // 3. Complex Multiply-Accumulate across all IR partitions
        accum_spec_.fill(0.0f);
        for (size_t p = 0; p < kNumPartitions; ++p) {
            const size_t slot = (fdl_idx_ + kNumPartitions - p) & (kNumPartitions - 1);
            const auto&  X    = fdl_[slot];
            const auto&  H    = ir_spectra_[p];
            for (size_t k = 0; k < kFftSize; ++k) {
                const float xr = X[2 * k];
                const float xi = X[2 * k + 1];
                const float hr = H[2 * k];
                const float hi = H[2 * k + 1];
                accum_spec_[2 * k]     += xr * hr - xi * hi;
                accum_spec_[2 * k + 1] += xr * hi + xi * hr;
            }
        }

        // 4. Inverse FFT and save valid upper B samples (Overlap-Save)
        Radix2FFT<kFftSize>::Transform(accum_spec_, true);
        for (size_t i = 0; i < kBlockSize; ++i) {
            out_fifo_[i] = accum_spec_[2 * (kBlockSize + i)];
        }

        fdl_idx_ = (fdl_idx_ + 1) & (kNumPartitions - 1);
    }

    using ComplexSpec = std::array<float, 2 * kFftSize>;

    std::array<ComplexSpec, kNumPartitions> fdl_{};
    std::array<ComplexSpec, kNumPartitions> ir_spectra_{};
    ComplexSpec                             time_buf_{};
    ComplexSpec                             accum_spec_{};
    std::array<float, kFftSize>             overlap_in_{};
    std::array<float, kBlockSize>           out_fifo_{};

    size_t fdl_idx_    = 0;
    size_t sample_pos_ = 0;
    float  mix_        = 0.40f;
};

} // namespace icio500::convol

namespace {
icio500::Hardware                                        g_hw;
icio500::Params                                          g_params;
ICIO500_SDRAM_BSS icio500::convol::PartitionedConvolver  g_engine;

void AudioCallback(daisy::AudioHandle::InputBuffer  in,
                   daisy::AudioHandle::OutputBuffer out,
                   size_t                           size) {
    for (size_t i = 0; i < size; ++i) {
        g_engine.ProcessSample(in[0][i], in[1][i], out[0][i], out[1][i]);
    }
}
} // namespace

int main() {
    g_hw.Init(64);
    g_engine.Init(g_hw.SampleRate());
    g_engine.SetParams(g_params);
    g_hw.StartAudio(AudioCallback);

    while (true) {
        g_hw.PollControls(g_params);
        g_engine.SetParams(g_params);
        daisy::System::Delay(1);
    }
}
