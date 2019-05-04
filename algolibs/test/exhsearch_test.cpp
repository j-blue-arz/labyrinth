#include "libexhsearch/exhsearch.h"
#include "libexhsearch/graph_algorithms.h"
#include "graphbuilder/text_graph_builder.h"


#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include <set>

using namespace graph;

class ExhaustiveSearchTest : public ::testing::Test {
protected:

    static const std::vector<std::string> big_component_maze;
    static const std::vector<std::string> difficult_maze;

    void SetUp() override {
        buildGraph();
    }

    void buildGraph(const std::vector<std::string> & maze = big_component_maze, 
        const std::initializer_list<GraphBuilder::OutPath> leftover_out_paths = {GraphBuilder::OutPath::North, GraphBuilder::OutPath::East}) {
        TextGraphBuilder builder{};

        graph_ = builder.setMaze(maze)
            .withStandardShiftLocations()
            .withLeftoverOutPaths(leftover_out_paths)
            .buildGraph();
    }

    MazeGraph graph_{0};
};

const std::vector<std::string> ExhaustiveSearchTest::big_component_maze = {
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

const std::vector<std::string> ExhaustiveSearchTest::difficult_maze = {
    "###|#.#|###|###|#.#|###|###|",
    "#..|#..|...|#..|#..|#..|..#|",
    "#.#|###|#.#|#.#|###|#.#|#.#|",
    "---------------------------|",
    "#.#|#.#|#.#|###|#.#|#.#|###|",
    "#..|..#|..#|...|#..|#.#|...|",
    "###|###|#.#|###|###|#.#|###|",
    "---------------------------|",
    "#.#|###|#.#|#.#|###|###|#.#|",
    "#..|#..|#..|#.#|...|...|..#|",
    "#.#|#.#|#.#|#.#|#.#|###|#.#|",
    "---------------------------|",
    "###|#.#|###|#.#|###|###|###|",
    "...|..#|#..|#.#|#..|...|...|",
    "###|#.#|#.#|#.#|#.#|###|###|",
    "---------------------------|",
    "#.#|#.#|#.#|#.#|#.#|###|#.#|",
    "#..|#..|#..|#.#|..#|...|...|",
    "#.#|###|#.#|#.#|#.#|###|###|",
    "---------------------------|",
    "###|#.#|#.#|#.#|#.#|#.#|#.#|",
    "..#|#..|#..|...|#.#|#..|..#|",
    "#.#|###|#.#|###|#.#|#.#|#.#|",
    "---------------------------|",
    "#.#|###|###|###|#.#|#.#|#.#|",
    "#..|...|#..|...|#.#|...|..#|",
    "###|###|#.#|###|#.#|###|###|",
    "---------------------------*"
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
        if(!reachable::isReachable(graph, player_location, action.move_location)) {
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

void performTest(MazeGraph & graph, const Location & player_location, MazeGraph::NodeId objective_id, size_t expected_depth) {
    algorithm::ExhaustiveSearch search(graph);

    auto actions = search.findBestActions(player_location, objective_id);

    ASSERT_THAT(actions, testing::SizeIs(testing::Ge(1)));
    EXPECT_TRUE(isCorrectPlayerActionSequence(graph, player_location, actions));
    EXPECT_TRUE(playerActionsReachObjective(graph, player_location, objective_id, actions));
    EXPECT_THAT(actions, testing::SizeIs(expected_depth));
}

TEST_F(ExhaustiveSearchTest, d1_direct_path) {
    SCOPED_TRACE("d1_direct_path");
    auto objective_id = graph_.getNodeId(Location(6, 2));
    Location player_location{3, 3};
    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, withObjectiveLeftover_shouldReturnOneCorrectMove) {
    SCOPED_TRACE("withObjectiveLeftover_shouldReturnOneCorrectMove");
    auto objective_id = graph_.getLeftoverNodeId();
    Location player_location{0, 0};
    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, requiresRotatingLeftover_shouldReturnOneCorrectMove) {
    SCOPED_TRACE("requiresRotatingLeftover_shouldReturnOneCorrectMove");
    graph_.setLeftoverOutPaths("NW");
    auto objective_id = graph_.getNodeId(Location{4, 0});
    Location player_location{0, 0};
    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, d2_two_shifts) {
    SCOPED_TRACE("d2_two_shifts");
    auto objective_id = graph_.getNodeId(Location(6, 6));
    Location player_location{3, 3};
    performTest(graph_, player_location, objective_id, 2);
}

TEST_F(ExhaustiveSearchTest, d2_long_running) {
    SCOPED_TRACE("d2_long_running");
    graph_.setLeftoverOutPaths("NES");
    auto objective_id = graph_.getNodeId(Location(3, 2));
    Location player_location{0, 5};

    performTest(graph_, player_location, objective_id, 2);
}

TEST_F(ExhaustiveSearchTest, d2_self_push_out) {
    SCOPED_TRACE("d2_self_push_out");
    buildGraph(difficult_maze, {GraphBuilder::OutPath::North, GraphBuilder::OutPath::East});
    auto objective_id = graph_.getNodeId(Location(6, 6));
    Location player_location{0, 6};

    performTest(graph_, player_location, objective_id, 2);
}

TEST_F(ExhaustiveSearchTest, d3_obj_push_out) {
    SCOPED_TRACE("d3_obj_push_out");
    buildGraph(difficult_maze, {GraphBuilder::OutPath::North, GraphBuilder::OutPath::East});
    auto objective_id = graph_.getNodeId(Location(5, 1));
    Location player_location{0, 6};

    performTest(graph_, player_location, objective_id, 3);
}

TEST_F(ExhaustiveSearchTest, d3_long_running) {
    SCOPED_TRACE("d3_long_running");
    buildGraph(difficult_maze, {GraphBuilder::OutPath::North, GraphBuilder::OutPath::South});
    auto objective_id = graph_.getNodeId(Location(1, 1));
    Location player_location{4, 6};

    performTest(graph_, player_location, objective_id, 3);
}
