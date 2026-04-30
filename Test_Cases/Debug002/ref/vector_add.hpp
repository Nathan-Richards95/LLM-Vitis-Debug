#ifndef VECTOR_ADD_HPP
#define VECTOR_ADD_HPP

#include <adf.h>
#include "include.hpp"

void vector_add(
    input_window<int32_t>* in0,
    input_window<int32_t>* in1,
    output_window<int32_t>* out
);

#endif