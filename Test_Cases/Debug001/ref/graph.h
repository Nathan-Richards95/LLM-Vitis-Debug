#pragma once

#include <adf.h>
#include <vector>
#include "../shared/FirSingleStream.h"

using namespace adf;

#define NUM_SAMPLES 512
#define NFRAMES 4

std::vector<cint16> taps = {
    {  -82,  -253}, {    0,  -204}, {   11,   -35}, { -198,   273},
    { -642,   467}, {-1026,   333}, { -927,     0}, { -226,   -73},
    {  643,   467}, { 984,  1355}, {  550,  1691}, {    0,   647},
    {  538, -1656}, {2860, -3936}, { 6313, -4587}, { 9113, -2961},
    { 9582,     0}, {7421,  2411}, { 3936,  2860}, { 1023,  1409},
    { -200,  -615}, {   0, -1778}, {  517, -1592}, {  467,  -643},
    { -192,   140}, {-882,   287}, {-1079,     0}, { -755,  -245},
    { -273,  -198}, {  22,    30}, {   63,   194}, {    0,   266}
};

std::vector<cint16> taps_aie(taps.rbegin(), taps.rend());

const int SHIFT = 0;

class FIRGraphGMIO : public adf::graph {
private:
    adf::kernel k;

public:
    adf::input_gmio gmioIn;
    adf::output_gmio gmioOut;

    FIRGraphGMIO() {
        k = adf::kernel::create_object<SingleStream::FIR_SingleStream<NUM_SAMPLES, SHIFT>>(taps_aie);

        gmioIn  = adf::input_gmio::create("gmioIn", 64, 1000);
        gmioOut = adf::output_gmio::create("gmioOut", 64, 1000);

        connect<>(gmioIn.out[0], k.in[0]);
        connect<>(k.out[0], gmioOut.in[0]);

        source(k) = "ref.cpp";
        headers(k) = {"../shared/FirSingleStream.h"};
        runtime<ratio>(k) = 0.9;
    }
};

extern FIRGraphGMIO G;