#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <adf.h>
#include "include.hpp"
#include "gemm.hpp"

using namespace adf;

class GemmGraph : public graph {
public:
    kernel k;

    input_gmio gmio_A;
    input_gmio gmio_B;
    output_gmio gmio_C;

    GemmGraph() {
        gmio_A = input_gmio::create("gmio_A", 64, 1000);
        gmio_B = input_gmio::create("gmio_B", 64, 1000);
        gmio_C = output_gmio::create("gmio_C", 64, 1000);

        k = kernel::create(gemm);

        source(k) = "gemm.cpp";
        runtime<ratio>(k) = 0.8;

        connect<window<A_BYTES>>(gmio_A.out[0], k.in[0]);
        connect<window<B_BYTES>>(gmio_B.out[0], k.in[1]);
        connect<window<C_BYTES>>(k.out[0], gmio_C.in[0]);
    }
};

extern GemmGraph my_graph;

#endif