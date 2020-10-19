#include <algorithm>

#include "graphbuilder/text_graph_builder.h"
#include "solvers/graph_algorithms.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

using namespace labyrinth;

::testing::AssertionResult reachableFromIndex(const std::vector<reachable::ReachableNode>& reachable_nodes, Location location, size_t index) {
    auto iter = std::find_if(reachable_nodes.begin(), reachable_nodes.end(), [&location](auto& reachable_node) {
        return reachable_node.reached_location == location;
    });
    if (iter == reachable_nodes.end()) {
        return ::testing::AssertionFailure() << "Location " << location << " was not reached.";
    }
    auto reachable_node = *iter;
    if(reachable_node.parent_source_index != index) {
        return ::testing::AssertionFailure() << "Expected parent index " << index << ", but was " << reachable_node.parent_source_index;
    }
    return ::testing::AssertionSuccess();
}

class GraphAlgorithmsTest : public ::testing::Test {
protected:
    void SetUp() override {
        TextGraphBuilder builder{};
        const std::vector<std::string> maze{"###|###|#.#|",
                                            "#..|...|..#|",
                                            "#.#|#.#|###|",
                                            "------------",
                                            "#.#|###|###|",
                                            "#..|...|...|",
                                            "#.#|###|###|",
                                            "------------",
                                            "#.#|###|###|",
                                            "#..|#..|...|",
                                            "###|#.#|#.#|",
                                            "------------"};
        graph_ = builder.setMaze(maze).buildGraph();
        graph_.setLeftoverOutPaths(OutPaths::North);
    }

    MazeGraph graph_{0};
};

TEST_F(GraphAlgorithmsTest, isReachable_withNeighboringNodes_returnsTrue) {
    EXPECT_TRUE(reachable::isReachable(graph_, Location{0, 0}, Location{0, 1}));
}

TEST_F(GraphAlgorithmsTest, isReachable_withDistanceOfTwo_returnsTrue) {
    EXPECT_TRUE(reachable::isReachable(graph_, Location{1, 1}, Location{0, 0}));
}

TEST_F(GraphAlgorithmsTest, isReachable_withLongerPath_returnsTrue) {
    EXPECT_TRUE(reachable::isReachable(graph_, Location{2, 0}, Location{0, 2}));
}

TEST_F(GraphAlgorithmsTest, isReachable_withUnconnectedCorners_returnsFalse) {
    EXPECT_FALSE(reachable::isReachable(graph_, Location{2, 2}, Location{0, 0}));
}

TEST_F(GraphAlgorithmsTest, isReachable_withUnconnectedNeighbors_returnsFalse) {
    EXPECT_FALSE(reachable::isReachable(graph_, Location{2, 1}, Location{1, 1}));
}

TEST_F(GraphAlgorithmsTest, isReachable_withPathToInsertedNode_returnsTrue) {
    graph_.shift(Location{1, 0}, RotationDegreeType::_0);
    EXPECT_TRUE(reachable::isReachable(graph_, Location{0, 0}, Location{1, 0}));
}

TEST_F(GraphAlgorithmsTest, multiSourceReachableLocations_withTwoSources_returnsCorrectLocations) {
    std::vector<Location> sources = {Location{0, 0}, Location{2, 2}};
    auto reachableLocations = reachable::multiSourceReachableLocations(graph_, sources);
    ASSERT_THAT(reachableLocations, testing::SizeIs(9));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{0, 0}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{0, 1}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{0, 2}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{1, 0}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{1, 1}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{1, 2}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{2, 0}, 0));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{2, 1}, 1));
    ASSERT_TRUE(reachableFromIndex(reachableLocations, Location{2, 2}, 1));
}
