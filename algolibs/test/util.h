#pragma once
#include "libexhsearch/location.h"
#include "libexhsearch/maze_graph.h"

#include <iterator>
#include <set>
#include <sstream>

#include "gtest/gtest.h"

namespace labyrinth {
namespace testutils {

std::string locationsToString(std::set<labyrinth::Location> locations);

::testing::AssertionResult hasNeighbors(const labyrinth::MazeGraph& graph,
                                        const labyrinth::Location& source,
                                        std::set<labyrinth::Location> expected);

::testing::AssertionResult assertNumNeighbors(const labyrinth::MazeGraph& g,
                                              const labyrinth::Location& source,
                                              size_t expected);

template <class It>
labyrinth::OutPaths getBitmask(It first, It last) {
    labyrinth::OutPathsIntegerType result{0};
    for (auto it = first; it != last; ++it) {
        result |= static_cast<labyrinth::OutPathsIntegerType>(*it);
    }
    return static_cast<labyrinth::OutPaths>(result);
}

labyrinth::OutPaths getBitmask(std::string out_paths_string);

labyrinth::OutPaths getBitmask(const std::vector<labyrinth::OutPaths>& out_paths);

} // namespace testutils
} // namespace labyrinth