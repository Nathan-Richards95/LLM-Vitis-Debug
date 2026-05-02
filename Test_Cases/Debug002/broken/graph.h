#pragma once

#include <adf.h>

using namespace adf;

// Kernel declaration
void mm3_kernel0_L3_B0_A0_C3(
    input_window_int8* __restrict matA,
    output_stream_acc48* __restrict matC
);

// Graph definition
class MM3Graph : public adf::graph {
private:
    adf::kernel k;

public:
    adf::input_plio inA;
    adf::output_plio outC;

    MM3Graph() {
        // Create kernel
        k = adf::kernel::create(mm3_kernel0_L3_B0_A0_C3);

        // Input and output PLIOs
        inA = adf::input_plio::create(
            "inA",
            adf::plio_32_bits,
            "input.txt"
        );

        outC = adf::output_plio::create(
            "outC",
            adf::plio_32_bits,
            "output.txt"
        );

        // Connect input → kernel
        adf::connect<> net_in(inA.out[0], k.in[0]);

        // Connect kernel → output
        adf::connect<> net_out(k.out[0], outC.in[0]);

        // Kernel source
        adf::source(k) = "broken.cpp";

        // Required headers for compile
        adf::headers(k) = {
            "para_L3.h",
            "parameter_L3_B0_A0_C3.h"
        };

        // Runtime estimate
        adf::runtime<ratio>(k) = 0.9;
    }
};

// Global graph object
extern MM3Graph G;