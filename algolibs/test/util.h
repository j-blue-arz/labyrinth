#pragma once
#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"

#include <sstream>
#include <set>

#include "gtest/gtest.h"

std::string locationsToString(std::set<labyrinth::Location> locations) {
    std::stringstream stream;
    for (const auto & location : locations) {
        stream << location << ", ";
    }
    return stream.str();
}

::testing::AssertionResult hasNeighbors(const labyrinth::MazeGraph & graph, const labyrinth::Location & source, std::initializer_list<labyrinth::Location> targets) {
    std::set<labyrinth::Location> expected{targets};
    auto neighbors = graph.neighbors(source);
    std::set<labyrinth::Location> actual{neighbors.begin(), neighbors.end()};
    if (actual == expected) {
        return ::testing::AssertionSuccess();
    }
    return ::testing::AssertionFailure() << "Expected neighbors: " << locationsToString(expected) << ", actual: " << locationsToString(actual);
}

::testing::AssertionResult assertNumNeighbors(const labyrinth::MazeGraph & g, const labyrinth::Location & source, size_t expected) {
    size_t actual{0};
    auto neighbors = g.neighbors(source);
    for (auto neighbor : neighbors) {
        actual++;
    }
    if (actual == expected) {
        return ::testing::AssertionSuccess();
    }
    return ::testing::AssertionFailure() << "Expected neighbors: " << expected << ", actual: " << actual;
}

size_t numNeighbors(const labyrinth::MazeGraph & g, const labyrinth::Location & source) {
    auto neighbors = g.neighbors(source);
    std::set<labyrinth::Location> actual{neighbors.begin(), neighbors.end()};
    return actual.size();
}

size_t countEdges(const labyrinth::MazeGraph & g) {
    size_t count = 0;
    for (auto row = 0; row < g.getExtent(); row++) {
        for (auto column = 0; column < g.getExtent(); column++) {
            count += numNeighbors(g, labyrinth::Location{row, column});
        }
    }
    return count / 2;
}

template<class It>
labyrinth::OutPaths getBitmask(It first, It last) {
    labyrinth::OutPathsIntegerType result{0};
    for (auto it = first; it != last; ++it) {
        result |= static_cast<labyrinth::OutPathsIntegerType>(*it);
    }
    return static_cast<labyrinth::OutPaths>(result);
}

labyrinth::OutPaths getBitmask(std::string out_paths_string) {
    std::vector<labyrinth::OutPaths> out_path_vector;
    if (out_paths_string.find('N') != std::string::npos) {
        out_path_vector.push_back(labyrinth::OutPaths::North);
    }
    if (out_paths_string.find('E') != std::string::npos) {
        out_path_vector.push_back(labyrinth::OutPaths::East);
    }
    if (out_paths_string.find('S') != std::string::npos) {
        out_path_vector.push_back(labyrinth::OutPaths::South);
    }
    if (out_paths_string.find('W') != std::string::npos) {
        out_path_vector.push_back(labyrinth::OutPaths::West);
    }
    return getBitmask(std::begin(out_path_vector), std::end(out_path_vector));
}

labyrinth::OutPaths getBitmask(const std::initializer_list<labyrinth::OutPaths> & out_paths) {
    return getBitmask(std::begin(out_paths), std::end(out_paths));
}



