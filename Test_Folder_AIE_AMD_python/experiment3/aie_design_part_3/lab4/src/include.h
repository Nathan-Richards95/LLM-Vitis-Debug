#ifndef INCLUDE_H
#define INCLUDE_H
#include <adf/stream/types.h>
#include <adf.h>
#include <aie_api/aie.hpp>

#define KERNEL_IP_IMG_H 128
#define KERNEL_IP_IMG_W 128

using namespace adf;

void decrypt(input_buffer<uint8_t> &__restrict image,
             input_buffer<uint8_t> &__restrict key,
             output_buffer<uint8_t> &__restrict output);

void thresholding(input_buffer<uint8_t> &__restrict image,
                  output_buffer<uint8_t> &__restrict output);

#endif
