#include <adf.h>
#include "include.h"
#include <stdio.h>

class aie_adf_graph : public adf::graph {
public:
    int num_parts = 4;
    input_gmio image[4];
    input_gmio key[4];
    output_gmio out[4];

    kernel decrypt_k[4];
    kernel thresholding_k[4];

    aie_adf_graph() {
        for(int i = 0; i < num_parts; i++){
            image[i] = input_gmio::create("image" + std::to_string(i), 64, 10000);
            key[i] = input_gmio::create("key" + std::to_string(i), 64, 10000);
            out[i] = output_gmio::create("out" + std::to_string(i), 64, 10000);

            decrypt_k[i] = kernel::create(decrypt);
            source(decrypt_k[i]) = "kernels/decrypt.cc";
            runtime<ratio>(decrypt_k[i]) = 1;

            thresholding_k[i] = kernel::create(thresholding);
            source(thresholding_k[i]) = "kernels/thresholding.cc";
            runtime<ratio>(thresholding_k[i]) = 1;

            connect<>(image[i].out[0], decrypt_k[i].in[0]);
            dimensions(decrypt_k[i].in[0]) = {KERNEL_IP_IMG_H * KERNEL_IP_IMG_W};
            single_buffer(decrypt_k[i].in[0]);

            connect<>(key[i].out[0], decrypt_k[i].in[1]);
            dimensions(decrypt_k[i].in[1]) = {KERNEL_IP_IMG_H * KERNEL_IP_IMG_W};
            single_buffer(decrypt_k[i].in[1]);

            connect<>(decrypt_k[i].out[0], thresholding_k[i].in[0]);
            dimensions(decrypt_k[i].out[0]) = {KERNEL_IP_IMG_H * KERNEL_IP_IMG_W};
            dimensions(thresholding_k[i].in[0]) = {KERNEL_IP_IMG_H * KERNEL_IP_IMG_W};
            single_buffer(thresholding_k[i].in[0]);

            connect<>(thresholding_k[i].out[0], out[i].in[0]);
            dimensions(thresholding_k[i].out[0]) = {KERNEL_IP_IMG_H * KERNEL_IP_IMG_W};
        }
    }
};