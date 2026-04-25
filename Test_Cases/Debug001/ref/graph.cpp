#include "graph.h"

FIRGraphPLIO G;

#if defined(__X86SIM__) || defined(__AIESIM__)
int main() {
    G.init();
    G.run(NFRAMES);
    G.end();
    return 0;
}
#endif