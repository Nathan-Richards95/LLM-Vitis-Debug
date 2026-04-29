#include <aie_api/aie.hpp>
#include <aie_api/aie_adf.hpp>
#include "FirSingleStream.h"

void abs_signal(adf::input_buffer<int32_t> &in,
                adf::output_buffer<int32_t> &out) {

    int32_t *input = in.data();
    int32_t *output = out.data();

    for (int i = 0; i < NUM_SAMPLES; i++) {
        if (input[i] < 0) {
            // BUG: should negate negative values
            output[i] = input[i];
        } else {
            output[i] = input[i];
        }
    }
}