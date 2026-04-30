#include <adf.h>
#include <iostream>
#include <fstream>
#include <cstdint>

#include "graph.hpp"
#include "include.hpp"

using namespace adf;

int main() {
    int32_t input0[VECTOR_SIZE];
    int32_t input1[VECTOR_SIZE];
    int32_t output[VECTOR_SIZE];

    std::ifstream fin("input.txt");

    if (!fin) {
        std::cerr << "Error: could not open input.txt\n";
        return 1;
    }

    for (int i = 0; i < VECTOR_SIZE; i++) {
        fin >> input0[i];
    }

    for (int i = 0; i < VECTOR_SIZE; i++) {
        fin >> input1[i];
    }

    for (int i = 0; i < VECTOR_SIZE; i++) {
        output[i] = 0;
    }

    my_graph.init();

    my_graph.gmio_in0.gm2aie_nb(input0, VECTOR_BYTES);
    my_graph.gmio_in1.gm2aie_nb(input1, VECTOR_BYTES);
    my_graph.gmio_out.aie2gm_nb(output, VECTOR_BYTES);

    my_graph.run(1);

    my_graph.gmio_in0.wait();
    my_graph.gmio_in1.wait();
    my_graph.gmio_out.wait();

    my_graph.end();

    std::cout << "Vector addition output:\n";
    for (int i = 0; i < VECTOR_SIZE; i++) {
        std::cout << output[i] << "\n";
    }

    return 0;
}