#ifndef GRAPH_H
#define GRAPH_H

#include <adf.h>
#include "FirSingleStream.h"

using namespace adf;

class AbsGraph : public graph {
public:
    input_plio in;
    output_plio out;

    kernel abs_kernel;

    AbsGraph() {
        in = input_plio::create("DataIn", plio_32_bits, "input.txt");
        out = output_plio::create("DataOut", plio_32_bits, "output.txt");

        abs_kernel = kernel::create(abs_signal);

        source(abs_kernel) = "broken.cpp";

        connect(in.out[0], abs_kernel.in[0]);
        connect(abs_kernel.out[0], out.in[0]);

        runtime<ratio>(abs_kernel) = 0.8;
    }
};

#endif