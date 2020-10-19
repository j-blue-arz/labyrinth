#include "util.h"

using namespace labyrinth;
using namespace labyrinth::testutils;

namespace {
std::vector<Location> getNeighbors(const MazeGraph& graph, const Location& location) {
    std::vector<Location> result;
    result.reserve(4);
    auto iter = graph.neighbors(location);
    while (!iter.isAtEnd()) {
        result.push_back(*iter);
        ++iter;
    }
    return result;
}
} // namespace

std::string labyrinth::testutils::locationsToString(std::set<labyrinth::Location> locations) {
    std::stringstream stream;
    for (const auto& location : locations) {
        stream << location << ", ";
    }
    return stream.str();
}

::testing::AssertionResult labyrinth::testutils::hasNeighbors(const labyrinth::MazeGraph& graph,
                                                              const labyrinth::Location& source,
                                                              std::set<labyrinth::Location> expected) {
    auto neighbors = getNeighbors(graph, source);
    std::set<labyrinth::Location> actual{neighbors.begin(), neighbors.end()};
    if (actual == expected) {
        return ::testing::AssertionSuccess();
    }
    return ::testing::AssertionFailure() << "Expected neighbors: " << locationsToString(expected)
                                         << ", actual: " << locationsToString(actual);
}

::testing::AssertionResult labyrinth::testutils::assertNumNeighbors(const labyrinth::MazeGraph& graph,
                                                                    const labyrinth::Location& source,
                                                                    size_t expected) {
    const auto neighbors = getNeighbors(graph, source);
    size_t actual = std::distance(std::cbegin(neighbors), std::cend(neighbors));
    if (actual == expected) {
        return ::testing::AssertionSuccess();
    }
    return ::testing::AssertionFailure() << "Expected neighbors: " << expected << ", actual: " << actual;
}

labyrinth::OutPaths labyrinth::testutils::getBitmask(std::string out_paths_string) {
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

labyrinth::OutPaths labyrinth::testutils::getBitmask(const std::vector<labyrinth::OutPaths>& out_paths) {
    return getBitmask(std::begin(out_paths), std::end(out_paths));
}
