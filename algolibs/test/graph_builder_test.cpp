#include "graphbuilder/text_graph_builder.h"

#include "util.h"

#include "gtest/gtest.h"
#include <set>

using namespace labyrinth;
using namespace labyrinth::testutils;

class GraphBuilderFromTextTest : public ::testing::Test {
protected:
    void SetUp() override {
        TextGraphBuilder builder{};
        const std::vector<std::string> maze{"###|#.#|#.#|",
                                            "#..|...|..#|",
                                            "#.#|#.#|###|",
                                            "------------",
                                            "#.#|###|###|",
                                            "#..|...|...|",
                                            "#.#|###|###|",
                                            "------------",
                                            "#.#|#.#|###|",
                                            "#..|#.#|..#|",
                                            "###|#.#|#.#|",
                                            "------------"};
        builder.setMaze(maze);
        builder.withLeftoverOutPaths("NES");
        graph_ = builder.buildGraph();
    }

    MazeGraph graph_{0};
};

TEST_F(GraphBuilderFromTextTest, getNumberOfNodes_returnsCorrectValue) {
    EXPECT_EQ(graph_.getNumberOfNodes(), 10);
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow0Column0_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 0}, {Location{0, 1}, Location{1, 0}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow0Column1_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 1}, {Location{0, 0}, Location{0, 2}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow0Column2_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{0, 2}, {Location{0, 1}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow1Column0_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 0}, {Location{0, 0}, Location{1, 1}, Location{2, 0}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow1Column1_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 1}, {Location{1, 0}, Location{1, 2}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow1Column2_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{1, 2}, {Location{1, 1}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow2Column0_returnsCorrectNeighbors) {
    EXPECT_TRUE(hasNeighbors(graph_, Location{2, 0}, {Location{1, 0}}));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow2Column1_returnsNoNeighbors) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location{2, 1}, 0));
}

TEST_F(GraphBuilderFromTextTest, neighbors_withRow2Column2_returnsNoNeighbors) {
    EXPECT_TRUE(assertNumNeighbors(graph_, Location{2, 2}, 0));
}

TEST_F(GraphBuilderFromTextTest, leftover_outPaths_areCorrect) {
    auto leftover_node = graph_.getLeftover();
    EXPECT_EQ(leftover_node.rotation, 0);
    EXPECT_TRUE(hasOutPath(leftover_node, OutPaths::North));
    EXPECT_TRUE(hasOutPath(leftover_node, OutPaths::East));
    EXPECT_TRUE(hasOutPath(leftover_node, OutPaths::South));
    EXPECT_FALSE(hasOutPath(leftover_node, OutPaths::West));
}
