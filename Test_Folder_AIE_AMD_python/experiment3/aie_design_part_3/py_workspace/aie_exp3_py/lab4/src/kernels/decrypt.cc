#include "adf/window/acc_types.h"
#include "aie_api/aie.hpp"
#include "aie_api/aie_adf.hpp"
#include "include.h"
#include <adf.h>
#include <aie_api/utils.hpp>
#include <cstdint>

using namespace adf;

void decrypt(adf::input_buffer<uint8_t> &__restrict image,
             adf::input_buffer<uint8_t> &__restrict key,
             adf::output_buffer<uint8_t> &__restrict output) {
    constexpr int num_elems = KERNEL_IP_IMG_H * KERNEL_IP_IMG_W;
    const uint8_t *__restrict pA = image.data();
    const uint8_t *__restrict pB = key.data();
    uint8_t *__restrict pC = output.data();
    constexpr int vec_size = 32; // 32 x uint8_t = 256 bits
    int temp = 0;
    for (int i = 0; i <= num_elems - vec_size; i+= vec_size)
        chess_prepare_for_pipelining
        {
            aie::vector<uint8_t, vec_size> va = aie::load_v<vec_size>(pA + i);
            aie::vector<uint8_t, vec_size> vb = aie::load_v<vec_size>(pB + i);
            aie::vector<uint8_t, vec_size> vc = aie::bit_xor(va, vb);
            aie::store_v(pC + i, vc);
            temp = i;
        }

    for (int i = temp; i < num_elems; ++i)
        chess_prepare_for_pipelining {
            pC[i] = pA[i] ^ pB[i];
        }
}
