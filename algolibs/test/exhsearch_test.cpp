#include "libexhsearch/exhsearch.h"
#include "libexhsearch/graph_algorithms.h"
#include "graphbuilder/text_graph_builder.h"


#include "gtest/gtest.h"

using namespace graph;

class ExhaustiveSearchTest : public ::testing::Test {
protected:

    void SetUp() override {
        TextGraphBuilder builder{};
        const std::vector<std::string> maze{
            "###|#.#|#.#|###|#.#|#.#|###|",
            "#..|#..|...|...|#..|..#|..#|",
            "#.#|###|###|#.#|###|###|#.#|",
            "---------------------------|",
            "###|###|#.#|#.#|#.#|#.#|#.#|",
            "...|...|#.#|#..|#.#|...|..#|",
            "#.#|#.#|#.#|###|#.#|###|#.#|",
            "---------------------------|",
            "#.#|#.#|#.#|#.#|#.#|#.#|#.#|",
            "#..|#..|..#|#..|..#|#.#|..#|",
            "#.#|#.#|#.#|#.#|#.#|#.#|#.#|",
            "---------------------------|",
            "#.#|#.#|#.#|###|#.#|###|###|",
            "..#|..#|#..|...|...|...|..#|",
            "###|#.#|###|#.#|###|#.#|#.#|",
            "---------------------------|",
            "###|#.#|###|#.#|###|#.#|###|",
            "#..|..#|#..|#.#|...|#..|...|",
            "#.#|###|#.#|#.#|#.#|###|###|",
            "---------------------------|",
            "###|#.#|###|#.#|#.#|#.#|#.#|",
            "..#|#..|...|...|#.#|#..|..#|",
            "#.#|#.#|###|###|#.#|#.#|#.#|",
            "---------------------------|",
            "#.#|#.#|###|###|#.#|#.#|#.#|",
            "#..|...|...|...|#.#|...|..#|",
            "###|###|#.#|###|#.#|###|###|",
            "---------------------------*"
        };
        graph_ = builder.setMaze(maze)
            .withStandardShiftLocations()
            .withLeftoverOutPaths({GraphBuilder::OutPath::North, GraphBuilder::OutPath::East})
            .buildGraph();
    }

    MazeGraph graph_{0};

};

TEST_F(ExhaustiveSearchTest, withDirectPathToObjective_shouldReachInOneMove) {
    algorithm::ExhaustiveSearch search(graph_);
    auto objective_id = graph_.getNodeId(Location(6, 2));
    auto player_id = graph_.getNodeId(Location(3, 3));

    auto move = search.findBestMove(Location(3, 3), Location(6, 2));

    graph_.shift(move.first.shift_location, move.first.rotation);
    auto objective_location = graph_.getLocation(objective_id, Location(-1, -1));
    auto player_location = graph_.getLocation(player_id, move.first.shift_location);
    auto move_location = move.second;
    EXPECT_TRUE(algorithm::isReachable(graph_, player_location, move_location)) 
        << "Invalid move: " << move_location << " is not reachable from " << player_location;
    EXPECT_EQ(move_location, objective_location) 
        << "Last move to " << move_location << " does not reach objective at " << objective_location;
}

