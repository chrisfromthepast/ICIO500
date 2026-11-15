/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Unified Multi-Mode Firmware)
 */
#include "common/icio500_hw.h"

namespace {
icio500::Hardware       g_hw;
icio500::Params         g_params;
icio500::ModeCrossfader g_crossfader;

void AudioCallback(daisy::AudioHandle::InputBuffer  in,
                   daisy::AudioHandle::OutputBuffer out,
                   size_t                           size) {
    for (size_t i = 0; i < size; ++i) {
        icio500::EngineMode active = icio500::EngineMode::kCloudSeed;
        const float fade_gain      = g_crossfader.StepGain(active);

        float wet_l = in[0][i];
        float wet_r = in[1][i];

        switch (active) {
            case icio500::EngineMode::kCloudSeed:
            case icio500::EngineMode::kDaisyVerb:
            case icio500::EngineMode::kFunBox:
            case icio500::EngineMode::kConvol:
            case icio500::EngineMode::kRoomove:
            default:
                break;
        }

        out[0][i] = wet_l * fade_gain;
        out[1][i] = wet_r * fade_gain;
    }
}
} // namespace

int main() {
    g_hw.Init(48);

    // Boot into Reverb (EngineMode::kCloudSeed) showing Param 0 (Cyan, bottom-to-top)
    g_params.mode = icio500::EngineMode::kCloudSeed;
    g_hw.StartAudio(AudioCallback);

    while (true) {
        g_hw.PollControls(g_params);
        g_crossfader.RequestMode(g_params.mode);
        daisy::System::Delay(1);
    }
}
