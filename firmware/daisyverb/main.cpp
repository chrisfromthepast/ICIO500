/*
 * MIT License
 * Copyright (c) 2021 adion12 (DaisyVerb Reverb Topologies)
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Firmware Integration)
 */
#include "icio500_hw.h"
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace icio500::daisyverb {

template <size_t CapacityPow2>
class DelayLine {
    static_assert((CapacityPow2 & (CapacityPow2 - 1)) == 0,
                  "CapacityPow2 must be a power of two");
    static constexpr size_t kMask = CapacityPow2 - 1;

public:
    void Reset() noexcept {
        buffer_.fill(0.0f);
        write_idx_ = 0;
    }

    inline void Write(float sample) noexcept {
        buffer_[write_idx_] = sample;
        write_idx_          = (write_idx_ + 1) & kMask;
    }

    inline float Read(size_t delay_samples) const noexcept {
        const size_t clamped = delay_samples < CapacityPow2 ? delay_samples : kMask;
        return buffer_[(write_idx_ - clamped) & kMask];
    }

    inline float ReadLinear(float delay_samples) const noexcept {
        const float max_del = static_cast<float>(CapacityPow2 - 2);
        const float safe_d  = delay_samples < 1.0f ? 1.0f : (delay_samples > max_del ? max_del : delay_samples);
        const auto  d_int   = static_cast<size_t>(safe_d);
        const float frac    = safe_d - static_cast<float>(d_int);
        const float s0      = buffer_[(write_idx_ - d_int) & kMask];
        const float s1      = buffer_[(write_idx_ - (d_int + 1)) & kMask];
        return s0 + frac * (s1 - s0);
    }

    inline float ProcessAllpass(float in, size_t delay_samples, float coeff) noexcept {
        const float delayed = Read(delay_samples);
        const float v       = in - coeff * delayed;
        Write(v);
        return delayed + coeff * v;
    }

private:
    std::array<float, CapacityPow2> buffer_{};
    size_t                          write_idx_ = 0;
};

class OnePoleLP {
public:
    void Reset() noexcept { state_ = 0.0f; }

    inline float Process(float in, float damping) noexcept {
        const float d = ClampUnit(damping);
        state_        = in * (1.0f - d) + state_ * d;
        return state_;
    }

private:
    float state_ = 0.0f;
};

// Dattorro Figure-Eight Stereo Plate Tank
class DattorroPlateEngine {
public:
    void Init(float sample_rate) noexcept {
        sample_rate_ = sample_rate > 8000.0f ? sample_rate : 48000.0f;
        pre_delay_.Reset();
        for (auto& ap : in_ap_) {
            ap.Reset();
        }
        tank_ap1_l_.Reset();
        tank_ap1_r_.Reset();
        tank_del1_l_.Reset();
        tank_del1_r_.Reset();
        tank_ap2_l_.Reset();
        tank_ap2_r_.Reset();
        tank_del2_l_.Reset();
        tank_del2_r_.Reset();
        input_lp_.Reset();
        damp_l_.Reset();
        damp_r_.Reset();
        tank_l_    = 0.0f;
        tank_r_    = 0.0f;
        lfo_phase_ = 0.0f;
    }

    void SetParams(const Params& p) noexcept {
        mix_   = ClampUnit(p.mix);
        decay_ = ClampUnit(p.decay) * 0.95f; // Bounded for unconditional stability
        damp_  = ClampUnit(p.damping) * 0.90f;
        mod_   = ClampUnit(p.mod) * 16.0f;
    }

    inline void ProcessSample(float in_l, float in_r, float& out_l, float& out_r) noexcept {
        constexpr float kTwoPi = 6.28318530718f;

        const float mono_in = 0.5f * (in_l + in_r);
        pre_delay_.Write(mono_in);
        float sig = input_lp_.Process(pre_delay_.Read(720), 0.25f);

        sig = in_ap_[0].ProcessAllpass(sig, 229, 0.75f);
        sig = in_ap_[1].ProcessAllpass(sig, 173, 0.75f);
        sig = in_ap_[2].ProcessAllpass(sig, 613, 0.625f);
        sig = in_ap_[3].ProcessAllpass(sig, 449, 0.625f);

        lfo_phase_ += 0.8f / sample_rate_;
        if (lfo_phase_ >= 1.0f) {
            lfo_phase_ -= 1.0f;
        }
        const float mod_l = std::sin(kTwoPi * lfo_phase_) * mod_;
        const float mod_r = std::cos(kTwoPi * lfo_phase_) * mod_;

        // Left Tank Branch
        float node_l       = sig + decay_ * tank_r_;
        const float ap1_dl = tank_ap1_l_.ReadLinear(1087.0f + mod_l);
        const float v1_l   = node_l + 0.70f * ap1_dl;
        tank_ap1_l_.Write(v1_l);
        node_l = ap1_dl - 0.70f * v1_l;

        tank_del1_l_.Write(node_l);
        node_l = damp_l_.Process(tank_del1_l_.Read(7187), damp_) * decay_;
        node_l = tank_ap2_l_.ProcessAllpass(node_l, 2909, 0.50f);
        tank_del2_l_.Write(node_l);
        const float next_tank_l = tank_del2_l_.Read(5987);

        // Right Tank Branch
        float node_r       = sig + decay_ * tank_l_;
        const float ap1_dr = tank_ap1_r_.ReadLinear(1459.0f + mod_r);
        const float v1_r   = node_r + 0.70f * ap1_dr;
        tank_ap1_r_.Write(v1_r);
        node_r = ap1_dr - 0.70f * v1_r;

        tank_del1_r_.Write(node_r);
        node_r = damp_r_.Process(tank_del1_r_.Read(6803), damp_) * decay_;
        node_r = tank_ap2_r_.ProcessAllpass(node_r, 4297, 0.50f);
        tank_del2_r_.Write(node_r);
        const float next_tank_r = tank_del2_r_.Read(5101);

        tank_l_ = next_tank_l;
        tank_r_ = next_tank_r;

        const float wet_l = 0.6f * (tank_del1_r_.Read(429)  + tank_del1_r_.Read(4801)
                                  - tank_ap2_r_.Read(3079)  + tank_del2_r_.Read(3217)
                                  - tank_del1_l_.Read(3191) - tank_ap2_l_.Read(301)
                                  - tank_del2_l_.Read(1721));

        const float wet_r = 0.6f * (tank_del1_l_.Read(569)  + tank_del1_l_.Read(5843)
                                  - tank_ap2_l_.Read(1979)  + tank_del2_l_.Read(4309)
                                  - tank_del1_r_.Read(3407) - tank_ap2_r_.Read(541)
                                  - tank_del2_r_.Read(197));

        out_l = in_l * (1.0f - mix_) + wet_l * mix_;
        out_r = in_r * (1.0f - mix_) + wet_r * mix_;
    }

private:
    DelayLine<4096>              pre_delay_;
    std::array<DelayLine<1024>, 4> in_ap_;
    DelayLine<2048>              tank_ap1_l_, tank_ap1_r_;
    DelayLine<8192>              tank_del1_l_, tank_del1_r_;
    DelayLine<8192>              tank_ap2_l_, tank_ap2_r_;
    DelayLine<8192>              tank_del2_l_, tank_del2_r_;

    OnePoleLP input_lp_;
    OnePoleLP damp_l_, damp_r_;

    float sample_rate_ = 48000.0f;
    float tank_l_      = 0.0f;
    float tank_r_      = 0.0f;
    float lfo_phase_   = 0.0f;

    float mix_   = 0.45f;
    float decay_ = 0.75f;
    float damp_  = 0.35f;
    float mod_   = 8.0f;
};

} // namespace icio500::daisyverb

namespace {
icio500::Hardware                          g_hw;
icio500::Params                            g_params;
ICIO500_SDRAM_BSS icio500::daisyverb::DattorroPlateEngine g_engine;

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
