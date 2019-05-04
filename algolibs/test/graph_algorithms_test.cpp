#include "graphbuilder/text_graph_builder.h"
#include "libexhsearch/graph_algorithms.h"

#include "gtest/gtest.h"

using namespace graph;

class GraphAlgorithmsTest : public ::testing::Test {
protected:

    void SetUp() override {
        TextGraphBuilder builder{};
        const std::vector<std::string> maze{
            "###|###|#.#|",
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
            "------------"
        };
        builder.setMaze(maze).withLeftoverOutPaths({GraphBuilder::OutPath::North});
        graph_ = builder.buildGraph();
    }

    MazeGraph graph_{ 0 };
};

TEST_F(GraphAlgorithmsTest, IsReachableForNeighbor) {
    EXPECT_TRUE(reachable::isReachable(graph_, Location(0, 0), Location(0, 1)));
}

TEST_F(GraphAlgorithmsTest, IsReachableForDistanceOfTwo) {
    EXPECT_TRUE(reachable::isReachable(graph_, Location(1, 1), Location(0, 0)));
}

TEST_F(GraphAlgorithmsTest, IsReachableCornerToCorner) {
    EXPECT_TRUE(reachable::isReachable(graph_, Location(2, 0), Location(0, 2)));
}

TEST_F(GraphAlgorithmsTest, IsReachableForUnconnectedCorners) {
    EXPECT_FALSE(reachable::isReachable(graph_, Location(2, 2), Location(0, 0)));
}

TEST_F(GraphAlgorithmsTest, IsReachableForUnconnectedNeighbors) {
    EXPECT_FALSE(reachable::isReachable(graph_, Location(2, 1), Location(1, 1)));
}

TEST_F(GraphAlgorithmsTest, IsReachable_AfterOneShift_FindsInsertedNode) {
    graph_.shift(Location{1, 0}, 0);
    EXPECT_TRUE(reachable::isReachable(graph_, Location(0, 0), Location(1, 0)));
}