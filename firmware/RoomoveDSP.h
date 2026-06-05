#pragma once

#include <cstddef>

struct RoomoveDspState
{
    float armorStrength;
};

inline void roomoveDspInit(RoomoveDspState *state, float sampleRate)
{
    (void)sampleRate;
    state->armorStrength = 0.0f;
}

inline void roomoveDspSetArmorStrength(RoomoveDspState *state, float armorStrength)
{
    if(armorStrength < 0.0f)
    {
        armorStrength = 0.0f;
    }
    else if(armorStrength > 1.0f)
    {
        armorStrength = 1.0f;
    }

    state->armorStrength = armorStrength;
}

inline void processRoomoveAudio(RoomoveDspState *state, float *in, float *out, size_t size)
{
    (void)state;

    for(size_t i = 0; i < size; ++i)
    {
        out[i] = in[i];
    }
}
