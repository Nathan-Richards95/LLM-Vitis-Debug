#pragma once

#include <adf.h>

using namespace adf;

// Kernel declaration matching broken.cc
void mm3_kernel0_L3_B0_A0_C3(
    input_window_int8* __restrict matA,
    output_stream_acc48* __restrict matC
);

class MM3Graph : public adf::graph {
public:
    adf::input_gmio  inA;
    adf::output_gmio outC;

    adf::kernel k;

    MM3Graph() {
        k = adf::kernel::create(mm3_kernel0_L3_B0_A0_C3);

        inA  = adf::input_gmio::create("inA", 64, 1000);
        outC = adf::output_gmio::create("outC", 64, 1000);

        // IMPORTANT:
        // Replace WINDOW_BYTES with the real input window size in BYTES.
        adf::connect< adf::window<WINDOW_BYTES> >(inA.out[0], k.in[0]);
        adf::connect<>(k.out[0], outC.in[0]);

        adf::source(k) = "broken.cc";
        adf::headers(k) = {
            "../shared/para_L3.h",
            "../shared/parameter_L3_B0_A0_C3.h"
        };

        adf::runtime<ratio>(k) = 0.9;
    }
};

extern MM3Graph G;