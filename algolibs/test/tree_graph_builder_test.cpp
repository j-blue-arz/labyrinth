#include "graphbuilder/tree_graph_builder.h"
#include "libexhsearch/graph_algorithms.h"

#include "util.h"

#include "gtest/gtest.h"
#include <set>

using namespace labyrinth;

TEST(TreeGraphBuilderTest, CorrectNeighborsForExtentOfTwo) {
    TreeGraphBuilder builder{};
    MazeGraph graph = builder.setExtent(2).buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 4);
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 0}, {Location{0, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{0, 1}, {Location{0, 0}, Location{1, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 0}, {Location{1, 1}}));
    EXPECT_TRUE(hasNeighbors(graph, Location{1, 1}, {Location{0, 1}, Location{1, 0}}));
}

TEST(TreeGraphBuilderTest, IsTreeForExtentOfFour) {
    TreeGraphBuilder builder{};
    MazeGraph graph = builder.setExtent(4).buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 16);
    EXPECT_EQ(countEdges(graph), 15);
    auto reachable_from_corner = reachable::reachableLocations(graph, Location{0, 0});
    EXPECT_EQ(reachable_from_corner.size(), 16);
}

TEST(TreeGraphBuilderTest, IsTreeForExtentOfEight) {
    TreeGraphBuilder builder{};
    MazeGraph graph = builder.setExtent(8).buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 64);
    EXPECT_EQ(countEdges(graph), 63);
    auto reachable_from_corner = reachable::reachableLocations(graph, Location{0, 0});
    EXPECT_EQ(reachable_from_corner.size(), 64);
}

TEST(TreeGraphBuilderTest, IsTreeForExtentOfSixteen) {
    TreeGraphBuilder builder{};
    MazeGraph graph = builder.setExtent(16).buildGraph();
    EXPECT_EQ(graph.getNumberOfNodes(), 256);
    EXPECT_EQ(countEdges(graph), 255);
    auto reachable_from_corner = reachable::reachableLocations(graph, Location{0, 0});
    EXPECT_EQ(reachable_from_corner.size(), 256);
}
