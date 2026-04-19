#include <algorithm>
#include <cstdint>
#include <cstring>
#include <exception>
#include <iostream>
#include <string>
#include <vector>

#include "xrt/xrt_aie.h"
#include "xrt/xrt_device.h"
#include "xrt/xrt_graph.h"

// -----------------------------
// User configuration
// -----------------------------
static constexpr int TP_DIM        = 1024;
static constexpr int TP_SSR        = 2;
static constexpr int LOCAL_DIM     = TP_DIM / TP_SSR;
using TT_DATA = std::int32_t;

// -----------------------------
// Utility helpers
// -----------------------------
static void print_vector(const std::vector<TT_DATA>& v, const std::string& label, int count = 16) {
    std::cout << label << " (first " << std::min<int>(count, v.size()) << "): ";
    for (int i = 0; i < std::min<int>(count, v.size()); ++i) {
        std::cout << v[i] << " ";
    }
    std::cout << "\n";
}

static bool is_sorted_ascending(const std::vector<TT_DATA>& v) {
    for (size_t i = 1; i < v.size(); ++i) {
        if (v[i - 1] > v[i]) {
            return false;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <xclbin>\n";
        return 1;
    }

    const std::string xclbin_path = argv[1];

    const size_t in_bytes_per_port = LOCAL_DIM * sizeof(TT_DATA);
    const size_t out_bytes         = TP_DIM * sizeof(TT_DATA);

    try {
        // -----------------------------------------
        // Open device and load xclbin
        // -----------------------------------------
        auto device = xrt::device(0);
        auto uuid   = device.load_xclbin(xclbin_path);

        // Graph instance name must match the global graph object in graph.cpp
        auto ghdl = xrt::graph(device, uuid, "gr");

        // -----------------------------------------
        // Allocate GMIO buffers
        // Note: only non-cacheable BOs are supported for GMIO
        // -----------------------------------------
        auto in_bo0  = xrt::aie::bo(device, in_bytes_per_port, xrt::bo::flags::normal, 0);
        auto in_bo1  = xrt::aie::bo(device, in_bytes_per_port, xrt::bo::flags::normal, 0);
        auto out_bo  = xrt::aie::bo(device, out_bytes,         xrt::bo::flags::normal, 0);

        auto* in0_ptr = in_bo0.map<TT_DATA*>();
        auto* in1_ptr = in_bo1.map<TT_DATA*>();
        auto* out_ptr = out_bo.map<TT_DATA*>();

        // -----------------------------------------
        // Prepare test input
        //
        // Since TP_SSR=2, the graph has two public inputs.
        // For an easy sanity check, we give it two halves that
        // together form a shuffled 0..1023 sequence.
        //
        // The graph itself is a full bitonic-sort graph, not just
        // a raw merge stage, so unsorted data is okay here.
        // -----------------------------------------
        std::vector<TT_DATA> host_in0(LOCAL_DIM);
        std::vector<TT_DATA> host_in1(LOCAL_DIM);

        for (int i = 0; i < LOCAL_DIM; ++i) {
            // Fill with a deliberately mixed pattern
            host_in0[i] = (LOCAL_DIM - 1 - i) * 2;
            host_in1[i] = (LOCAL_DIM - 1 - i) * 2 + 1;
        }

        std::memcpy(in0_ptr, host_in0.data(), in_bytes_per_port);
        std::memcpy(in1_ptr, host_in1.data(), in_bytes_per_port);
        std::memset(out_ptr, 0, out_bytes);

        print_vector(host_in0, "Input stream 0");
        print_vector(host_in1, "Input stream 1");

        // -----------------------------------------
        // Start graph
        // One run because TP_NUM_FRAMES = 1
        // -----------------------------------------
        ghdl.run(1);

        // -----------------------------------------
        // Kick off output read first, then inputs
        // This follows the GMIO async style used in AMD examples
        // -----------------------------------------
        auto out_run = out_bo.async("gr.gmioOut[0]",
                                    XCL_BO_SYNC_BO_AIE_TO_GMIO,
                                    out_bytes,
                                    0);

        in_bo0.async("gr.gmioIn[0]",
                     XCL_BO_SYNC_BO_GMIO_TO_AIE,
                     in_bytes_per_port,
                     0);

        in_bo1.async("gr.gmioIn[1]",
                     XCL_BO_SYNC_BO_GMIO_TO_AIE,
                     in_bytes_per_port,
                     0);

        // Wait for graph and GMIO completion
        ghdl.wait();
        out_run.wait();

        // -----------------------------------------
        // Copy output back into STL vector
        // -----------------------------------------
        std::vector<TT_DATA> result(TP_DIM);
        std::memcpy(result.data(), out_ptr, out_bytes);

        print_vector(result, "Output");

        if (!is_sorted_ascending(result)) {
            std::cerr << "ERROR: output is not sorted in ascending order.\n";
            return 2;
        }

        std::cout << "SUCCESS: output is sorted.\n";

        ghdl.end();
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n";
        return 3;
    }
}