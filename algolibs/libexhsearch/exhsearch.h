#pragma once

#include "maze_graph.h"
#include "graph_algorithms.h"

#include <queue>

namespace labyrinth {

namespace exhsearch {

    struct ShiftAction {
        Location location{0, 0};
        MazeGraph::RotationDegreeType rotation{0};
    };

    struct PlayerAction {
        ShiftAction shift;
        Location move_location;
    };

    std::vector<PlayerAction> findBestActions(
        const MazeGraph & graph,
        const Location & source,
        MazeGraph::NodeId objective_id,
        const Location & previous_shift_location = Location{-1, -1});

} // namespace algorithm
} // namespace graph
