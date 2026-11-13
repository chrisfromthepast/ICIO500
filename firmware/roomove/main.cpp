/*
 * MIT License
 * Copyright (c) 2026 Chris Williams / SeaDubs (ICIO500 Roomove Firmware Target)
 */
#include "icio500_hw.h"
#include "RoomoveDSP.h"
#include <cstddef>
#include <type_traits>
#include <utility>

namespace icio500::roomove {

namespace detail {
template <typename T, typename = void>
struct HasInit : std::false_type {};
template <typename T>
struct HasInit<T, std::void_t<decltype(std::declval<T&>().Init(48000.0f))>> : std::true_type {};

template <typename T, typename = void>
struct HasPrepare : std::false_type {};
template <typename T>
struct HasPrepare<T, std::void_t<decltype(std::declval<T&>().prepare(48000.0f))>> : std::true_type {};

template <typename T, typename = void>
struct HasProcessStereo : std::false_type {};
template <typename T>
struct HasProcessStereo<T, std::void_t<decltype(std::declval<T&>().ProcessSample(
                               0.0f, 0.0f, std::declval<float&>(), std::declval<float&>()))>>
    : std::true_type {};

template <typename T, typename = void>
struct HasProcessMonoCap : std::false_type {};
template <typename T>
struct HasProcessMonoCap<T, std::void_t<decltype(static_cast<float>(std::declval<T&>().ProcessSample(0.0f)))>>
    : std::true_type {};

template <typename T, typename = void>
struct HasProcessMonoLower : std::false_type {};
template <typename T>
struct HasProcessMonoLower<T, std::void_t<decltype(static_cast<float>(std::declval<T&>().processSample(0.0f)))>>
    : std::true_type {};
} // namespace detail

class RoomoveAdapter {
public:
    void Init(float sample_rate) noexcept {
        if constexpr (detail::HasInit<RoomoveDSP>::value) {
            dsp_.Init(sample_rate);
        } else if constexpr (detail::HasPrepare<RoomoveDSP>::value) {
            dsp_.prepare(sample_rate);
        }
    }

    void SetParams(const Params& p) noexcept {
        mix_       = ClampUnit(p.mix);
        threshold_ = ClampUnit(p.decay);
        reduction_ = ClampUnit(p.damping);
    }

    inline void ProcessSample(float in_l, float in_r, float& out_l, float& out_r) noexcept {
        float dry_l = in_l;
        float dry_r = in_r;

        if constexpr (detail::HasProcessStereo<RoomoveDSP>::value) {
            dsp_.ProcessSample(in_l, in_r, dry_l, dry_r);
        } else if constexpr (detail::HasProcessMonoCap<RoomoveDSP>::value) {
            dry_l = dsp_.ProcessSample(in_l);
            dry_r = dsp_.ProcessSample(in_r);
        } else if constexpr (detail::HasProcessMonoLower<RoomoveDSP>::value) {
            dry_l = dsp_.processSample(in_l);
            dry_r = dsp_.processSample(in_r);
        }

        out_l = in_l * (1.0f - mix_) + dry_l * mix_;
        out_r = in_r * (1.0f - mix_) + dry_r * mix_;
    }

private:
    RoomoveDSP dsp_{};
    float      mix_       = 1.0f;
    float      threshold_ = 0.5f;
    float      reduction_ = 0.7f;
};

} // namespace icio500::roomove

namespace {
icio500::Hardware                                    g_hw;
icio500::Params                                      g_params;
ICIO500_SDRAM_BSS icio500::roomove::RoomoveAdapter   g_engine;

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
