#pragma once

#include <adf.h>
#include <vector>
#include "FirSingleStream.h"

using namespace adf;

#define NUM_SAMPLES 512
#define NFRAMES 4

// Original taps from the tutorial
static std::vector<cint16> taps = {
    {  -82,  -253}, {    0,  -204}, {   11,   -35}, { -198,   273},
    { -642,   467}, {-1026,   333}, { -927,     0}, { -226,   -73},
    {  643,   467}, { 984,  1355}, {  550,  1691}, {    0,   647},
    {  538, -1656}, {2860, -3936}, { 6313, -4587}, { 9113, -2961},
    { 9582,     0}, {7421,  2411}, { 3936,  2860}, { 1023,  1409},
    { -200,  -615}, {   0, -1778}, {  517, -1592}, {  467,  -643},
    { -192,   140}, {-882,   287}, {-1079,     0}, { -755,  -245},
    { -273,  -198}, {  22,    30}, {   63,   194}, {    0,   266}
};

// Reverse for AIE kernel construction, same as tutorial
static std::vector<cint16> taps_aie(taps.rbegin(), taps.rend());

// SHIFT=0 is useful for debugging impulse response
static constexpr int SHIFT = 0;
// static constexpr int SHIFT = 15;

class FIRGraphPLIO : public adf::graph {
private:
    adf::kernel k;

public:
    adf::input_plio  in;
    adf::output_plio out;

    FIRGraphPLIO() {
        k = adf::kernel::create_object<
            SingleStream::FIR_SingleStream<NUM_SAMPLES, SHIFT>
        >(taps_aie);

        // Update file paths if your data folder lives somewhere else
        in  = adf::input_plio::create(
            "fir_in",
            adf::plio_64_bits,
            "data/PhaseIn_0.txt"
        );

        out = adf::output_plio::create(
            "fir_out",
            adf::plio_64_bits,
            "data/Output_0.txt"
        );

        adf::connect<>(in.out[0], k.in[0]);
        adf::connect<>(k.out[0], out.in[0]);

        adf::source(k)  = "broken.cpp";
        adf::headers(k) = { "FirSingleStream.h" };
        adf::runtime<ratio>(k) = 0.9;
    }
};

extern FIRGraphPLIO G;