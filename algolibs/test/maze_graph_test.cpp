#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"
#include "util.h"

#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include <set>

using namespace labyrinth;
using namespace labyrinth::testutils;

class MazeGraphTest : public ::testing::Test {
protected:
    static const size_t extent = 3;

    MazeGraphTest() : graph_{extent} {}

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
        graph_.setOutPaths(Location{0, 0}, getBitmask("ES"));
        graph_.setOutPaths(Location{0, 1}, getBitmask("NESW"));
        graph_.setOutPaths(Location{0, 2}, getBitmask("NW"));

        graph_.setOutPaths(Location{1, 0}, getBitmask("NES"));
        graph_.setOutPaths(Location{1, 1}, getBitmask("EW"));
        graph_.setOutPaths(Location{1, 2}, getBitmask("EW"));

        graph_.setOutPaths(Location{2, 0}, getBitmask("NE"));
        graph_.setOutPaths(Location{2, 1}, getBitmask("NS"));
        graph_.setOutPaths(Location{2, 2}, getBitmask("WS"));
    }

    MazeGraph graph_;

    
};

const size_t MazeGraphTest::extent;

TEST_F(MazeGraphTest, constructedGraph_hasCorrectNumberOfNodes) {
    EXPECT_EQ(graph_.getNumberOfNodes(), 9);
}

TEST_F(MazeGraphTest, constructedGraph_hasUniqueNodeIds) {
    std::set<NodeId> ids;
    for (auto row = 0u; row < MazeGraphTest::extent; row++) {
        for (auto column = 0u; column < MazeGraphTest::extent; column++) {
            ids.insert(graph_.getNode(Location{row, column}).node_id);
        }
    }
    EXPECT_EQ(ids.size(), graph_.getNumberOfNodes()) << "duplicate node ids detected";
}

TEST_F(MazeGraphTest, constructedGraph_hasConsecutiveNodeIdsStartingWith0) {
    std::set<NodeId> ids;
    for (auto row = 0u; row < MazeGraphTest::extent; row++) {
        for (auto column = 0u; column < MazeGraphTest::extent; column++) {
            ids.insert(graph_.getNode(Location{row, column}).node_id);
        }
    }
    for (NodeId id = 0; id < ids.size(); id++) {
        EXPECT_TRUE(ids.find(id) != ids.end()) << "Node id " << id << " is not contained in the graph.";
    }
}

TEST_F(MazeGraphTest, constructedGraph_withExtent7_assignsNodeId49toLeftover) {
    const MazeGraph graph{7};
    auto leftover_id = graph.getLeftover().node_id;
    EXPECT_EQ(leftover_id, 49u);

}

TEST_F(MazeGraphTest, neighbors_forCornerWithOneNeighbor) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 2}, {Location{0, 1}}));
}

TEST_F(MazeGraphTest, neighbors_forCornerWithNoNeighbor) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location{2, 2}, 0));
}

TEST_F(MazeGraphTest, neighbors_forBorderWithNoNeighbor) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location{2, 1}, 0));
}

TEST_F(MazeGraphTest, neighbors_forInnerNodeWithTwoNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 1}, {Location{1, 0}, Location{1, 2}}));
}

TEST_F(MazeGraphTest, neighbors_forBorderNodeWithThreeNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 0}, {Location{0, 0}, Location{1, 1}, Location{2, 0}}));
}

TEST_F(MazeGraphTest, neighbors_forBorderNodeWithThreeNeighbors_isIterable) {
    auto neighbors = graph_.neighbors(Location{1, 0});
    std::set<Location> neighbor_set;
    for (auto iter = neighbors.begin(); iter != neighbors.end(); ++iter) {
        Location location = *iter;
        neighbor_set.insert(location);
    }
    EXPECT_THAT(neighbor_set, testing::SizeIs(3));
    auto expected = std::set<Location>{Location{0, 0}, Location{1, 1}, Location{2, 0}};
    EXPECT_EQ(neighbor_set, expected) <<
        "(1, 0) should have three neighbors, (0, 0), (1, 1), and (2, 0).";
}

TEST_F(MazeGraphTest, getShiftLocations_withoutValidLocations_returnsEmptyCollection) {
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_THAT(shift_locations, testing::IsEmpty());
}

TEST_F(MazeGraphTest, getShiftLocations_withTwoValidLocations_returnsBoth) {
    graph_.addShiftLocation(Location{0, 2});
    graph_.addShiftLocation(Location{0, 1});
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_THAT(shift_locations, testing::SizeIs(2));
    EXPECT_THAT(shift_locations, testing::UnorderedElementsAre(Location{0, 1}, Location{0, 2}));
}

TEST_F(MazeGraphTest, getShiftLocations_withAddingTwoEqualLocations_returnsOnlyOne) {
    graph_.addShiftLocation(Location{0, 2});
    graph_.addShiftLocation(Location{0, 2});
    auto shift_locations = graph_.getShiftLocations();
    EXPECT_THAT(shift_locations, testing::SizeIs(1));
    EXPECT_THAT(shift_locations, testing::UnorderedElementsAre(Location{0, 2}));
}

TEST_F(MazeGraphTest, shift_alongColumn_resultsInCorrectNodeIds) {
    NodeId old_column_ids[] = {graph_.getNode(Location{0, 1}).node_id, graph_.getNode(Location{1, 1}).node_id, graph_.getNode(Location{2, 1}).node_id};

    graph_.shift(Location{0, 1}, 0);

    EXPECT_EQ(old_column_ids[0], graph_.getNode(Location{1, 1}).node_id);
    EXPECT_EQ(old_column_ids[1], graph_.getNode(Location{2, 1}).node_id);
}

TEST_F(MazeGraphTest, shift_alongColumn_resultsInCorrectPaths) {

    graph_.shift(Location{0, 1}, 0);

    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 1}, {Location{1, 0}, Location{1, 2}}));
    EXPECT_TRUE(hasNeighbors(graph_, Location{2, 1}, {Location{2, 0}, Location{2, 2}}));
}

TEST_F(MazeGraphTest, shift_alongColumn_insertsLeftover) {
    graph_.setLeftoverOutPaths(getBitmask("ES"));
    auto old_leftover_id = graph_.getLeftover().node_id;

    graph_.shift(Location{0, 1}, 0);

    EXPECT_EQ(old_leftover_id, graph_.getNode(Location{0, 1}).node_id);
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 1}, {Location{1, 1}, Location{0, 2}}));
}

TEST_F(MazeGraphTest, shift_alongColumn_updatesLeftover) {
    auto pushed_out_id = graph_.getNode(Location{2, 1}).node_id;

    graph_.shift(Location{0, 1}, 0);

    EXPECT_EQ(pushed_out_id, graph_.getLeftover().node_id);
}

TEST_F(MazeGraphTest, shift_alongRow_resultsInCorrectNodeIds) {
    NodeId old_row_ids[] = {graph_.getNode(Location{1, 0}).node_id, graph_.getNode(Location{1, 1}).node_id, graph_.getNode(Location{1, 2}).node_id};

    graph_.shift(Location{1, 2}, 0);

    EXPECT_EQ(old_row_ids[1], graph_.getNode(Location{1, 0}).node_id);
    EXPECT_EQ(old_row_ids[2], graph_.getNode(Location{1, 1}).node_id);
}

TEST_F(MazeGraphTest, shift_alongRow_resultsInCorrectPaths) {

    graph_.shift(Location{1, 2}, 0);

    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 1}, {Location{1, 0}}));
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 0}, {Location{1, 1}}));
}

TEST_F(MazeGraphTest, shift_alongRow_insertsLeftover) {
    graph_.setLeftoverOutPaths(getBitmask("NEW"));
    auto old_leftover_id = graph_.getLeftover().node_id;

    graph_.shift(Location{1, 2}, 0);

    EXPECT_EQ(old_leftover_id, graph_.getNode(Location{1, 2}).node_id);
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 2}, {Location{1, 1}}));
}

TEST_F(MazeGraphTest, shift_atOppositeLocationOfPreviouslyPushedInNode_insertsCorrectNodeAndResultsInCorrectNeighbors) {
    graph_.addShiftLocation(Location{2, 1});
    graph_.addShiftLocation(Location{1, 2});
    auto pushed_out_id = graph_.getNode(Location{1, 0}).node_id;

    graph_.shift(Location{1, 2}, 0);
    graph_.shift(Location{2, 1}, 0);

    EXPECT_EQ(pushed_out_id, graph_.getNode(Location{2, 1}).node_id);
    EXPECT_TRUE(hasNeighbors(graph_, Location{2, 1}, {Location{1, 1}, Location{2, 2}}));
}

TEST_F(MazeGraphTest, shift_tJunctWithRotation_resultsInCorrectNeighbors) {
    graph_.setLeftoverOutPaths(getBitmask("NES"));

    graph_.shift(Location{2, 1}, 90);

    EXPECT_TRUE(hasNeighbors(graph_, Location{2, 1}, {Location{2, 0}, Location{2, 2}}));
}

TEST_F(MazeGraphTest, shift_cornerWithRotation_resultsInCorrectNeighbors) {
    graph_.setLeftoverOutPaths(getBitmask("NE"));

    graph_.shift(Location{2, 1}, 270);

    EXPECT_TRUE(hasNeighbors(graph_, Location{2, 1}, {Location{2, 0}, Location{1, 1}}));
}

TEST_F(MazeGraphTest, getLocation_WithInnerNode_ReturnsCorrectLocation) {
    auto node_id = graph_.getNode(Location{1, 1}).node_id;

    Location location = graph_.getLocation(node_id, Location{-1, -1});

    EXPECT_EQ(location, (Location{1, 1}));
}

TEST_F(MazeGraphTest, getLocation_WithInnerNodeAfterShift_ReturnsCorrectLocation) {
    auto node_id = graph_.getNode(Location{1, 1}).node_id;

    graph_.shift(Location{0, 1}, 0);

    Location location = graph_.getLocation(node_id, Location{1, 1});
    EXPECT_EQ(location, (Location{2, 1}));
}

TEST_F(MazeGraphTest, getLocation_WithLeftoverNodeId_ReturnsGivenLocation) {
    Location location = graph_.getLocation(9, Location{0, 1});
    EXPECT_EQ(location, (Location{0, 1}));
}

TEST_F(MazeGraphTest, LocationOfNode_WithLeftoverNodeIdAfterShift_ReturnsInsertedLocation) {
    auto old_leftover_id = graph_.getLeftover().node_id;

    graph_.shift(Location{1, 2}, 0);

    Location location = graph_.getLocation(old_leftover_id, Location{1, 1});
    EXPECT_EQ(location, (Location{1, 2}));
}

TEST_F(MazeGraphTest, constructGraph_withLinearizedInputNodes_modificationOfInputNodeDoesNotAlterGraph) {
    std::vector<Node> nodes;
    nodes.push_back(Node{0, getBitmask("ES"), 0});
    nodes.push_back(Node{1, getBitmask("NESW"), 0});
    nodes.push_back(Node{2, getBitmask("NW"), 0});

    nodes.push_back(Node{3, getBitmask("NES"), 0});
    nodes.push_back(Node{4, getBitmask("EW"), 0});
    nodes.push_back(Node{5, getBitmask("EW"), 0});

    nodes.push_back(Node{6, getBitmask("NE"), 0});
    nodes.push_back(Node{7, getBitmask("NS"), 0});
    nodes.push_back(Node{8, getBitmask("WS"), 0});

    nodes.push_back(Node{9, getBitmask("NS"), 0});

    MazeGraph graph{nodes};

    EXPECT_TRUE(hasOutPath(graph.getNode(Location{0, 0}), OutPaths::East));
    EXPECT_TRUE(hasOutPath(graph.getLeftover(), OutPaths::South));

    nodes[0].out_paths = getBitmask("NS");
    nodes[9].out_paths = getBitmask("EW");

    EXPECT_TRUE(hasOutPath(graph.getNode(Location{0, 0}), OutPaths::East));
    EXPECT_TRUE(hasOutPath(graph.getLeftover(), OutPaths::South));
}

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

MazeGraph createMazeGraphWithInputNodes() {
    std::vector<Node> input_nodes;
    const OutPaths corner = getBitmask({OutPaths::North, OutPaths::East});
    const OutPaths straight = getBitmask({OutPaths::North, OutPaths::South});
    const OutPaths t_junct = getBitmask({OutPaths::North, OutPaths::East, OutPaths::South});
    const OutPaths cross = getBitmask({OutPaths::North, OutPaths::East, OutPaths::South, OutPaths::West});
    input_nodes.push_back(Node{5, corner, 90});
    input_nodes.push_back(Node{6, cross, 90});
    input_nodes.push_back(Node{7, corner, 270});
    input_nodes.push_back(Node{8, t_junct, 0});
    input_nodes.push_back(Node{9, straight, 90});
    input_nodes.push_back(Node{0, straight, 270});
    input_nodes.push_back(Node{1, corner, 0});
    input_nodes.push_back(Node{2, straight, 0});
    input_nodes.push_back(Node{3, corner, 180});
    input_nodes.push_back(Node{4, t_junct, 180});
    return MazeGraph(input_nodes);
}

TEST_F(MazeGraphTest, constructGraph_withLinearizedInputNodes_createsSameGraph) {
    const MazeGraph input_graph = createMazeGraphWithInputNodes();
    static const auto all_out_paths = {OutPaths::North, OutPaths::East, OutPaths::South, OutPaths::West};

    for (auto row = 0u; row < MazeGraphTest::extent; row++) {
        for (auto column = 0u; column < MazeGraphTest::extent; column++) {
            Location location{row, column};
            for (auto out_path : all_out_paths) {
                auto input_node = input_graph.getNode(location);
                auto expected_node = graph_.getNode(location);
                EXPECT_EQ(hasOutPath(input_node, out_path), hasOutPath(expected_node, out_path)) <<
                    "Created graph differs at location " << location; 
            }
        }
    }
}

TEST_F(MazeGraphTest, leftoverHasOutPath_withLinearizedInputNodes_isCorrect) {
    const MazeGraph input_graph = createMazeGraphWithInputNodes();
    auto leftover_node = input_graph.getLeftover();
    EXPECT_TRUE(hasOutPath(leftover_node, OutPaths::North));
    EXPECT_FALSE(hasOutPath(leftover_node, OutPaths::East));
    EXPECT_TRUE(hasOutPath(leftover_node, OutPaths::South));
    EXPECT_TRUE(hasOutPath(leftover_node, OutPaths::West));
}

TEST_F(MazeGraphTest, getNodeId_withLinearizedInputNodes_returnsCorrectIds) {
    const MazeGraph input_graph = createMazeGraphWithInputNodes();

    EXPECT_EQ(input_graph.getLeftover().node_id, 4u);
    EXPECT_EQ(input_graph.getNode(Location{0, 0}).node_id, 5);
    EXPECT_EQ(input_graph.getNode(Location{0, 1}).node_id, 6);
    EXPECT_EQ(input_graph.getNode(Location{0, 2}).node_id, 7);
    EXPECT_EQ(input_graph.getNode(Location{1, 0}).node_id, 8);
    EXPECT_EQ(input_graph.getNode(Location{1, 1}).node_id, 9);
    EXPECT_EQ(input_graph.getNode(Location{1, 2}).node_id, 0);
    EXPECT_EQ(input_graph.getNode(Location{2, 0}).node_id, 1);
    EXPECT_EQ(input_graph.getNode(Location{2, 1}).node_id, 2);
    EXPECT_EQ(input_graph.getNode(Location{2, 2}).node_id, 3);
}

TEST_F(MazeGraphTest, getLocation_withLinearizedInputNodes_returnsCorrectLocations) {
    const MazeGraph input_graph = createMazeGraphWithInputNodes();

    EXPECT_EQ(input_graph.getLocation(4, Location{-1, -1}), (Location{-1, -1}));
    EXPECT_EQ(input_graph.getLocation(5, Location{-1, -1}), (Location{0, 0}));
    EXPECT_EQ(input_graph.getLocation(6, Location{-1, -1}), (Location{0, 1}));
    EXPECT_EQ(input_graph.getLocation(7, Location{-1, -1}), (Location{0, 2}));
    EXPECT_EQ(input_graph.getLocation(8, Location{-1, -1}), (Location{1, 0}));
    EXPECT_EQ(input_graph.getLocation(9, Location{-1, -1}), (Location{1, 1}));
    EXPECT_EQ(input_graph.getLocation(0, Location{-1, -1}), (Location{1, 2}));
    EXPECT_EQ(input_graph.getLocation(1, Location{-1, -1}), (Location{2, 0}));
    EXPECT_EQ(input_graph.getLocation(2, Location{-1, -1}), (Location{2, 1}));
    EXPECT_EQ(input_graph.getLocation(3, Location{-1, -1}), (Location{2, 2}));
}
