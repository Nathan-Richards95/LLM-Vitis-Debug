#include "graph.h"

ClipGraph clip_graph;

#if defined(__AIESIM__) || defined(__X86SIM__)
int main() {
    clip_graph.init();
    clip_graph.run(1);
    clip_graph.end();

    return 0;
}
#endif