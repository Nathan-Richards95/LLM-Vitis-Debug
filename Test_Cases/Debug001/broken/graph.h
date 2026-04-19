#pragma once

#include <adf.h>
#include <vector>
#include "../shared/FirSingleStream.h"

// Keep the same values as the 2024.1 tutorial unless you want to change them.
#define NUM_SAMPLES 512
#define NFRAMES 4

using namespace adf;

// Same taps as the tutorial graph, then reversed for AIE use.
static constexpr int kShift = 0;

static const cint16 taps_aie[32] = {
    {   0,   266}, {  63,   194}, {  22,    30}, { -273,  -198},
    { -755,  -245}, {-1079,     0}, { -882,   287}, { -192,   140},
    {  467,  -643}, { 517, -1592}, {   0, -1778}, { -200,  -615},
    { 1023,  1409}, {3936,  2860}, {7421,  2411}, { 9582,     0},
    { 9113, -2961}, {6313, -4587}, {2860, -3936}, {  538, -1656},
    {    0,   647}, { 550,  1691}, { 984,  1355}, {  643,   467},
    { -226,   -73}, { -927,     0}, {-1026,   333}, { -642,   467},
    { -198,  	273}, {	11,  	-35}, {	0, 	-204}, {	-82, 	-253}
};

static std::vector<cint16> taps_aie(taps.rbegin(), taps.rend());

// The tutorial uses SHIFT=0 for impulse-debug style viewing and comments
// that SHIFT=15 is the realistic scaled case.
static constexpr int SHIFT = 0;
// static constexpr int SHIFT = 15;

class FIRGraphGMIO : public adf::graph {
private:
    adf::kernel k;

public:
    adf::input_gmio  gmioIn;
    adf::output_gmio gmioOut;

    FIRGraphGMIO() {
        k = adf::kernel::create_object<SingleStream::FIR_SingleStream<32, kShift>>(taps_aie);

        gmioIn  = adf::input_gmio::create("gmioIn", 64, 1000);
        gmioOut = adf::output_gmio::create("gmioOut", 64, 1000);

        adf::connect<>(gmioIn.out[0],  k.in[0]);
        adf::connect<>(k.out[0],       gmioOut.in[0]);

        adf::source(k)  = "broken.cc";
        adf::headers(k) = { "../shared/FirSingleStream.h" };
        adf::runtime<ratio>(k) = 0.9;
    }
};

extern FIRGraphGMIO G;