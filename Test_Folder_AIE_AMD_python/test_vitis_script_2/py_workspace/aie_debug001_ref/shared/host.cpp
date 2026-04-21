#include <adf/adf_api/XRTConfig.h>
#include <xrt/xrt_device.h>

#include <cstdint>
#include <cstring>
#include <exception>
#include <iostream>
#include <string>
#include <vector>

#include "graph.h"

static void generate_impulse_input(cint16* in, int nsamples) {
    for (int i = 0; i < nsamples; ++i) {
        in[i].real = 0;
        in[i].imag = 0;
    }

    // Simple impulse for debugging the FIR response.
    if (nsamples > 0) {
        in[0].real = 1;
        in[0].imag = 0;
    }
}

static void print_first_outputs(const cint16* out, int count) {
    for (int i = 0; i < count; ++i) {
        std::cout << "[" << i << "] = (" << out[i].real << ", " << out[i].imag << ")\n";
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <design.xclbin>\n";
        return 1;
    }

    const std::string xclbin_path = argv[1];

    // The tutorial constants are NUM_SAMPLES=512 and NFRAMES=4.
    constexpr int TOTAL_SAMPLES = NUM_SAMPLES * NFRAMES;
    constexpr size_t BUFFER_BYTES = TOTAL_SAMPLES * sizeof(cint16);

    try {
        // Open device and load xclbin
        xrt::device device(0);
        auto uuid = device.load_xclbin(xclbin_path);

        // Register XRT with the global ADF graph object
        adf::registerXRT(device, uuid);

        // For GMIO on Linux, allocate with GMIO::malloc
        auto* in_buf  = reinterpret_cast<cint16*>(adf::GMIO::malloc(BUFFER_BYTES));
        auto* out_buf = reinterpret_cast<cint16*>(adf::GMIO::malloc(BUFFER_BYTES));

        if (!in_buf || !out_buf) {
            std::cerr << "ERROR: GMIO::malloc failed.\n";
            return 2;
        }

        generate_impulse_input(in_buf, TOTAL_SAMPLES);
        std::memset(out_buf, 0, BUFFER_BYTES);

        // Run the graph for NFRAMES, same as the tutorial's file-based main()
        G.run(NFRAMES);

        // Start output transfer first, then input transfer
        G.gmioOut.aie2gm_nb(out_buf, BUFFER_BYTES);
        G.gmioIn.gm2aie_nb(in_buf, BUFFER_BYTES);

        // Wait for completion
        G.gmioIn.wait();
        G.gmioOut.wait();
        G.wait();

        std::cout << "First 32 output samples:\n";
        print_first_outputs(out_buf, 32);

        G.end();

        adf::GMIO::free(in_buf);
        adf::GMIO::free(out_buf);

        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n";
        return 3;
    }
}