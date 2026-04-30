#ifndef GEMM_HPP
#define GEMM_HPP

#include <adf.h>
#include "include.hpp"

void gemm(
    input_window<int32_t>* inA,
    input_window<int32_t>* inB,
    output_window<int32_t>* outC
);

#endif