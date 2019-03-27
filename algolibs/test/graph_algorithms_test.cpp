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
        builder.setMaze(maze);
        graph_ = builder.buildGraph();
    }

    StaticGraph graph_{ 0 };
};

TEST_F(GraphAlgorithmsTest, IsReachableForNeighbor) {
    EXPECT_TRUE(algorithm::isReachable(graph_, Location(0, 0), Location(0, 1)));
}

TEST_F(GraphAlgorithmsTest, IsReachableForDistanceOfTwo) {
    EXPECT_TRUE(algorithm::isReachable(graph_, Location(1, 1), Location(0, 0)));
}

TEST_F(GraphAlgorithmsTest, IsReachableCornerToCorner) {
    EXPECT_TRUE(algorithm::isReachable(graph_, Location(2, 0), Location(0, 2)));
}

TEST_F(GraphAlgorithmsTest, IsReachableForUnconnectedCorners) {
    EXPECT_FALSE(algorithm::isReachable(graph_, Location(2, 2), Location(0, 0)));
}

TEST_F(GraphAlgorithmsTest, IsReachableForUnconnectedNeighbors) {
    EXPECT_FALSE(algorithm::isReachable(graph_, Location(2, 1), Location(1, 1)));
}