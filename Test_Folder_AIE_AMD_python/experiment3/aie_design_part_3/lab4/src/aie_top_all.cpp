#include "aie_top.h"
#include "png_utils/png_utils.cpp"
#include <iostream>
#include <vector>
#include <cstdint>

using namespace adf;

#define INPUT_IMG_H 256
#define INPUT_IMG_W 256
#define NUM_PARTS 4

aie_adf_graph accel;

#if defined(__AIESIM__) || defined(__X86SIM__)
int main(int argc, char **argv) {
    std::cout << "Simulation started!!" << std::endl;

    const char *filename_ip =
        "/data/courses/class_cse494598cen571spring2026_aaror112/Lab4/Stego/stego_group_27.png";
    const char *filename_key =
        "/data/courses/class_cse494598cen571spring2026_aaror112/Lab4/Key_Images/key_group_27.png";
    const char *filename_out = "decrypted_image_out.png";

    std::vector<unsigned char> image;
    std::vector<unsigned char> imageKey;
    unsigned width = 0, height = 0;
    unsigned keyWidth = 0, keyHeight = 0;

    if (!load_decode_and_print_png(filename_ip, image, width, height)) {
        return -1;
    }

    if (!load_decode_and_print_png(filename_key, imageKey, keyWidth, keyHeight)) {
        return -1;
    }

    if (width != INPUT_IMG_W || height != INPUT_IMG_H) {
        std::cerr << "Input image dimensions do not match expected size." << std::endl;
        return -1;
    }

    if (keyWidth != width || keyHeight != height) {
        std::cerr << "Key image dimensions do not match input image." << std::endl;
        return -1;
    }

    constexpr int PART_H = INPUT_IMG_H / 2;
    constexpr int PART_W = INPUT_IMG_W / 2;
    constexpr int BLOCK_SIZE_in_BytesIP = PART_H * PART_W;
    constexpr int BLOCK_SIZE_in_BytesOUT = PART_H * PART_W;

    uint8_t* dinArrayIP[NUM_PARTS];
    uint8_t* dinArrayKey[NUM_PARTS];
    uint8_t* doutArrayOUT[NUM_PARTS];

    for (int i = 0; i < NUM_PARTS; i++) {
        dinArrayIP[i] = (uint8_t*)GMIO::malloc(BLOCK_SIZE_in_BytesIP);
        dinArrayKey[i] = (uint8_t*)GMIO::malloc(BLOCK_SIZE_in_BytesIP);
        doutArrayOUT[i] = (uint8_t*)GMIO::malloc(BLOCK_SIZE_in_BytesOUT);
    }

    // Split image and key into 4 quadrants:
    // part 0 = top-left
    // part 1 = top-right
    // part 2 = bottom-left
    // part 3 = bottom-right
    for (int r = 0; r < PART_H; r++) {
        for (int c = 0; c < PART_W; c++) {
            int localIdx = r * PART_W + c;

            int idx0 = r * INPUT_IMG_W + c;
            int idx1 = r * INPUT_IMG_W + (c + PART_W);
            int idx2 = (r + PART_H) * INPUT_IMG_W + c;
            int idx3 = (r + PART_H) * INPUT_IMG_W + (c + PART_W);

            dinArrayIP[0][localIdx] = image[idx0];
            dinArrayIP[1][localIdx] = image[idx1];
            dinArrayIP[2][localIdx] = image[idx2];
            dinArrayIP[3][localIdx] = image[idx3];

            dinArrayKey[0][localIdx] = imageKey[idx0];
            dinArrayKey[1][localIdx] = imageKey[idx1];
            dinArrayKey[2][localIdx] = imageKey[idx2];
            dinArrayKey[3][localIdx] = imageKey[idx3];
        }
    }

    std::cout << "Graph initialized!!" << std::endl;
    accel.init();

    std::cout << "Start data transfer to AIEs!!" << std::endl;
    for (int i = 0; i < NUM_PARTS; i++) {
        accel.image[i].gm2aie_nb(dinArrayIP[i], BLOCK_SIZE_in_BytesIP);
        accel.key[i].gm2aie_nb(dinArrayKey[i], BLOCK_SIZE_in_BytesIP);
    }

    std::cout << "Graph execution started!!" << std::endl;
    accel.run(1);

    std::cout << "Start data transfer from AIEs!!" << std::endl;
    for (int i = 0; i < NUM_PARTS; i++) {
        accel.out[i].aie2gm(doutArrayOUT[i], BLOCK_SIZE_in_BytesOUT);
    }

    std::cout << "Waiting for output transfers!!" << std::endl;
    for (int i = 0; i < NUM_PARTS; i++) {
        accel.out[i].wait();
    }

    // Reassemble output image
    std::vector<unsigned char> output(width * height);

    for (int r = 0; r < PART_H; r++) {
        for (int c = 0; c < PART_W; c++) {
            int localIdx = r * PART_W + c;

            int idx0 = r * INPUT_IMG_W + c;
            int idx1 = r * INPUT_IMG_W + (c + PART_W);
            int idx2 = (r + PART_H) * INPUT_IMG_W + c;
            int idx3 = (r + PART_H) * INPUT_IMG_W + (c + PART_W);

            output[idx0] = doutArrayOUT[0][localIdx];
            output[idx1] = doutArrayOUT[1][localIdx];
            output[idx2] = doutArrayOUT[2][localIdx];
            output[idx3] = doutArrayOUT[3][localIdx];
        }
    }

    savePNG(filename_out, output, width, height);

    accel.end();

    for (int i = 0; i < NUM_PARTS; i++) {
        GMIO::free(dinArrayIP[i]);
        GMIO::free(dinArrayKey[i]);
        GMIO::free(doutArrayOUT[i]);
    }

    return 0;
}
#endif
