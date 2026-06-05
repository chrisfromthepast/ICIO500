#include "daisy_seed.h"
#include "daisysp.h"
#include "RoomoveDSP.h"

using namespace daisy;
using namespace daisysp;

DaisySeed hw;
RoomoveDspState roomoveState;

// Audio Configuration
const int AUDIO_BLOCK_SIZE = 48;  // DSP processing block size
const float PULSE_DURATION_SECONDS = 0.100f;  // 100ms pulse duration
const float PULSE_REPETITION_RATE_HZ = 1.0f;  // 1Hz pulse repetition

// Pink noise and pulse generator variables
PinkNoise pink;
Metro tick;
bool pulseActive = false;
int pulseSamplesRemaining = 0;
int pulseDurationSamples = 0;
const float GAIN_MINUS_18DB = 0.12589f;

// Hardware Pins
const int FADER_PIN = 15; 
const int JUMPER_NOISE_PIN = 13;  // Ground to blast pink noise pulse out of the main output
const int JUMPER_BYPASS_PIN = 14; // Ground to hard-bypass the DSP 

GPIO jumperNoise;
GPIO jumperBypass;

void AudioCallback(AudioHandle::InputBuffer in, AudioHandle::OutputBuffer out, size_t size)
{
    float faderVal = hw.adc.GetFloat(0);
    roomoveDspSetArmorStrength(&roomoveState, faderVal);

    bool noiseMode = !jumperNoise.Read();
    bool bypassMode = !jumperBypass.Read();

    // 1. Pink Noise Calibration Mode (Overrides everything)
    if (noiseMode) 
    {
        for(size_t i = 0; i < size; i++)
        {
            if(tick.Process()) 
            {
                pulseActive = true;
                pulseSamplesRemaining = pulseDurationSamples;
            }
            
            float noiseSample = 0.0f;
            if(pulseActive) 
            {
                noiseSample = pink.Process() * GAIN_MINUS_18DB;
                pulseSamplesRemaining--;
                if(pulseSamplesRemaining <= 0) pulseActive = false;
            }
            // Output to the mono THAT 1646 driver
            out[0][i] = noiseSample;
            out[1][i] = noiseSample;
        }
    }
    // 2. DSP Hard Bypass (AD to DA only)
    else if (bypassMode)
    {
        for(size_t i = 0; i < size; i++)
        {
            out[0][i] = in[0][i];
            out[1][i] = in[0][i];
        }
    }
    // 3. Normal DSP Mode
    else
    {
        processRoomoveAudio(&roomoveState, in[0], out[0], size);
        for(size_t i = 0; i < size; i++)
        {
            out[1][i] = out[0][i];
        }
    }
}

int main(void)
{
    hw.Init();
    hw.SetAudioBlockSize(AUDIO_BLOCK_SIZE); 
    float sampleRate = hw.AudioSampleRate();

    roomoveDspInit(&roomoveState, sampleRate);
    pink.Init();
    tick.Init(PULSE_REPETITION_RATE_HZ, sampleRate);
    pulseDurationSamples = (int)(sampleRate * PULSE_DURATION_SECONDS);

    AdcChannelConfig adcConfig;
    adcConfig.InitSingle(hw.GetPin(FADER_PIN));
    hw.adc.Init(&adcConfig, 1);
    hw.adc.Start();

    jumperNoise.Init(hw.GetPin(JUMPER_NOISE_PIN), GPIO::Mode::INPUT, GPIO::Pull::PULLUP);
    jumperBypass.Init(hw.GetPin(JUMPER_BYPASS_PIN), GPIO::Mode::INPUT, GPIO::Pull::PULLUP);

    hw.StartAudio(AudioCallback);

    while(1)
    {
        System::Delay(10);
    }
}
