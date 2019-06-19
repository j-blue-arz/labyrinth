// extern c library interface. no namespace, no class, no inline

#include "location.h"

extern "C" {
    struct CLocation {
        short row;
        short column;
    };

    struct CNode {
        unsigned int node_id;
        unsigned char out_paths; // bitmask. 1, 2, 4, 8 for N, E, S, W, respectively
        short rotation;
    };

    struct CGraph {
        unsigned long long extent;
        // The graph is always quadratic.
        // Hence, the given number of nodes is expected to be equal to extent*extent + 1.
        // The nodes specify the row-wise layout of the maze. The last entry is the leftover.
        // Node ids are expected to be unique.
        unsigned long long num_nodes;
        struct CNode * nodes;
    };

    struct CAction {
        struct CLocation shift_location;
        short rotation;
        struct CLocation move_location;
    };

    __declspec(dllexport) struct CAction find_action(struct CGraph * c_graph, struct CLocation * c_player_location, unsigned int objective_id,
                                                     struct CLocation * c_previous_shift_location);
}
