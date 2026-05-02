#include <aie_api/aie.hpp>
#include <aie_api/aie_adf.hpp>
#include "../broken/FirSingleStream.h"

void clip_signal(adf::input_buffer<int32_t> &in,
                 adf::output_buffer<int32_t> &out) {

    int32_t *input = in.data();
    int32_t *output = out.data();

    for (int i = 0; i < NUM_SAMPLES; i++) {
        if (input[i] > 100) {
            output[i] = 100;
        } else if (input[i] < 0) {
            output[i] = 0;
        } else {
            output[i] = input[i];
        }
    }
}