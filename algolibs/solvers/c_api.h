#pragma once

// extern c library interface.
#ifdef WIN32
#define PUBLIC_API __declspec(dllexport)
#else
#define PUBLIC_API
#endif

#include "location.h"
#include "maze_graph.h"
#include "solvers.h"

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
    long int extent;
    // The graph is always quadratic.
    // Hence, the given number of nodes is expected to be equal to extent*extent + 1.
    // The nodes specify the row-wise layout of the maze. The last entry is the leftover.
    // Node ids are expected to be unique.
    unsigned long num_nodes;
    struct CNode* nodes;
};

struct CAction {
    struct CLocation shift_location;
    short rotation;
    struct CLocation move_location;
};

struct CPlayerLocations {
    struct CLocation* locations;
    unsigned long num_players;
};

struct CSearchStatus {
    unsigned long current_search_depth;
    bool search_terminated;
};

PUBLIC_API struct CAction find_action(struct CGraph* c_graph,
                                      struct CPlayerLocations* c_player_locations,
                                      unsigned int objective_id,
                                      struct CLocation* c_previous_shift_location);

PUBLIC_API void abort_search();

PUBLIC_API struct CSearchStatus get_status();
}

labyrinth::Location mapLocation(const struct CLocation& location) noexcept {
    return labyrinth::Location{location.row, location.column};
}

labyrinth::Location mapLocationAtIndex(const struct CPlayerLocations& player_locations, size_t index) noexcept {
    if (index >= player_locations.num_players) {
        index = player_locations.num_players - 1;
    }
    return mapLocation(player_locations.locations[index]);
}

labyrinth::RotationDegreeType mapRotation(short rotation) noexcept {
    return static_cast<labyrinth::RotationDegreeType>((rotation / 90 + 4) % 4);
}

labyrinth::Node mapNode(const struct CNode& node) noexcept {
    const auto out_paths = static_cast<labyrinth::OutPaths>(node.out_paths);
    return labyrinth::Node{node.node_id, out_paths, mapRotation(node.rotation)};
}

labyrinth::MazeGraph mapGraph(struct CGraph graph) {
    std::vector<labyrinth::Node> input_nodes;
    input_nodes.reserve(graph.num_nodes);
    for (unsigned long i = 0; i < graph.num_nodes; ++i) {
        input_nodes.push_back(mapNode(graph.nodes[i]));
    }
    const auto extent = static_cast<labyrinth::MazeGraph::ExtentType>(graph.extent);
    labyrinth::MazeGraph maze_graph{input_nodes};
    for (auto pos = 1; pos < extent; pos += 2) {
        maze_graph.addShiftLocation(labyrinth::Location{0, pos});
        maze_graph.addShiftLocation(labyrinth::Location{graph.extent - 1, pos});
        maze_graph.addShiftLocation(labyrinth::Location{pos, 0});
        maze_graph.addShiftLocation(labyrinth::Location{pos, graph.extent - 1});
    }
    return maze_graph;
}

struct CLocation locationToCLocation(const labyrinth::Location& location) noexcept {
    struct CLocation c_location = {location.getRow(), location.getColumn()};
    return c_location;
}

short rotationToCRotation(labyrinth::RotationDegreeType rotation) noexcept {
    return static_cast<labyrinth::RotationDegreeIntegerType>(rotation) * 90;
}

struct CAction actionToCAction(const labyrinth::solvers::PlayerAction& action) {
    struct CAction c_action = {locationToCLocation(action.shift.location),
                               rotationToCRotation(action.shift.rotation),
                               locationToCLocation(action.move_location)};
    return c_action;
}

struct CAction errorAction() {
    struct CLocation error_location = {-1, -1};
    struct CAction c_action = {error_location, 0, error_location};
    return c_action;
}
