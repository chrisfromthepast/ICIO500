/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Hardware & PCA9555 UI Driver)
 */
#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>

#if defined(__ARM_ARCH) || defined(DAISY_SEED_H)
#include "daisy_seed.h"
#ifndef ICIO500_SDRAM_BSS
#define ICIO500_SDRAM_BSS DSY_SDRAM_BSS
#endif
#else
#ifndef ICIO500_SDRAM_BSS
#define ICIO500_SDRAM_BSS
#endif
#endif

namespace icio500 {

inline constexpr float ClampUnit(float v) noexcept {
    return v < 0.0f ? 0.0f : (v > 1.0f ? 1.0f : v);
}

// Expandable engine list: starts at Top LED (D1 = index 0) and steps down D1..D10
enum class EngineMode : uint8_t {
    kCloudSeed = 0, // Boot default: Algorithmic Reverb (Top LED D1)
    kDaisyVerb = 1, // Dattorro Plate Reverb           (LED D2)
    kFunBox    = 2, // 8x8 FDN + Shimmer Reverb        (LED D3)
    kConvol    = 3, // Partitioned IR Convolution      (LED D4)
    kRoomove   = 4, // Neural Dereverberation          (LED D5)
    kCount     = 5
};

// 3-bit hardware RGB color for the PCA9555 Encoder RGB pins (P0_1=R, P0_2=G, P0_3=B)
struct RgbColor {
    bool r = false;
    bool g = false;
    bool b = false;
};

namespace Palette {
inline constexpr RgbColor kOff    = {false, false, false};
inline constexpr RgbColor kPurple = {true,  false, true};  // Mode Select: R + B
inline constexpr RgbColor kCyan   = {false, true,  true};  // Param 0 (Mix / Roomove Level): G + B
inline constexpr RgbColor kGreen  = {false, true,  false}; // Param 1 (Decay / Threshold): G
inline constexpr RgbColor kAmber  = {true,  true,  false}; // Param 2 (Damping / Reduction): R + G
inline constexpr RgbColor kBlue   = {false, false, true};  // Param 3 (Mod / Shimmer): B
} // namespace Palette

struct Params {
    static constexpr size_t kNumParams = 4;

    float mix     = 0.45f; // Param 0 (Cyan)
    float decay   = 0.78f; // Param 1 (Green)
    float damping = 0.35f; // Param 2 (Amber)
    float mod     = 0.25f; // Param 3 (Blue)

    EngineMode mode = EngineMode::kCloudSeed; // Boots into Reverb

    float GetByIndex(size_t idx) const noexcept {
        switch (idx & 3U) {
            case 0:  return mix;
            case 1:  return decay;
            case 2:  return damping;
            default: return mod;
        }
    }

    void SetByIndex(size_t idx, float val) noexcept {
        const float clamped = ClampUnit(val);
        switch (idx & 3U) {
            case 0:  mix     = clamped; break;
            case 1:  decay   = clamped; break;
            case 2:  damping = clamped; break;
            default: mod     = clamped; break;
        }
    }

    static constexpr RgbColor ColorForParam(size_t idx) noexcept {
        switch (idx & 3U) {
            case 0:  return Palette::kCyan;
            case 1:  return Palette::kGreen;
            case 2:  return Palette::kAmber;
            default: return Palette::kBlue;
        }
    }

    static constexpr size_t ParamCountForMode(EngineMode m) noexcept {
        return (m == EngineMode::kRoomove) ? 1U : kNumParams;
    }
};

// Clickless audio-rate mode switcher (16ms down -> swap -> 16ms up)
class ModeCrossfader {
public:
    void RequestMode(EngineMode target) noexcept {
        if (target != current_ && target != pending_) {
            pending_    = target;
            fading_out_ = true;
        }
    }

    inline float StepGain(EngineMode& active_out) noexcept {
        constexpr float kStep = 1.0f / (0.016f * 48000.0f);
        if (fading_out_) {
            gain_ -= kStep;
            if (gain_ <= 0.0f) {
                gain_       = 0.0f;
                current_    = pending_;
                fading_out_ = false;
            }
        } else if (gain_ < 1.0f) {
            gain_ += kStep;
            if (gain_ > 1.0f) {
                gain_ = 1.0f;
            }
        }
        active_out = current_;
        return gain_;
    }

private:
    EngineMode current_    = EngineMode::kCloudSeed;
    EngineMode pending_    = EngineMode::kCloudSeed;
    float      gain_       = 1.0f;
    bool       fading_out_ = false;
};

// UI State Machine for 10-Segment Bar Graph (D1=Top .. D10=Bottom) + Illuminated Encoder
class ModeUiController {
public:
    static constexpr size_t   kNumBarLeds = 10;   // D1 (idx 0 = Top) .. D10 (idx 9 = Bottom)
    static constexpr uint32_t kHoldTimeMs = 2000; // 2-second hold for Mode Select
    static constexpr float    kEncStep    = 0.05f;

    void Update(uint32_t now_ms,
                bool     btn_pressed,
                int32_t  enc_delta,
                Params&  params) noexcept {
        // 1. 2-Second Hold vs Short Click
        if (btn_pressed && !prev_btn_) {
            btn_down_ms_ = now_ms;
            long_fired_  = false;
        } else if (btn_pressed && !long_fired_ && (now_ms - btn_down_ms_ >= kHoldTimeMs)) {
            in_select_mode_ = !in_select_mode_;
            staged_mode_    = params.mode;
            long_fired_     = true;
        } else if (!btn_pressed && prev_btn_ && !long_fired_) {
            if (in_select_mode_) {
                params.mode     = staged_mode_;
                active_param_   = 0;
                in_select_mode_ = false;
            } else {
                const size_t num_p = Params::ParamCountForMode(params.mode);
                active_param_      = (active_param_ + 1U) % num_p;
            }
        }
        prev_btn_ = btn_pressed;

        // 2. Encoder Rotation
        if (enc_delta != 0) {
            if (in_select_mode_) {
                const int32_t count = static_cast<int32_t>(EngineMode::kCount);
                int32_t       next  = static_cast<int32_t>(staged_mode_) + (enc_delta > 0 ? 1 : -1);
                while (next < 0) next += count;
                while (next >= count) next -= count;
                staged_mode_ = static_cast<EngineMode>(next);
            } else {
                const float cur  = params.GetByIndex(active_param_);
                const float next = cur + static_cast<float>(enc_delta) * kEncStep;
                params.SetByIndex(active_param_, next);
            }
        }

        // 3. Render 10-LED Bar + Encoder RGB
        bar_leds_.fill(false);
        if (in_select_mode_) {
            enc_rgb_              = Palette::kPurple;
            under_led_            = true;
            const size_t top_down = static_cast<size_t>(staged_mode_) % kNumBarLeds;
            bar_leds_[top_down]   = true; // D1 (index 0) is Top LED, steps down D1 -> D10
        } else {
            enc_rgb_   = Params::ColorForParam(active_param_);
            under_led_ = true;
            // Fill 10-LED Bar from Bottom (D10 = index 9) to Top (D1 = index 0)
            const float  level = ClampUnit(params.GetByIndex(active_param_));
            const size_t lit   = static_cast<size_t>(level * static_cast<float>(kNumBarLeds) + 0.5f);
            for (size_t step = 0; step < lit && step < kNumBarLeds; ++step) {
                const size_t bar_idx = (kNumBarLeds - 1U) - step; // 9 (Bottom) down to 0 (Top)
                bar_leds_[bar_idx]   = true;
            }
        }
    }

    // Packs active-low 16-bit PCA9555 port registers (Port 0 = low byte, Port 1 = high byte)
    // matching faceplate.ato:
    // P0_0 = led_under, P0_1 = ENC_R, P0_2 = ENC_G, P0_3 = ENC_B, P0_4 = D9, P0_5 = D10
    // P1_0..P1_7 = D1..D8
    uint16_t PackPca9555ActiveLow() const noexcept {
        uint8_t port0_active = 0;
        uint8_t port1_active = 0;

        if (under_led_)  port0_active |= (1U << 0);
        if (enc_rgb_.r)  port0_active |= (1U << 1);
        if (enc_rgb_.g)  port0_active |= (1U << 2);
        if (enc_rgb_.b)  port0_active |= (1U << 3);
        if (bar_leds_[8]) port0_active |= (1U << 4); // D9 (near bottom)
        if (bar_leds_[9]) port0_active |= (1U << 5); // D10 (bottom LED)

        for (size_t i = 0; i < 8; ++i) {
            if (bar_leds_[i]) {
                port1_active |= static_cast<uint8_t>(1U << i); // D1 (top) .. D8
            }
        }

        // Invert because LED anodes are tied to V_5V (0 = ON, 1 = OFF)
        const uint8_t p0_reg = static_cast<uint8_t>(~port0_active);
        const uint8_t p1_reg = static_cast<uint8_t>(~port1_active);
        return static_cast<uint16_t>(p0_reg) | (static_cast<uint16_t>(p1_reg) << 8U);
    }

private:
    std::array<bool, kNumBarLeds> bar_leds_{};
    RgbColor                      enc_rgb_        = Palette::kCyan;
    bool                          under_led_      = true;
    EngineMode                    staged_mode_    = EngineMode::kCloudSeed;
    size_t                        active_param_   = 0;
    uint32_t                      btn_down_ms_    = 0;
    bool                          prev_btn_       = false;
    bool                          long_fired_     = false;
    bool                          in_select_mode_ = false;
};

#if defined(DAISY_SEED_H)
class Hardware {
public:
    static constexpr uint8_t kPca9555Addr = 0x20; // 7-bit I2C address with A0=A1=A2=GND

    void Init(size_t block_size = 48) {
        seed_.Configure();
        seed_.Init();
        seed_.SetAudioBlockSize(block_size);
        seed_.SetAudioSampleRate(daisy::SaiHandle::Config::SampleRate::SAI_48KHZ);

        // Initialize Quadrature Encoder on D15 (ENC_A), D16 (ENC_B), D17 (ENC_SW)
        encoder_.Init(daisy::seed::D15, daisy::seed::D16, daisy::seed::D17);

        // Initialize I2C1 on D11 (SCL) and D12 (SDA) for PCA9555 LED Driver
        daisy::I2CHandle::Config i2c_cfg;
        i2c_cfg.periph         = daisy::I2CHandle::Config::Peripheral::I2C_1;
        i2c_cfg.speed          = daisy::I2CHandle::Config::Speed::I2C_400KHZ;
        i2c_cfg.mode           = daisy::I2CHandle::Config::Mode::I2C_MASTER;
        i2c_cfg.pin_config.scl = daisy::seed::D11;
        i2c_cfg.pin_config.sda = daisy::seed::D12;
        i2c_.Init(i2c_cfg);

        // Configure PCA9555 Port 0 & Port 1 as outputs (Register 0x06 & 0x07 = 0x00)
        uint8_t cfg_cmd[3] = {0x06, 0x00, 0x00};
        i2c_.TransmitBlocking(kPca9555Addr, cfg_cmd, 3, 10);
    }

    void StartAudio(daisy::AudioHandle::AudioCallback cb) {
        seed_.StartAudio(cb);
    }

    float SampleRate() const noexcept {
        return seed_.AudioSampleRate();
    }

    void PollControls(Params& params) noexcept {
        encoder_.Debounce();
        const uint32_t now_ms      = daisy::System::GetNow();
        const bool     btn_pressed = encoder_.Pressed();
        const int32_t  enc_delta   = encoder_.Increment();

        ui_.Update(now_ms, btn_pressed, enc_delta, params);

        // Only transmit I2C frame when LED state changes
        const uint16_t packed = ui_.PackPca9555ActiveLow();
        if (packed != prev_leds_) {
            prev_leds_         = packed;
            uint8_t out_cmd[3] = {
                0x02, // PCA9555 Output Port 0 register
                static_cast<uint8_t>(packed & 0xFFU),
                static_cast<uint8_t>((packed >> 8U) & 0xFFU)
            };
            i2c_.TransmitBlocking(kPca9555Addr, out_cmd, 3, 5);
        }
    }

private:
    daisy::DaisySeed seed_;
    daisy::Encoder   encoder_;
    daisy::I2CHandle i2c_;
    ModeUiController ui_;
    uint16_t         prev_leds_ = 0xFFFFU;
};
#endif

} // namespace icio500
