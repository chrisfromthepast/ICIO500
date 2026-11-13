#include "daisy_seed.h"
#include "CloudSeed/ReverbController.h"
#include "CloudSeed/FastSin.h"
#include "CloudSeed/AudioLib/ValueTables.h"
#include "CloudSeed/AllpassDiffuser.h"
#include "CloudSeed/MultitapDiffuser.h"

using namespace daisy;

DaisySeed hw;
CloudSeed::ReverbController* reverb = nullptr;

// Allocate CloudSeed's delay line pool in Daisy Seed 64MB SDRAM (up to 32 MB)
DSY_SDRAM_BSS char sdram_pool[32 * 1024 * 1024];
size_t pool_offset = 0;

void* custom_pool_alloc(size_t size) {
    // 4-byte align allocations in SDRAM
    size = (size + 3) & ~static_cast<size_t>(3);
    if (pool_offset + size > sizeof(sdram_pool)) {
        return nullptr;
    }
    void* ptr = &sdram_pool[pool_offset];
    pool_offset += size;
    return ptr;
}

void AudioCallback(AudioHandle::InputBuffer in,
                   AudioHandle::OutputBuffer out,
                   size_t size) {
    // CloudSeed processes non-interleaved float* buffers in-place or L/R
    reverb->Process(const_cast<float*>(in[0]),
                    const_cast<float*>(in[1]),
                    out[0],
                    out[1],
                    size);
}

int main(void) {
    hw.Configure();
    hw.Init();
    hw.SetAudioBlockSize(48);
    hw.SetAudioSampleRate(SaiHandle::Config::SampleRate::SAI_48KHZ);

    // Initialize lookup tables in CloudSeed
    AudioLib::ValueTables::Init();
    CloudSeed::FastSin::Init();

    // Instantiate controller at 48kHz and load initial factory preset (0-9)
    static CloudSeed::ReverbController reverb_instance(48000);
    reverb = &reverb_instance;
    reverb->initFactoryChorus(); // e.g., Chorus / Dullighan / Hyperplane / MediumSpace

    hw.StartAudio(AudioCallback);

    while(1) {
        // Poll ICIO500 encoders / switches and update CloudSeed parameters:
        // reverb->SetParameter(::Parameter::DryOut, val);
        // reverb->SetParameter(::Parameter::LateOut, val);
        // reverb->SetParameter(::Parameter::LineDecay, val);
        // reverb->SetParameter(::Parameter::LateDiffusionFeedback, val);
        System::Delay(1);
    }
}
