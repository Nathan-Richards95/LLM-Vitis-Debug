#include <adf.h>
#include "library/bitonic_sort_graph.hpp"

// Adjust include paths in your build so this resolves from:
// <Vitis_Libraries>/dsp/L2/include/aie/bitonic_sort_graph.hpp

using namespace adf;

// -----------------------------
// User configuration
// -----------------------------
static constexpr int TP_DIM        = 1024;
static constexpr int TP_NUM_FRAMES = 1;
static constexpr int TP_ASCENDING  = 1;
static constexpr int TP_CASC_LEN   = 1;
static constexpr int TP_SSR        = 2;

using TT_DATA = int32;

// -----------------------------
// Graph
// -----------------------------
class sort_graph : public graph {
public:
    // Two inputs because TP_SSR = 2
    input_gmio gmioIn[TP_SSR];
    output_gmio gmioOut;

    xf::dsp::aie::bitonic_sort::bitonic_sort_graph<
        TT_DATA,
        TP_DIM,
        TP_NUM_FRAMES,
        TP_ASCENDING,
        TP_CASC_LEN,
        TP_SSR
    > sorter;

    sort_graph() {
        // Name these carefully: the host code uses these exact names.
        gmioIn[0] = input_gmio::create("gmioIn[0]", 64, 1000);
        gmioIn[1] = input_gmio::create("gmioIn[1]", 64, 1000);
        gmioOut   = output_gmio::create("gmioOut[0]", 64, 1000);

        connect<>(gmioIn[0].out[0], sorter.in[0]);
        connect<>(gmioIn[1].out[0], sorter.in[1]);
        connect<>(sorter.out[0], gmioOut.in[0]);
    }
};

// Global graph instance name must match the host-side xrt::graph name.
sort_graph gr;