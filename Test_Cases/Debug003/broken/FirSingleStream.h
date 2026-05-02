#ifndef FIR_SINGLE_STREAM_H
#define FIR_SINGLE_STREAM_H

#include <adf.h>
#include <stdint.h>

#define NUM_SAMPLES 32

void clip_signal(adf::input_buffer<int32_t> &in,
                 adf::output_buffer<int32_t> &out);

#endif