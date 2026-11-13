/*
 * MIT License
 * Copyright (c) 2024 Keith Bloemer / GuitarML (FunBox Reverb Concepts)
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Portable FDN/Shimmer Engine)
 */
#include "icio500_hw.h"
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace icio500::funbox {

// Dual-grain pitch shifter for +1 octave shimmer feedback (Venus / Earth mode)
template <size_t BufferPow2>
class OctaveShimmer {
    static_assert((BufferPow2 & (BufferPow2 - 1)) == 0,
                  "BufferPow2 must be a power of two");
    static constexpr size_t kMask = BufferPow2 - 1;

public:
    void Reset() noexcept {
        buf_.fill(0.0f);
        write_idx_ = 0;
        phasor_    = 0.0f;
    }

    inline float Process(float in) noexcept {
        buf_[write_idx_] = in;

        // Two Hann-windowed read pointers 180 degrees apart pitching +1 octave
        const float p0 = phasor_;
        const float p1 = (phasor_ + 0.5f) >= 1.0f ? (phasor_ - 0.5f) : (phasor_ + 0.5f);

        constexpr float kWindowSpan = static_cast<float>(BufferPow2 / 2);
        const float d0 = (1.0f - p0) * kWindowSpan + 1.0f;
        const float d1 = (1.0f - p1) * kWindowSpan + 1.0f;

        const float w0 = 0.5f * (1.0f - std::cos(6.28318530718f * p0));
        const float w1 = 0.5f * (1.0f - std::cos(6.28318530718f * p1));

        const float out = ReadLinear(d0) * w0 + ReadLinear(d1) * w1;

        write_idx_ = (write_idx_ + 1) & kMask;
        phasor_ += 1.0f / kWindowSpan;
        if (phasor_ >= 1.0f) {
            phasor_ -= 1.0f;
        }
        return out;
    }

private:
    inline float ReadLinear(float delay) const noexcept {
        const auto  d_int = static_cast<size_t>(delay);
        const float frac  = delay - static_cast<float>(d_int);
        const float s0    = buf_[(write_idx_ - d_int) & kMask];
        const float s1    = buf_[(write_idx_ - (d_int + 1)) & kMask];
        return s0 + frac * (s1 - s0);
    }

    std::array<float, BufferPow2> buf_{};
    size_t                        write_idx_ = 0;
    float                         phasor_    = 0.0f;
};

// 8-Delay-Line Hadamard FDN with Shimmer & Tilt EQ
class FunBoxReverbEngine {
    static constexpr size_t kNumLines = 8;
    static constexpr size_t kMaxDelay = 8192;
    static constexpr size_t kMask     = kMaxDelay - 1;

    // Co-prime delay lengths at 48 kHz
    static constexpr std::array<size_t, kNumLines> kLengths = {
        1499, 1877, 2269, 2713, 3259, 3881, 4597, 5419
    };

public:
    void Init(float /*sample_rate*/) noexcept {
        for (auto& line : delay_lines_) {
            line.fill(0.0f);
        }
        lp_state_.fill(0.0f);
        shimmer_l_.Reset();
        shimmer_r_.Reset();
        write_idx_ = 0;
    }

    void SetParams(const Params& p) noexcept {
        mix_     = ClampUnit(p.mix);
        decay_   = ClampUnit(p.decay) * 0.94f;
        damping_ = ClampUnit(p.damping) * 0.85f;
        shimmer_ = ClampUnit(p.mod) * 0.35f;
    }

    inline void ProcessSample(float in_l, float in_r, float& out_l, float& out_r) noexcept {
        std::array<float, kNumLines> delayed{};
        for (size_t i = 0; i < kNumLines; ++i) {
            const size_t r_idx = (write_idx_ - kLengths[i]) & kMask;
            delayed[i]         = delay_lines_[i][r_idx];
        }

        // Fast 8-point orthogonal Hadamard mixing matrix (normalized by 1/sqrt(8))
        std::array<float, kNumLines> mixed = delayed;
        for (size_t stride = 1; stride < kNumLines; stride <<= 1) {
            for (size_t i = 0; i < kNumLines; i += (stride << 1)) {
                for (size_t j = 0; j < stride; ++j) {
                    const float a         = mixed[i + j];
                    const float b         = mixed[i + j + stride];
                    mixed[i + j]          = a + b;
                    mixed[i + j + stride] = a - b;
                }
            }
        }

        constexpr float kNorm = 0.35355339059f; // 1.0f / sqrt(8.0f)
        const float shim_l    = shimmer_l_.Process(delayed[0] + delayed[2]) * shimmer_;
        const float shim_r    = shimmer_r_.Process(delayed[1] + delayed[3]) * shimmer_;

        float wet_l = 0.0f;
        float wet_r = 0.0f;

        for (size_t i = 0; i < kNumLines; ++i) {
            const float in_feed = ((i & 1U) == 0U) ? (in_l + shim_l) : (in_r + shim_r);
            const float fb      = mixed[i] * kNorm * decay_;
            lp_state_[i]        = (in_feed * 0.25f + fb) * (1.0f - damping_) + lp_state_[i] * damping_;
            delay_lines_[i][write_idx_] = lp_state_[i];

            if ((i & 1U) == 0U) {
                wet_l += delayed[i];
            } else {
                wet_r += delayed[i];
            }
        }

        write_idx_ = (write_idx_ + 1) & kMask;

        wet_l *= 0.5f;
        wet_r *= 0.5f;
        out_l = in_l * (1.0f - mix_) + wet_l * mix_;
        out_r = in_r * (1.0f - mix_) + wet_r * mix_;
    }

private:
    std::array<std::array<float, kMaxDelay>, kNumLines> delay_lines_{};
    std::array<float, kNumLines>                        lp_state_{};
    OctaveShimmer<2048>                                 shimmer_l_, shimmer_r_;
    size_t                                              write_idx_ = 0;

    float mix_     = 0.45f;
    float decay_   = 0.80f;
    float damping_ = 0.35f;
    float shimmer_ = 0.20f;
};

} // namespace icio500::funbox

namespace {
icio500::Hardware                                      g_hw;
icio500::Params                                        g_params;
ICIO500_SDRAM_BSS icio500::funbox::FunBoxReverbEngine  g_engine;

void AudioCallback(daisy::AudioHandle::InputBuffer  in,
                   daisy::AudioHandle::OutputBuffer out,
                   size_t                           size) {
    for (size_t i = 0; i < size; ++i) {
        g_engine.ProcessSample(in[0][i], in[1][i], out[0][i], out[1][i]);
    }
}
} // namespace

int main() {
    g_hw.Init(48);
    g_engine.Init(g_hw.SampleRate());
    g_engine.SetParams(g_params);
    g_hw.StartAudio(AudioCallback);

    while (true) {
        g_hw.PollControls(g_params);
        g_engine.SetParams(g_params);
        daisy::System::Delay(1);
    }
}
