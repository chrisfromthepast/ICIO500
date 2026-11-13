/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Hardware & Mode Switcher)
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

// Expandable engine list (starts at 0 = Top LED and steps down the line)
enum class EngineMode : uint8_t {
    kCloudSeed = 0, // Boot default: Algorithmic Reverb (Top LED 0)
    kDaisyVerb = 1, // Dattorro Plate Reverb           (LED 1)
    kFunBox    = 2, // 8x8 FDN + Shimmer Reverb        (LED 2)
    kConvol    = 3, // Partitioned IR Convolution      (Bottom LED 3)
    kRoomove   = 4, // Neural Dereverberation          (Page 2, Top LED 0)
    kCount     = 5
};

struct RgbColor {
    uint8_t r = 0;
    uint8_t g = 0;
    uint8_t b = 0;
};

namespace Palette {
inline constexpr RgbColor kOff    = {0,   0,   0};
inline constexpr RgbColor kPurple = {180, 0,   255}; // Mode Select indicator
inline constexpr RgbColor kCyan   = {0,   220, 255}; // Param 0: Mix / Roomove Level
inline constexpr RgbColor kGreen  = {0,   255, 60};  // Param 1: Decay / Threshold
inline constexpr RgbColor kAmber  = {255, 140, 0};   // Param 2: Damping / Reduction
inline constexpr RgbColor kBlue   = {30,  80,  255}; // Param 3: Mod / Shimmer
} // namespace Palette

struct Params {
    static constexpr size_t kNumParams = 4;

    // Indexed parameter storage [0..3] per mode so each mode remembers its settings
    float mix     = 0.45f; // Param 0 (or Roomove dry/wet level)
    float decay   = 0.78f; // Param 1
    float damping = 0.35f; // Param 2
    float mod     = 0.25f; // Param 3

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

    // Roomove only needs 1 primary level parameter (or up to 3); Reverbs use all 4
    static constexpr size_t ParamCountForMode(EngineMode m) noexcept {
        return (m == EngineMode::kRoomove) ? 1U : kNumParams;
    }
};

// Clickless audio-rate mode switcher (16ms ramp down -> swap -> 16ms ramp up)
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

// Front-panel UI state machine:
// - 2000ms hold -> Mode Select (Purple LED, top LED 0 down to bottom LED 3)
// - Short click in Mode Select -> Confirms mode, returns to Perform mode
// - Short click in Perform mode -> Cycles active parameter (each with dedicated color)
// - Perform mode LEDs -> Fill from bottom (LED 3) to top (LED 0) showing parameter level
class ModeUiController {
public:
    static constexpr size_t   kNumLeds    = 4;    // LED 0 = Top, LED 3 = Bottom
    static constexpr uint32_t kHoldTimeMs = 2000; // 2-second hold for Mode Select
    static constexpr float    kEncStep    = 0.025f;

    void Update(uint32_t now_ms,
                bool     btn_pressed,
                int32_t  enc_delta,
                Params&  params) noexcept {
        // 1. Button press / 2-second hold / short-click detection
        if (btn_pressed && !prev_btn_) {
            btn_down_ms_ = now_ms;
            long_fired_  = false;
        } else if (btn_pressed && !long_fired_ && (now_ms - btn_down_ms_ >= kHoldTimeMs)) {
            // 2 seconds reached: enter (or exit) Mode Select
            in_select_mode_ = !in_select_mode_;
            staged_mode_    = params.mode;
            long_fired_     = true;
        } else if (!btn_pressed && prev_btn_ && !long_fired_) {
            // Short click released before 2 seconds
            if (in_select_mode_) {
                // Confirm staged mode and reset parameter cursor to Param 0
                params.mode     = staged_mode_;
                active_param_   = 0;
                in_select_mode_ = false;
            } else {
                // Cycle through parameters for the current mode
                const size_t num_p = Params::ParamCountForMode(params.mode);
                active_param_      = (active_param_ + 1U) % num_p;
            }
        }
        prev_btn_ = btn_pressed;

        // 2. Encoder rotation handling
        if (enc_delta != 0) {
            if (in_select_mode_) {
                // Step down the LED line (0 = Top -> 1 -> 2 -> 3 = Bottom ...)
                const int32_t count = static_cast<int32_t>(EngineMode::kCount);
                int32_t       next  = static_cast<int32_t>(staged_mode_) + (enc_delta > 0 ? 1 : -1);
                while (next < 0) next += count;
                while (next >= count) next -= count;
                staged_mode_ = static_cast<EngineMode>(next);
            } else {
                // Adjust active parameter level [0.0 .. 1.0]
                const float cur  = params.GetByIndex(active_param_);
                const float next = cur + static_cast<float>(enc_delta) * kEncStep;
                params.SetByIndex(active_param_, next);
            }
        }

        // 3. Render LEDs (LED 0 = Top, LED 3 = Bottom)
        if (in_select_mode_) {
            RenderModeSelectTopToBottom(staged_mode_);
        } else {
            const float    level = params.GetByIndex(active_param_);
            const RgbColor color = Params::ColorForParam(active_param_);
            RenderBargraphBottomToTop(level, color);
        }
    }

    const std::array<RgbColor, kNumLeds>& Leds() const noexcept { return leds_; }
    bool   IsInSelectMode() const noexcept { return in_select_mode_; }
    size_t ActiveParamIndex() const noexcept { return active_param_; }

private:
    // Mode Select: Purple LED starting at Top (LED 0) and stepping down to Bottom (LED 3)
    void RenderModeSelectTopToBottom(EngineMode mode) noexcept {
        leds_.fill(Palette::kOff);
        const size_t idx      = static_cast<size_t>(mode);
        const size_t led_slot = idx % kNumLeds; // 0 = Top LED, 3 = Bottom LED
        leds_[led_slot]       = Palette::kPurple;
    }

    // Perform Mode: Parameter level shown from Bottom (LED 3) to Top (LED 0)
    // using the parameter's dedicated color with proportional dimming on the top active LED
    void RenderBargraphBottomToTop(float level, RgbColor color) noexcept {
        leds_.fill(Palette::kOff);
        const float clamped = ClampUnit(level);
        const float scaled  = clamped * static_cast<float>(kNumLeds); // [0.0 .. 4.0]

        for (size_t step = 0; step < kNumLeds; ++step) {
            // step 0 = Bottom (LED 3), step 3 = Top (LED 0)
            const size_t led_idx = (kNumLeds - 1U) - step;
            const float  cell    = scaled - static_cast<float>(step);

            if (cell >= 1.0f) {
                leds_[led_idx] = color;
            } else if (cell > 0.0f) {
                leds_[led_idx] = {
                    static_cast<uint8_t>(static_cast<float>(color.r) * cell),
                    static_cast<uint8_t>(static_cast<float>(color.g) * cell),
                    static_cast<uint8_t>(static_cast<float>(color.b) * cell),
                };
            }
        }
    }

    std::array<RgbColor, kNumLeds> leds_{};
    EngineMode                     staged_mode_    = EngineMode::kCloudSeed;
    size_t                         active_param_   = 0;
    uint32_t                       btn_down_ms_    = 0;
    bool                           prev_btn_       = false;
    bool                           long_fired_     = false;
    bool                           in_select_mode_ = false;
};

#if defined(DAISY_SEED_H)
class Hardware {
public:
    void Init(size_t block_size = 48) {
        seed_.Configure();
        seed_.Init();
        seed_.SetAudioBlockSize(block_size);
        seed_.SetAudioSampleRate(daisy::SaiHandle::Config::SampleRate::SAI_48KHZ);
    }

    void StartAudio(daisy::AudioHandle::AudioCallback cb) {
        seed_.StartAudio(cb);
    }

    float SampleRate() const noexcept {
        return seed_.AudioSampleRate();
    }

    void PollControls(Params& params) noexcept {
        const uint32_t now_ms = daisy::System::GetNow();
        // Hook: pass combined button/encoder click and encoder delta into UI controller
        ui_.Update(now_ms, raw_btn_pressed_, raw_enc_delta_, params);
        raw_enc_delta_ = 0;
    }

    const ModeUiController& Ui() const noexcept { return ui_; }

private:
    daisy::DaisySeed seed_;
    ModeUiController ui_;
    bool             raw_btn_pressed_ = false;
    int32_t          raw_enc_delta_   = 0;
};
#endif

} // namespace icio500
