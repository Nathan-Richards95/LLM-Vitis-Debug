#pragma once
#include <adf.h>

using namespace adf;

// forward declaration of kernel
void bitonic_merge_main(
    input_stream<int>* in0,
    input_stream<int>* in1,
    output_stream<int>* out);

class simple_graph : public graph {
public:
    input_plio in0;
    input_plio in1;
    output_plio out;

    kernel k;

    simple_graph() {
        // create kernel
        k = kernel::create(bitonic_merge_main);

        // connect streams
        in0 = input_plio::create("in0", plio_32_bits, "data/input0.txt");
        in1 = input_plio::create("in1", plio_32_bits, "data/input1.txt");
        out = output_plio::create("out", plio_32_bits, "data/output.txt");

        connect<>(in0.out[0], k.in[0]);
        connect<>(in1.out[0], k.in[1]);
        connect<>(k.out[0], out.in[0]);

        // kernel source
        source(k) = "broken.cc";

        // runtime hint
        runtime<ratio>(k) = 0.9;
    }
};