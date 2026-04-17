#include <aie_api/aie.hpp>
#include <aie_api/aie_adf.hpp>
#include "include.h"


void thresholding(adf::input_buffer<uint8_t> &__restrict image,
                  adf::output_buffer<uint8_t> &__restrict output) {

    constexpr int num_elems = KERNEL_IP_IMG_H * KERNEL_IP_IMG_W;

    const uint8_t *__restrict pIn = image.data();
    uint8_t *__restrict pOut = output.data();
    constexpr int vec_size = 32; // 32 x uint8_t = 256 bits
    int temp = 0;
    for (int i = 0; i <= num_elems - vec_size; i += vec_size)
        chess_prepare_for_pipelining
        {
            aie::vector<uint8_t, vec_size> vin = aie::load_v<vec_size>(pIn + i);

            // Compare vin > 0 → mask
            auto mask = aie::gt(vin, (uint8_t)0);

            // Select: if >0 → 255, else → 0
            aie::vector<uint8_t, vec_size> vout =
                aie::select((uint8_t)255, (uint8_t)0, mask);

            aie::store_v(pOut + i, vout);
            temp = i;
        }

    for (int i = temp; i < num_elems; ++i)
        chess_prepare_for_pipelining {
            pOut[i] = (pIn[i] > 0) ? 255 : 0;
        }
}