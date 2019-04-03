#pragma once

#include "maze_graph.h"
#include "location.h"

namespace graph {

namespace algorithm {

bool isReachable(const MazeGraph & graph, const Location & source, const Location & target);

std::vector<Location> reachableLocations(const MazeGraph & graph, const Location & source);

}

}