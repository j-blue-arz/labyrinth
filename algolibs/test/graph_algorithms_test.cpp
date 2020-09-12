#include "graphbuilder/text_graph_builder.h"
#include "libexhsearch/graph_algorithms.h"

#include "gtest/gtest.h"

using namespace labyrinth;

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
                                            "#..|#..|#..|",
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
    graph_.shift(Location{1, 0}, 0);
    EXPECT_TRUE(reachable::isReachable(graph_, Location{0, 0}, Location{1, 0}));
}
