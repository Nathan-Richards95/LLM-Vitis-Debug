#include "graph.h"

simple_graph g;

#ifdef __AIESIM__
int main() {
    g.init();
    g.run(1);
    g.end();
    return 0;
}
#endif