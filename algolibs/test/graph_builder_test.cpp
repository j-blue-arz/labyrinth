#include "libexhsearch/graph_builder.h"

#include "gtest/gtest.h"

using namespace graph;

class GraphBuilderTest : public ::testing::Test {
protected:

	void SetUp() override {
		GraphBuilder builder{};
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
		graph_ = builder.buildGraphFromText(maze);
	}

	StaticGraph graph_{0};
};

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectExtent) {
	EXPECT_EQ(graph_.getNumberOfNodes(), 9);
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt0_0) {
	auto neighbors = graph_.neighbors(Location(0, 0));
	EXPECT_EQ(neighbors.size(), 2);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(0, 1)) != neighbors.end());
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(1, 0)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt0_1) {
	auto neighbors = graph_.neighbors(Location(0, 1));
	EXPECT_EQ(neighbors.size(), 2);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(0, 0)) != neighbors.end());
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(0, 2)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt0_2) {
	auto neighbors = graph_.neighbors(Location(0, 2));
	EXPECT_EQ(neighbors.size(), 1);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(0, 1)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt1_0) {
	auto neighbors = graph_.neighbors(Location(1, 0));
	EXPECT_EQ(neighbors.size(), 3);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(0, 0)) != neighbors.end());
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(1, 1)) != neighbors.end());
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(2, 0)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt1_1) {
	auto neighbors = graph_.neighbors(Location(1, 1));
	EXPECT_EQ(neighbors.size(), 2);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(1, 0)) != neighbors.end());
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(1, 2)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt1_2) {
	auto neighbors = graph_.neighbors(Location(1, 2));
	EXPECT_EQ(neighbors.size(), 1);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(1, 1)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt2_0) {
	auto neighbors = graph_.neighbors(Location(2, 0));
	EXPECT_EQ(neighbors.size(), 1);
	EXPECT_TRUE(std::find(neighbors.begin(), neighbors.end(), Location(1, 0)) != neighbors.end());
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt2_1) {
	auto neighbors = graph_.neighbors(Location(2, 1));
	EXPECT_EQ(neighbors.size(), 0);
}

TEST_F(GraphBuilderTest, BuildGraphFromTextHasCorrectNodeAt2_2) {
	auto neighbors = graph_.neighbors(Location(2, 2));
	EXPECT_EQ(neighbors.size(), 0);
}