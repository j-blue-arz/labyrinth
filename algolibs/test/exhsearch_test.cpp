#include "libexhsearch/exhsearch.h"
#include "libexhsearch/graph_algorithms.h"
#include "graphbuilder/text_graph_builder.h"


#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include <set>

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

::testing::AssertionResult isCorrectPlayerActionSequence(const graph::MazeGraph & original_graph, 
    const Location & player_location, const std::vector<algorithm::ExhaustiveSearch::PlayerAction> & actions) {
    std::set<graph::MazeGraph::RotationDegreeType> valid_shift_rotations = {0, 90, 180, 270};
    graph::MazeGraph graph{original_graph};
    auto shift_locations = graph.getShiftLocations();
    auto player_location_id = graph.getNodeId(player_location);
    for(auto action : actions) {
        if(std::find(shift_locations.begin(), shift_locations.end(), action.shift.location) == shift_locations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift location: " << action.shift.location;
        }
        if(valid_shift_rotations.find(action.shift.rotation) == valid_shift_rotations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift rotation: " << action.shift.rotation;
        }
        graph.shift(action.shift.location, action.shift.rotation);
        auto player_location = graph.getLocation(player_location_id, action.shift.location);
        if(!algorithm::isReachable(graph, player_location, action.move_location)) {
            return ::testing::AssertionFailure() << "Invalid move: " << action.move_location << " is not reachable from " << player_location;
        }
        player_location_id = graph.getNodeId(action.move_location);
    }
    return ::testing::AssertionSuccess();
}

::testing::AssertionResult playerActionsReachObjective(graph::MazeGraph & original_graph,
    const Location & player_location, graph::MazeGraph::NodeId objective_id, const std::vector<algorithm::ExhaustiveSearch::PlayerAction> & actions) {
    graph::MazeGraph graph{original_graph};
    auto player_location_id = graph.getNodeId(player_location);
    for(auto action : actions) {
        graph.shift(action.shift.location, action.shift.rotation);
        auto player_location = graph.getLocation(player_location_id, action.shift.location);
        player_location_id = graph.getNodeId(action.move_location);
    }
    if(player_location_id == objective_id) {
        return ::testing::AssertionSuccess();
    }
    else {
        auto move_location = graph.getLocation(player_location_id, Location(-1, -1));
        auto objective_location = graph.getLocation(objective_id, Location(-1, -1));
        return ::testing::AssertionFailure() << "Last move to " << move_location << " does not reach objective at " << objective_location;
    }
}

TEST_F(ExhaustiveSearchTest, withDirectPathToObjective_shouldReachInOneMove) {
    algorithm::ExhaustiveSearch search(graph_);
    auto objective_id = graph_.getNodeId(Location(6, 2));
    Location player_location{3, 3};

    auto actions = search.findBestActions(player_location, objective_id);

    ASSERT_THAT(actions, testing::SizeIs(1));
    EXPECT_TRUE(isCorrectPlayerActionSequence(graph_, player_location, actions));
    EXPECT_TRUE(playerActionsReachObjective(graph_, player_location, objective_id, actions));
}

TEST_F(ExhaustiveSearchTest, withObjectiveLeftover_shouldReachInOneMove) {
    algorithm::ExhaustiveSearch search(graph_);
    auto objective_id = graph_.getLeftoverNodeId();
    Location player_location{0, 0};

    auto actions = search.findBestActions(player_location, objective_id);

    ASSERT_THAT(actions, testing::SizeIs(1));
    EXPECT_TRUE(isCorrectPlayerActionSequence(graph_, player_location, actions));
    EXPECT_TRUE(playerActionsReachObjective(graph_, player_location, objective_id, actions));
}

TEST_F(ExhaustiveSearchTest, requiresRotatingLeftover_shouldReachInOneMove) {
    graph_.setLeftoverOutPaths("NW");
    algorithm::ExhaustiveSearch search(graph_);
    Location objective_location{4, 0};
    auto objective_id = graph_.getNodeId(objective_location);

    auto actions = search.findBestActions(Location(0, 0), objective_id);

    ASSERT_THAT(actions, testing::SizeIs(1));
    auto action = actions[0];
    EXPECT_EQ(action.shift.location, Location(1, 0));
    EXPECT_EQ(action.shift.rotation, 90);
    EXPECT_EQ(action.move_location, objective_location);
}

