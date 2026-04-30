#include "gemm.hpp"

void gemm(
    input_window<int32_t>* inA,
    input_window<int32_t>* inB,
    output_window<int32_t>* outC
) {
    int32_t A[A_SIZE];
    int32_t B[B_SIZE];

    for (int i = 0; i < A_SIZE; i++) {
        A[i] = window_readincr(inA);
    }

    for (int i = 0; i < B_SIZE; i++) {
        B[i] = window_readincr(inB);
    }

    for (int row = 0; row < M; row++) {
        for (int col = 0; col < N; col++) {
            int32_t sum = 0;

            for (int kk = 0; kk < K; kk++) {
                sum += A[row * K + kk] * B[kk * N + col];
            }

            window_writeincr(outC, sum);
        }
    }
}