#pragma once
#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"

#include <sstream>
#include <set>

#include "gtest/gtest.h"

std::string locationsToString(std::set<graph::Location> locations) {
    std::stringstream stream;
    for (auto location : locations) {
        stream << location << ", ";
    }
    return stream.str();
}

::testing::AssertionResult hasNeighbors(const graph::MazeGraph & graph, const graph::Location & source, std::initializer_list<graph::Location> targets) {
    std::set<graph::Location> expected{targets};
    auto neighbors = graph.neighbors(source);
    std::set<graph::Location> actual{neighbors.begin(), neighbors.end()};
    if (actual == expected) {
        return ::testing::AssertionSuccess();
    }
    return ::testing::AssertionFailure() << "Expected neighbors: " << locationsToString(expected) << ", actual: " << locationsToString(actual);
}

::testing::AssertionResult assertNumNeighbors(const graph::MazeGraph & g, const graph::Location & source, size_t expected) {
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

size_t numNeighbors(const graph::MazeGraph & g, const graph::Location & source) {
    auto neighbors = g.neighbors(source);
    std::set<graph::Location> actual{neighbors.begin(), neighbors.end()};
    return actual.size();
}

size_t countEdges(const graph::MazeGraph & g) {
    size_t count = 0;
    for (auto row = 0; row < g.getExtent(); row++) {
        for (auto column = 0; column < g.getExtent(); column++) {
            count += numNeighbors(g, graph::Location{row, column});
        }
    }
    return count / 2;
}

