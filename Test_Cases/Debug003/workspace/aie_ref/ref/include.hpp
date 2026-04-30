#ifndef INCLUDE_HPP
#define INCLUDE_HPP

#include <cstdint>

static constexpr int M = 4;
static constexpr int K = 4;
static constexpr int N = 4;

static constexpr int A_SIZE = M * K;
static constexpr int B_SIZE = K * N;
static constexpr int C_SIZE = M * N;

static constexpr int A_BYTES = A_SIZE * sizeof(int32_t);
static constexpr int B_BYTES = B_SIZE * sizeof(int32_t);
static constexpr int C_BYTES = C_SIZE * sizeof(int32_t);

static constexpr int NFRAMES = 1;

#endif