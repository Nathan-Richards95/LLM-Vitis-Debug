#pragma once
#include <aie_api/aie.hpp>

using namespace aie;

// Minimal LUT (must match v32int8 type)
alignas(32) static int8_t matB_LUT0[32] = {
    1,2,3,4,5,6,7,8,
    1,2,3,4,5,6,7,8,
    1,2,3,4,5,6,7,8,
    1,2,3,4,5,6,7,8
};