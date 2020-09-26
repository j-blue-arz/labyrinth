#pragma once

#include "location.h"
#include "maze_graph.h"

#include <utility>
#include <vector>

namespace labyrinth {

namespace reachable {

struct ReachableNode {
    explicit ReachableNode(size_t parent_source_index, Location reached_location) noexcept
        : parent_source_index{parent_source_index}, reached_location{reached_location} {}
    size_t parent_source_index;
    Location reached_location;
};

bool isReachable(const MazeGraph& graph, const Location& source, const Location& target);

std::vector<Location> reachableLocations(const MazeGraph& graph, const Location& source);

std::vector<ReachableNode> multiSourceReachableLocations(const MazeGraph& graph, const std::vector<Location>& sources);

} // namespace reachable

} // namespace labyrinth
