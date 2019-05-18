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
        // expected to be of size extent*extent + 1,
        // and specify the row-wise nodes of the maze. The last entry is the leftover.
        // node ids are expected to be unique.
        CNode * nodes;
        CLocation last_shift_location;
    };

    struct CAction {
        CLocation shift_location;
        short rotation;
        CLocation move_location;
    };

    __declspec(dllexport) struct CAction find_action(struct CGraph maze, struct CLocation player_location, unsigned int objective_id);
}
