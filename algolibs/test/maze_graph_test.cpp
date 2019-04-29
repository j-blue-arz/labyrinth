#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"
#include "util.h"

#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include <set>

using namespace graph;

class MazeGraphTest : public ::testing::Test {
protected:
    static const size_t extent = 3;

    MazeGraphTest() : graph_(extent) {}

    /*
    "###|#.#|#.#|"
    "#..|...|..#|"
    "#.#|#.#|###|"
    "------------"
    "#.#|###|###|"
    "#..|...|...|"
    "#.#|###|###|"
    "------------"
    "#.#|#.#|###|"
    "#..|#.#|..#|"
    "###|#.#|#.#|"
    "------------"*/

    void SetUp() override {
        graph_.setOutPaths(Location(0, 0), "ES");
        graph_.setOutPaths(Location(0, 1), "NESW");
        graph_.setOutPaths(Location(0, 2), "NW");

        graph_.setOutPaths(Location(1, 0), "NES");
        graph_.setOutPaths(Location(1, 1), "EW");
        graph_.setOutPaths(Location(1, 2), "EW");

        graph_.setOutPaths(Location(2, 0), "NE");
        graph_.setOutPaths(Location(2, 1), "NS");
        graph_.setOutPaths(Location(2, 2), "WS");
    }

    MazeGraph graph_;
};

const size_t MazeGraphTest::extent;

TEST_F(MazeGraphTest, NumberOfNodesIsCorrect) {
    EXPECT_EQ(graph_.getNumberOfNodes(), 9);
}

TEST_F(MazeGraphTest, AllNodesHaveUniqueIds) {
    std::set<MazeGraph::NodeId> ids;
    for(auto row = 0; row < MazeGraphTest::extent; row++) {
        for(auto column = 0; column < MazeGraphTest::extent; column++) {
            ids.insert(graph_.getNodeId(Location(row, column)));
        }
    }
    EXPECT_EQ(ids.size(), graph_.getNumberOfNodes()) << "duplicate node ids detected";
}

TEST_F(MazeGraphTest, NodeIdsAreConsecutiveStartingWith0) {
    std::set<MazeGraph::NodeId> ids;
    for(auto row = 0; row < MazeGraphTest::extent; row++) {
        for(auto column = 0; column < MazeGraphTest::extent; column++) {
            ids.insert(graph_.getNodeId(Location(row, column)));
        }
    }
    for(MazeGraph::NodeId id = 0; id < ids.size(); id++) {
        EXPECT_TRUE(ids.find(id) != ids.end()) << "Node id " << id << " is not contained in the graph.";
    }
}

TEST_F(MazeGraphTest, NodeIdOfLeftoverIs49forExtent7) {
    MazeGraph graph(7);
    auto leftover_id = graph.getLeftoverNodeId();
    EXPECT_EQ(leftover_id, 49);

}

TEST_F(MazeGraphTest, NeighborsForCornerWithOneNeighbor) {
    EXPECT_TRUE(hasNeighbors(graph_, Location(0, 2), {Location(0, 1)}));
}

TEST_F(MazeGraphTest, NeighborsForCornerWithNoNeighbor) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location(2, 2), 0));
}

TEST_F(MazeGraphTest, NeighborsForBorderWithNoNeighbor) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location(2, 1), 0));
}

TEST_F(MazeGraphTest, NeighborsForInnerNodeWithTwoNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location(1, 1), {Location(1, 0), Location(1, 2)}));
}

TEST_F(MazeGraphTest, NeighborsForBorderNodeWithThreeNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location(1, 0), {Location(0, 0), Location(1, 1), Location(2, 0)}));
}

TEST_F(MazeGraphTest, NeighborsForBorderNodeWithThreeNeighbors_Iter) {
    auto neighbors = graph_.neighbors(Location(1, 0));
    std::set<Location> neighbor_set;
    for(auto iter = neighbors.begin(); iter != neighbors.end(); iter++) {
        Location location = *iter;
        neighbor_set.insert(location);
    }
    EXPECT_THAT(neighbor_set, testing::SizeIs(3));
    auto expected = std::set<Location>{Location(0, 0), Location(1, 1), Location(2, 0)};
    EXPECT_EQ(neighbor_set, expected) <<
        "(1, 0) should have three neighbors, (0, 0), (1, 1), and (2, 0).";
}

TEST_F(MazeGraphTest, GetShiftLocationsWithoutValidLocations) {
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_THAT(shift_locations, testing::IsEmpty());
}

TEST_F(MazeGraphTest, GetShiftLocationsWithTwoValidLocations) {
    graph_.addShiftLocation(Location(0, 2));
    graph_.addShiftLocation(Location(0, 1));
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_THAT(shift_locations, testing::SizeIs(2));
    EXPECT_THAT(shift_locations, testing::UnorderedElementsAre(Location(0, 1), Location(0, 2)));
}

TEST_F(MazeGraphTest, GetShiftLocationsWithTwoEqualLocations) {
    graph_.addShiftLocation(Location(0, 2));
    graph_.addShiftLocation(Location(0, 2));
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_THAT(shift_locations, testing::SizeIs(1));
    EXPECT_THAT(shift_locations, testing::UnorderedElementsAre(Location(0, 2)));
}

TEST_F(MazeGraphTest, ShiftLocationComparesEqualToLocation) {
    graph_.addShiftLocation(Location(1, 0));
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_TRUE(*shift_locations.begin() == Location(1, 0)) << "Location object and return value of getShiftLocations() are not comparable";
}

TEST_F(MazeGraphTest, ShiftLocationComparesUnequalToLocation) {
    graph_.addShiftLocation(Location(1, 0));
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_TRUE(*shift_locations.begin() != Location(1, 1)) << "Location object and return value of getShiftLocations() are not comparable";
}

TEST_F(MazeGraphTest, ShiftAlongColumnResultsInCorrectNodeIds) {
    MazeGraph::NodeId old_column_ids[] = {graph_.getNodeId(Location(0, 1)), graph_.getNodeId(Location(1, 1)), graph_.getNodeId(Location(2, 1))};

    graph_.shift(Location(0, 1), 0);

    EXPECT_EQ(old_column_ids[0], graph_.getNodeId(Location(1, 1)));
    EXPECT_EQ(old_column_ids[1], graph_.getNodeId(Location(2, 1)));
}

TEST_F(MazeGraphTest, ShiftAlongColumnResultsInCorrectPaths) {
    
    graph_.shift(Location(0, 1), 0);

    EXPECT_TRUE(hasNeighbors(graph_, Location(1, 1), {Location(1, 0), Location(1, 2)}));
    EXPECT_TRUE(hasNeighbors(graph_, Location(2, 1), {Location(2, 0), Location(2, 2)}));
}

TEST_F(MazeGraphTest, ShiftAlongColumnInsertsLeftover) {
    graph_.setLeftoverOutPaths("ES");
    auto old_leftover_id = graph_.getLeftoverNodeId();

    graph_.shift(Location(0, 1), 0);

    EXPECT_EQ(old_leftover_id, graph_.getNodeId(Location(0, 1)));
    EXPECT_TRUE(hasNeighbors(graph_, Location(0, 1), {Location(1, 1), Location(0, 2)}));
}

TEST_F(MazeGraphTest, ShiftAlongColumnUpdatesLeftover) {
    auto pushed_out_id = graph_.getNodeId(Location(2, 1));

    graph_.shift(Location(0, 1), 0);

    EXPECT_EQ(pushed_out_id, graph_.getLeftoverNodeId());
}

TEST_F(MazeGraphTest, ShiftAlongRowResultsInCorrectNodeIds) {
    MazeGraph::NodeId old_row_ids[] = {graph_.getNodeId(Location(1, 0)), graph_.getNodeId(Location(1, 1)), graph_.getNodeId(Location(1, 2))};

    graph_.shift(Location(1, 2), 0);

    EXPECT_EQ(old_row_ids[1], graph_.getNodeId(Location(1, 0)));
    EXPECT_EQ(old_row_ids[2], graph_.getNodeId(Location(1, 1)));
}

TEST_F(MazeGraphTest, ShiftAlongRowResultsInCorrectPaths) {

    graph_.shift(Location(1, 2), 0);

    EXPECT_TRUE(hasNeighbors(graph_, Location(1, 1), {Location(1, 0)}));
    EXPECT_TRUE(hasNeighbors(graph_, Location(1, 0), {Location(1, 1)}));
}

TEST_F(MazeGraphTest, ShiftAlongRowInsertsLeftover) {
    graph_.setLeftoverOutPaths("NEW");
    auto old_leftover_id = graph_.getLeftoverNodeId();

    graph_.shift(Location(1, 2), 0);

    EXPECT_EQ(old_leftover_id, graph_.getNodeId(Location(1, 2)));
    EXPECT_TRUE(hasNeighbors(graph_, Location(1, 2), {Location(1, 1)}));
}

TEST_F(MazeGraphTest, TwoShiftsResultInCorrectPathAroundPushedOutAndPushedInNode) {
    graph_.addShiftLocation(Location(2, 1));
    graph_.addShiftLocation(Location(1, 2));
    auto pushed_out_id = graph_.getNodeId(Location(1, 0));

    graph_.shift(Location(1, 2), 0);
    graph_.shift(Location(2, 1), 0);

    EXPECT_EQ(pushed_out_id, graph_.getNodeId(Location(2, 1)));
    EXPECT_TRUE(hasNeighbors(graph_, Location(2, 1), {Location(1, 1), Location(2, 2)}));
}

TEST_F(MazeGraphTest, shift_tJunctWithRotation_resultsInCorrectNeighbors) {
    graph_.setLeftoverOutPaths("NES");

    graph_.shift(Location(2, 1), 90);

    EXPECT_TRUE(hasNeighbors(graph_, Location(2, 1), {Location(2, 0), Location(2, 2)}));
}

TEST_F(MazeGraphTest, shift_cornerWithRotation_resultsInCorrectNeighbors) {
    graph_.setLeftoverOutPaths("NE");

    graph_.shift(Location(2, 1), 270);

    EXPECT_TRUE(hasNeighbors(graph_, Location(2, 1), {Location(2, 0), Location(1, 1)}));
}

TEST_F(MazeGraphTest, LocationOfNode_WithInnerNode_ReturnsCorrectLocation) {
    auto node_id = graph_.getNodeId(Location(1, 1));

    Location location = graph_.getLocation(node_id, Location(-1, -1));

    EXPECT_EQ(location, Location(1, 1));
}

TEST_F(MazeGraphTest, LocationOfNode_WithInnerNodeAfterShift_ReturnsCorrectLocation) {
    auto node_id = graph_.getNodeId(Location(1, 1));

    graph_.shift(Location(0, 1), 0);

    Location location = graph_.getLocation(node_id, Location(1, 1));
    EXPECT_EQ(location, Location(2, 1));
}

TEST_F(MazeGraphTest, LocationOfNode_WithLeftoverNodeId_ReturnsGivenLocation) {
    Location location = graph_.getLocation(9, Location(0, 1));
    EXPECT_EQ(location, Location(0, 1));
}

TEST_F(MazeGraphTest, LocationOfNode_WithLeftoverNodeIdAfterShift_ReturnsInsertedLocation) {
    auto old_leftover_id = graph_.getLeftoverNodeId();

    graph_.shift(Location(1, 2), 0);

    Location location = graph_.getLocation(old_leftover_id, Location(1, 1));
    EXPECT_EQ(location, Location(1, 2));
}
