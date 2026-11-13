/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Hardware Abstraction)
 */
#pragma once

#include <algorithm>
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

struct Params {
    float   mix      = 0.45f;
    float   decay    = 0.78f;
    float   damping  = 0.35f;
    float   mod      = 0.25f;
    uint8_t mode     = 0;
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
        // Hook for ICIO500 MCP23017 dual-concentric encoders & switches
        params.mix     = ClampUnit(params.mix);
        params.decay   = ClampUnit(params.decay);
        params.damping = ClampUnit(params.damping);
        params.mod     = ClampUnit(params.mod);
    }

private:
    daisy::DaisySeed seed_;
};
#endif

} // namespace icio500
