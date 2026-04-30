#include "graph.hpp"

#if defined(__X86SIM__) || defined(__AIESIM__)
#include <iostream>
#include <fstream>
#include <cstdint>
#endif

GemmGraph my_graph;

#if defined(__X86SIM__) || defined(__AIESIM__)

int main() {
    int32_t A[A_SIZE];
    int32_t B[B_SIZE];
    int32_t C[C_SIZE] = {0};

    std::ifstream fin("input.txt");

    if (!fin) {
        std::cerr << "Error: could not open input.txt\n";
        return 1;
    }

    for (int i = 0; i < A_SIZE; i++) {
        fin >> A[i];
    }

    for (int i = 0; i < B_SIZE; i++) {
        fin >> B[i];
    }

    my_graph.init();

    my_graph.gmio_A.gm2aie_nb(A, A_BYTES);
    my_graph.gmio_B.gm2aie_nb(B, B_BYTES);
    my_graph.gmio_C.aie2gm_nb(C, C_BYTES);

    my_graph.run(NFRAMES);

    my_graph.gmio_A.wait();
    my_graph.gmio_B.wait();
    my_graph.gmio_C.wait();

    my_graph.end();

    std::cout << "GEMM output C = A * B:\n";

    for (int row = 0; row < M; row++) {
        for (int col = 0; col < N; col++) {
            std::cout << C[row * N + col] << " ";
        }
        std::cout << "\n";
    }

    return 0;
}

#endif