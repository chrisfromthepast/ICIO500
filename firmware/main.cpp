/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Unified Multi-Mode Firmware)
 */
#include "common/icio500_hw.h"

namespace {
daisy::DaisySeed        g_seed;
icio500::Params         g_params;
icio500::ModeCrossfader g_crossfader;
icio500::ModeUiController g_ui;

void AudioCallback(daisy::AudioHandle::InputBuffer  in,
                   daisy::AudioHandle::OutputBuffer out,
                   size_t                           size) {
    for (size_t i = 0; i < size; ++i) {
        icio500::EngineMode active = icio500::EngineMode::kCloudSeed;
        const float fade_gain      = g_crossfader.StepGain(active);

        float wet_l = in[0][i];
        float wet_r = in[1][i];

        // Dispatch to active engine (boots in kCloudSeed reverb)
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
    g_seed.Configure();
    g_seed.Init();
    g_seed.SetAudioBlockSize(48);
    g_seed.SetAudioSampleRate(daisy::SaiHandle::Config::SampleRate::SAI_48KHZ);

    // Boot default is EngineMode::kCloudSeed (Reverb)
    g_params.mode = icio500::EngineMode::kCloudSeed;
    g_seed.StartAudio(AudioCallback);

    while (true) {
        const uint32_t now_ms = daisy::System::GetNow();

        // Poll push button + 4 encoder switches (from GPIO / MCP23017)
        const bool                mode_btn_pressed = false;
        const std::array<bool, 4> enc_clicked      = {false, false, false, false};
        const int32_t             enc0_delta       = 0;

        g_ui.Update(now_ms, mode_btn_pressed, enc_clicked, enc0_delta, g_params);
        g_crossfader.RequestMode(g_params.mode);

        daisy::System::Delay(1);
    }
}
