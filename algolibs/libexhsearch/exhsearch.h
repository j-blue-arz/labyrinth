#pragma once

#include "maze_graph.h"

namespace graph {

namespace algorithm {
class ExhaustiveSearch {
public:
    struct ShiftAction {
        Location shift_location{-1, -1};
        MazeGraph::RotationDegreeType rotation{0};
    };

    explicit ExhaustiveSearch(const MazeGraph & graph) : graph_(graph) {}

    std::pair<ShiftAction, Location> findBestMove(const Location & source, const Location & current_objective_location);
private:
    

    const MazeGraph & graph_;
};

}
}