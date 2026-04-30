#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <adf.h>
#include "include.hpp"
#include "vector_add.hpp"

using namespace adf;

class VectorAddGraph : public graph {
public:
    kernel k;

    input_gmio gmio_in0;
    input_gmio gmio_in1;
    output_gmio gmio_out;

    VectorAddGraph() {
        gmio_in0 = input_gmio::create("gmio_in0", 64, 1000);
        gmio_in1 = input_gmio::create("gmio_in1", 64, 1000);
        gmio_out = output_gmio::create("gmio_out", 64, 1000);

        k = kernel::create(vector_add);

        source(k) = "vector_add.cpp";
        runtime<ratio>(k) = 0.8;

        connect<window<VECTOR_BYTES>>(gmio_in0.out[0], k.in[0]);
        connect<window<VECTOR_BYTES>>(gmio_in1.out[0], k.in[1]);
        connect<window<VECTOR_BYTES>>(k.out[0], gmio_out.in[0]);
    }
};

extern VectorAddGraph my_graph;

#endif