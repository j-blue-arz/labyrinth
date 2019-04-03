#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"

#include "gtest/gtest.h"

#include <set>

using namespace graph;

class MazeGraphTest : public ::testing::Test {
protected:
    static const size_t extent = 3;

    MazeGraphTest() : graph_(extent) {}

    void SetUp() override {
        graph_.setOutPaths(Location(0, 0), "ES");
        graph_.setOutPaths(Location(0, 1), "ESW");
        graph_.setOutPaths(Location(0, 2), "NW");

        graph_.setOutPaths(Location(1, 0), "NES");
        graph_.setOutPaths(Location(1, 1), "EW");
        graph_.setOutPaths(Location(1, 2), "EW");

        graph_.setOutPaths(Location(2, 0), "NE");
        graph_.setOutPaths(Location(2, 1), "ES");
        graph_.setOutPaths(Location(2, 2), "ES");
    }

    MazeGraph graph_;
};

const size_t MazeGraphTest::extent;


TEST_F(MazeGraphTest, NumberOfNodesIsCorrect) {
    EXPECT_EQ(graph_.getNumberOfNodes(), 9);
}

TEST_F(MazeGraphTest, AllNodesHaveUniqueIds) {
    std::set<MazeGraph::NodeId> ids;
    for (auto row = 0; row < MazeGraphTest::extent; row++) {
        for (auto column = 0; column < MazeGraphTest::extent; column++) {
            ids.insert(graph_.getNodeId(Location(row, column)));
        }
    }
    EXPECT_EQ(ids.size(), graph_.getNumberOfNodes()) << "duplicate node ids detected";
}

TEST_F(MazeGraphTest, NodeIdsAreConsecutiveStartingWith0) {
    std::set<MazeGraph::NodeId> ids;
    for (auto row = 0; row < MazeGraphTest::extent; row++) {
        for (auto column = 0; column < MazeGraphTest::extent; column++) {
            ids.insert(graph_.getNodeId(Location(row, column)));
        }
    }
    for (MazeGraph::NodeId id = 0; id < ids.size(); id++) {
        EXPECT_TRUE(ids.find(id) != ids.end()) << "Node id " << id << " is not contained in the graph.";
    }
}

TEST_F(MazeGraphTest, NeighborsForCornerWithOneNeighbor) {
    auto neighbors = graph_.neighbors(Location(0, 2));
    std::set<Location> neighbor_set(neighbors.begin(), neighbors.end());
    EXPECT_EQ(neighbor_set.size(), 1);
    EXPECT_EQ(neighbor_set, std::set<Location>{Location(0, 1)}) << "(0, 2) should have only one neighbor, (0, 1).";
}

TEST_F(MazeGraphTest, NeighborsForCornerWithNoNeighbor) {
    auto neighbors = graph_.neighbors(Location(2, 2));
    std::set<Location> neighbor_set(neighbors.begin(), neighbors.end());
    EXPECT_EQ(neighbor_set.size(), 0) << "(2, 2) should not have any neighbors.";
}

TEST_F(MazeGraphTest, NeighborsForInnerNodeWithTwoNeighbors) {
    auto neighbors = graph_.neighbors(Location(1, 1));
    std::set<Location> neighbor_set(neighbors.begin(), neighbors.end());
    EXPECT_EQ(neighbor_set.size(), 2);
    auto expected = std::set<Location>{ Location(1, 0), Location(1, 2) };
    EXPECT_EQ(neighbor_set, expected) << "(1, 1) should have two neighbors, (1, 0) and (1, 2).";
}

TEST_F(MazeGraphTest, NeighborsForBorderNodeWithThreeNeighbors) {
    auto neighbors = graph_.neighbors(Location(1, 0));
    std::set<Location> neighbor_set(neighbors.begin(), neighbors.end());
    EXPECT_EQ(neighbor_set.size(), 3);
    auto expected = std::set<Location>{ Location(0, 0), Location(1, 1), Location(2, 0) };
    EXPECT_EQ(neighbor_set, expected) <<
        "(1, 1) should have three neighbors, (0, 0), (1, 1), and (2, 0).";
}

TEST_F(MazeGraphTest, NeighborsForBorderNodeWithThreeNeighbors_Iter) {
    auto neighbors = graph_.neighbors(Location(1, 0));
    std::set<Location> neighbor_set;
    for (auto iter = neighbors.begin(); iter != neighbors.end(); iter++) {
        Location location = *iter;
        neighbor_set.insert(location);
    }
    EXPECT_EQ(neighbor_set.size(), 3);
    auto expected = std::set<Location>{ Location(0, 0), Location(1, 1), Location(2, 0) };
    EXPECT_EQ(neighbor_set, expected) <<
        "(1, 1) should have three neighbors, (0, 0), (1, 1), and (2, 0).";
}



