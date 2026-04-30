#include "vector_add.hpp"

void vector_add(
    input_window<int32_t>* in0,
    input_window<int32_t>* in1,
    output_window<int32_t>* out
) {
    for (int i = 0; i < VECTOR_SIZE; i++) {
        int32_t a = window_readincr(in0);
        int32_t b = window_readincr(in1);
        window_writeincr(out, a + b);
    }
}