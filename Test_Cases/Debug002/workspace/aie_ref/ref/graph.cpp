#include "graph.hpp"

#if defined(__X86SIM__) || defined(__AIESIM__)
#include <iostream>
#include <fstream>
#include <cstdint>
#endif

VectorAddGraph my_graph;

#if defined(__X86SIM__) || defined(__AIESIM__)

int main() {
    // Allocate GMIO-compatible buffers
    int32_t* input0 = (int32_t*) GMIO::malloc(VECTOR_BYTES);
    int32_t* input1 = (int32_t*) GMIO::malloc(VECTOR_BYTES);
    int32_t* output = (int32_t*) GMIO::malloc(VECTOR_BYTES);

    if (!input0 || !input1 || !output) {
        std::cerr << "Error: GMIO malloc failed\n";
        return 1;
    }

    // Open input file
    std::ifstream fin("data/PhaseIn_0.txt");
    if (!fin) {
        std::cerr << "Error: could not open data/PhaseIn_0.txt\n";
        return 1;
    }

    // Read two vectors
    for (int i = 0; i < VECTOR_SIZE; i++) fin >> input0[i];
    for (int i = 0; i < VECTOR_SIZE; i++) fin >> input1[i];

    // Initialize output
    for (int i = 0; i < VECTOR_SIZE; i++) output[i] = 0;

    // Start graph
    my_graph.init();

    // IMPORTANT: start graph first
    my_graph.run(1);

    // Start GMIO transfers
    my_graph.gmio_out.aie2gm_nb(output, VECTOR_BYTES);
    my_graph.gmio_in0.gm2aie_nb(input0, VECTOR_BYTES);
    my_graph.gmio_in1.gm2aie_nb(input1, VECTOR_BYTES);

    // Wait for completion
    my_graph.gmio_in0.wait();
    my_graph.gmio_in1.wait();
    my_graph.gmio_out.wait();

    my_graph.end();

    // Print results
    std::cout << "Vector addition output:\n";
    for (int i = 0; i < VECTOR_SIZE; i++) {
        std::cout << output[i] << "\n";
    }

    // Free GMIO buffers
    GMIO::free(input0);
    GMIO::free(input1);
    GMIO::free(output);

    return 0;
}

#endif