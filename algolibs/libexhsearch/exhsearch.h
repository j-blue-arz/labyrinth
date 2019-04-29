#pragma once

#include "maze_graph.h"

namespace graph {

namespace algorithm {
class ExhaustiveSearch {
public:
    struct ShiftAction {
        Location location{0, 0};
        MazeGraph::RotationDegreeType rotation{0};
    };

    struct PlayerAction {
        ShiftAction shift;
        Location move_location;
    };

    explicit ExhaustiveSearch(const MazeGraph & graph) : graph_(graph) {}

    std::vector<PlayerAction> findBestActions(const Location & source, MazeGraph::NodeId objective_id);
private:
    

    const MazeGraph & graph_;
};

}
}