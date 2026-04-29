#ifndef GRAPH_H
#define GRAPH_H

#include <adf.h>
#include "FirSingleStream.h"

using namespace adf;

class ClipGraph : public graph {
public:
    input_plio in;
    output_plio out;

    kernel clip_kernel;

    ClipGraph() {
        in = input_plio::create("DataIn", plio_32_bits, "input.txt");
        out = output_plio::create("DataOut", plio_32_bits, "output.txt");

        clip_kernel = kernel::create(clip_signal);

        source(clip_kernel) = "broken.cpp";

        connect(in.out[0], clip_kernel.in[0]);
        connect(clip_kernel.out[0], out.in[0]);

        runtime<ratio>(clip_kernel) = 0.8;
    }
};

#endif