/*
 * MIT License
 *
 * Copyright (c) 2021 adion12 (DaisyVerb Reverb Topologies for Daisy Seed)
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Firmware Integration)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include "daisy_seed.h"
#include <cmath>
#include <cstring>

using namespace daisy;

DaisySeed hw;

// ============================================================================
// SDRAM Delay Line Primitives (Pure MIT, No DaisySP-LGPL dependency)
// ============================================================================
template <size_t max_size>
struct DelayLineSDRAM {
    float  buffer[max_size];
    size_t write_ptr = 0;

    void Init() {
        std::memset(buffer, 0, sizeof(buffer));
        write_ptr = 0;
    }

    inline void Write(float sample) {
        buffer[write_ptr] = sample;
        write_ptr = (write_ptr + 1) % max_size;
    }

    inline float Read(size_t delay_samples) const {
        size_t idx = (write_ptr + max_size - delay_samples) % max_size;
        return buffer[idx];
    }

    // Linearly interpolated read for modulated tank delay lines
    inline float ReadHermiteOrLinear(float delay_samples) const {
        int32_t int_delay = static_cast<int32_t>(delay_samples);
        float   frac      = delay_samples - static_cast<float>(int_delay);
        size_t  idx0      = (write_ptr + max_size - int_delay) % max_size;
        size_t  idx1      = (write_ptr + max_size - (int_delay + 1)) % max_size;
        return buffer[idx0] * (1.0f - frac) + buffer[idx1] * frac;
    }

    // Schroeder Allpass helper
    inline float Allpass(float in, size_t delay_samples, float coeff) {
        float delayed = Read(delay_samples);
        float v       = in - coeff * delayed;
        Write(v);
        return delayed + coeff * v;
    }
};

struct OnePoleLP {
    float state = 0.0f;
    inline float Process(float in, float damping) {
        state = in * (1.0f - damping) + state * damping;
        return state;
    }
};

// ============================================================================
// Dattorro Figure-Eight Stereo Plate Tank (48 kHz Scaled Delays in SDRAM)
// ============================================================================
struct DattorroPlate {
    // Pre-delay + 4 Input Diffusers
    DelayLineSDRAM<4800> pre_delay;
    DelayLineSDRAM<512>  in_ap[4];

    // Left & Right Figure-Eight Tank Branches
    DelayLineSDRAM<2048> tank_ap1_l, tank_ap1_r;
    DelayLineSDRAM<8192> tank_del1_l, tank_del1_r;
    DelayLineSDRAM<4096> tank_ap2_l, tank_ap2_r;
    DelayLineSDRAM<8192> tank_del2_l, tank_del2_r;

    OnePoleLP input_lp;
    OnePoleLP damp_l, damp_r;

    float tank_l = 0.0f;
    float tank_r = 0.0f;
    float lfo_phase = 0.0f;
    float sample_rate = 48000.0f;

    // Parameters [0.0f .. 1.0f]
    float mix         = 0.45f;
    float decay       = 0.78f;
    float input_damp  = 0.25f;
    float tank_damp   = 0.35f;
    float pre_del_ms  = 15.0f;
    float mod_depth   = 12.0f; // samples
    float mod_rate_hz = 0.8f;

    // 48 kHz scaled prime delay lengths (from Jon Dattorro 1997 AES paper)
    static constexpr size_t kInApLen[4] = { 229, 173, 613, 449 };
    static constexpr size_t kTankAp1L   = 1087;
    static constexpr size_t kTankAp1R   = 1459;
    static constexpr size_t kTankDel1L  = 7187;
    static constexpr size_t kTankDel1R  = 6803;
    static constexpr size_t kTankAp2L   = 2909;
    static constexpr size_t kTankAp2R   = 4297;
    static constexpr size_t kTankDel2L  = 5987;
    static constexpr size_t kTankDel2R  = 5101;

    void Init(float sr) {
        sample_rate = sr;
        pre_delay.Init();
        for (int i = 0; i < 4; ++i) in_ap[i].Init();
        tank_ap1_l.Init();
        tank_ap1_r.Init();
        tank_del1_l.Init();
        tank_del1_r.Init();
        tank_ap2_l.Init();
        tank_ap2_r.Init();
        tank_del2_l.Init();
        tank_del2_r.Init();
        tank_l = 0.0f;
        tank_r = 0.0f;
        lfo_phase = 0.0f;
    }

    inline void Process(float in_l, float in_r, float& out_l, float& out_r) {
        // 1. Sum to mono for input diffusion & apply pre-delay + bandwidth LP
        float mono_in = 0.5f * (in_l + in_r);
        size_t pre_samples = static_cast<size_t>((pre_del_ms * 0.001f) * sample_rate);
        if (pre_samples >= 4799) pre_samples = 4799;

        pre_delay.Write(mono_in);
        float diffused = input_lp.Process(pre_delay.Read(pre_samples), input_damp);

        // 2. Series Input Allpass Diffusers (0.75, 0.75, 0.625, 0.625)
        diffused = in_ap[0].Allpass(diffused, kInApLen[0], 0.75f);
        diffused = in_ap[1].Allpass(diffused, kInApLen[1], 0.75f);
        diffused = in_ap[2].Allpass(diffused, kInApLen[2], 0.625f);
        diffused = in_ap[3].Allpass(diffused, kInApLen[3], 0.625f);

        // 3. Quadrature LFO for Tank Modulation
        lfo_phase += mod_rate_hz / sample_rate;
        if (lfo_phase >= 1.0f) lfo_phase -= 1.0f;
        const float two_pi = 6.28318530718f;
        float mod_l = std::sin(two_pi * lfo_phase) * mod_depth;
        float mod_r = std::cos(two_pi * lfo_phase) * mod_depth;

        // 4. Left Tank Branch (fed by diffused input + cross-coupled Right tank)
        float node_l = diffused + decay * tank_r;
        // Modulated decaying allpass 1L
        float ap1_l_del = tank_ap1_l.ReadHermiteOrLinear(static_cast<float>(kTankAp1L) + mod_l);
        float v_ap1_l   = node_l + 0.70f * ap1_l_del;
        tank_ap1_l.Write(v_ap1_l);
        node_l = ap1_l_del - 0.70f * v_ap1_l;

        tank_del1_l.Write(node_l);
        node_l = damp_l.Process(tank_del1_l.Read(kTankDel1L), tank_damp);
        node_l *= decay;
        node_l = tank_ap2_l.Allpass(node_l, kTankAp2L, 0.50f);
        tank_del2_l.Write(node_l);
        float next_tank_l = tank_del2_l.Read(kTankDel2L);

        // 5. Right Tank Branch (fed by diffused input + cross-coupled Left tank)
        float node_r = diffused + decay * tank_l;
        // Modulated decaying allpass 1R
        float ap1_r_del = tank_ap1_r.ReadHermiteOrLinear(static_cast<float>(kTankAp1R) + mod_r);
        float v_ap1_r   = node_r + 0.70f * ap1_r_del;
        tank_ap1_r.Write(v_ap1_r);
        node_r = ap1_r_del - 0.70f * v_ap1_r;

        tank_del1_r.Write(node_r);
        node_r = damp_r.Process(tank_del1_r.Read(kTankDel1R), tank_damp);
        node_r *= decay;
        node_r = tank_ap2_r.Allpass(node_r, kTankAp2R, 0.50f);
        tank_del2_r.Write(node_r);
        float next_tank_r = tank_del2_r.Read(kTankDel2R);

        tank_l = next_tank_l;
        tank_r = next_tank_r;

        // 6. Multi-Tap Stereo Output Accumulator
        float wet_l = 0.6f * (tank_del1_r.Read(429)  + tank_del1_r.Read(4801)
                            - tank_ap2_r.Read(3079)  + tank_del2_r.Read(3217)
                            - tank_del1_l.Read(3191) - tank_ap2_l.Read(301)
                            - tank_del2_l.Read(1721));

        float wet_r = 0.6f * (tank_del1_l.Read(569)  + tank_del1_l.Read(5843)
                            - tank_ap2_l.Read(1979)  + tank_del2_l.Read(4309)
                            - tank_del1_r.Read(3407) - tank_ap2_r.Read(541)
                            - tank_del2_r.Read(197));

        out_l = in_l * (1.0f - mix) + wet_l * mix;
        out_r = in_r * (1.0f - mix) + wet_r * mix;
    }
};

// Allocate entire reverb tank in Daisy Seed's 64MB external SDRAM
DSY_SDRAM_BSS DattorroPlate verb;

// ============================================================================
// Real-Time Audio Callback (48 kHz, 48-sample non-interleaved blocks)
// ============================================================================
void AudioCallback(AudioHandle::InputBuffer  in,
                   AudioHandle::OutputBuffer out,
                   size_t                    size) {
    for (size_t i = 0; i < size; ++i) {
        verb.Process(in[0][i], in[1][i], out[0][i], out[1][i]);
    }
}

int main(void) {
    hw.Configure();
    hw.Init();
    hw.SetAudioBlockSize(48);
    hw.SetAudioSampleRate(SaiHandle::Config::SampleRate::SAI_48KHZ);

    verb.Init(hw.AudioSampleRate());

    hw.StartAudio(AudioCallback);

    while (1) {
        // ICIO500 control polling hook (MCP23017 encoders / switches)
        // verb.mix        = ...;
        // verb.decay      = ...;
        // verb.tank_damp  = ...;
        // verb.pre_del_ms = ...;
        System::Delay(1);
    }
}
