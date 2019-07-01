#pragma once

#include "maze_graph.h"
#include "location.h"

#include <utility>
#include <vector>


namespace labyrinth {

namespace reachable {

struct ReachableNode {
    explicit ReachableNode(size_t parent_source_index, NodeId reached_id) noexcept :
        parent_source_index{parent_source_index}, reached_id{reached_id} {}
    size_t parent_source_index;
    NodeId reached_id;
};

bool isReachable(const MazeGraph & graph, const Location & source, const Location & target);

std::vector<Location> reachableLocations(const MazeGraph & graph, const Location & source);

std::vector<ReachableNode> multiSourceReachableLocations(const MazeGraph & graph, const std::vector<Location> & sources);

}

}
