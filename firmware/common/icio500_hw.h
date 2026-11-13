/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Hardware Abstraction)
 */
#pragma once
#include "daisy_seed.h"

namespace icio500 {

struct Hardware {
    daisy::DaisySeed seed;

    // Normalized parameters [0.0f .. 1.0f] mapped from ICIO500 controls
    float mix      = 0.5f;
    float decay    = 0.7f;
    float damping  = 0.4f;
    float mod_rate = 0.25f;
    uint8_t preset = 0;

    void Init(size_t block_size = 48) {
        seed.Configure();
        seed.Init();
        seed.SetAudioBlockSize(block_size);
        seed.SetAudioSampleRate(daisy::SaiHandle::Config::SampleRate::SAI_48KHZ);
    }

    void StartAudio(daisy::AudioHandle::AudioCallback cb) {
        seed.StartAudio(cb);
    }

    void PollControls() {
        // Hook for ICIO500 dual-concentric encoders (MCP23017) or ADC pins
    }
};

} // namespace icio500
