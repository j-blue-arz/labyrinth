#include "libexhsearch/tree_graph_builder.h"
#include "libexhsearch/graph_algorithms.h"

#include "gtest/gtest.h"
#include <set>

using namespace graph;

std::string locationsToString(std::set<Location> locations) {
    std::stringstream stream;
    for (auto location : locations) {
        stream << location << ", ";
    }
    return stream.str();
}

::testing::AssertionResult hasNeighbors(const StaticGraph & graph, const Location & source, std::initializer_list<Location> targets) {
    std::set<Location> expected{ targets };
    auto neighbors = graph.neighbors(source);
    std::set<Location> actual{ neighbors.begin(), neighbors.end() };
    if (actual == expected) {
        return ::testing::AssertionSuccess();
    }
    return ::testing::AssertionFailure() << "Expected neighbors: " << locationsToString(expected) << ", actual: " << locationsToString(actual);
}

size_t numNeighbors(const StaticGraph & graph, const Location & source) {
    auto neighbors = graph.neighbors(source);
    std::set<Location> actual{ neighbors.begin(), neighbors.end() };
    return actual.size();
}

size_t countEdges(const StaticGraph & graph) {
    size_t count = 0;
    for (auto row = 0; row < graph.getExtent(); row++) {
        for (auto column = 0; column < graph.getExtent(); column++) {
            count += numNeighbors(graph, Location(row, column));
        }
    }
    return count / 2;
}

TEST(TreeGraphBuilderTest, CorrectNeighborsForExtentOfTwo) {
    TreeGraphBuilder builder{};
    StaticGraph graph = builder.buildGraph(2);
    EXPECT_EQ(graph.getNumberOfNodes(), 4);
    EXPECT_TRUE(hasNeighbors(graph, Location(0, 0), { Location(0, 1) }));
    EXPECT_TRUE(hasNeighbors(graph, Location(0, 1), { Location(0, 0), Location(1, 1) }));
    EXPECT_TRUE(hasNeighbors(graph, Location(1, 0), { Location(1, 1) }));
    EXPECT_TRUE(hasNeighbors(graph, Location(1, 1), { Location(0, 1), Location(1, 0) }));
}

TEST(TreeGraphBuilderTest, IsTreeForExtentOfFour) {
    TreeGraphBuilder builder{};
    StaticGraph graph = builder.buildGraph(4);
    EXPECT_EQ(graph.getNumberOfNodes(), 16);
    EXPECT_EQ(countEdges(graph), 15);
    auto reachable_from_corner = algorithm::reachableLocations(graph, Location(0, 0));
    EXPECT_EQ(reachable_from_corner.size(), 16);
}

TEST(TreeGraphBuilderTest, IsTreeForExtentOfEight) {
    TreeGraphBuilder builder{};
    StaticGraph graph = builder.buildGraph(8);
    EXPECT_EQ(graph.getNumberOfNodes(), 64);
    EXPECT_EQ(countEdges(graph), 63);
    auto reachable_from_corner = algorithm::reachableLocations(graph, Location(0, 0));
    EXPECT_EQ(reachable_from_corner.size(), 64);
}

TEST(TreeGraphBuilderTest, IsTreeForExtentOfSixteen) {
    TreeGraphBuilder builder{};
    StaticGraph graph = builder.buildGraph(16);
    EXPECT_EQ(graph.getNumberOfNodes(), 256);
    EXPECT_EQ(countEdges(graph), 255);
    auto reachable_from_corner = algorithm::reachableLocations(graph, Location(0, 0));
    EXPECT_EQ(reachable_from_corner.size(), 256);
}