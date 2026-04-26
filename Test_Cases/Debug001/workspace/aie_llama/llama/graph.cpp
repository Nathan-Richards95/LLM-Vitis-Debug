#include "graph.h"

FIRGraphPLIO G;

#if defined(__X86SIM__) || defined(__AIESIM__)
int main() {
    std::cout << "SIM START\n";
    G.init();
    G.run(NFRAMES);
    G.end();
    std::cout << "SIM END\n";
    return 0;
}
#endif