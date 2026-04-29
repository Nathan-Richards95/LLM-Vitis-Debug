#include "graph.h"

AbsGraph abs_graph;

#if defined(__AIESIM__) || defined(__X86SIM__)
int main() {
    abs_graph.init();
    abs_graph.run(1);
    abs_graph.end();

    return 0;
}
#endif