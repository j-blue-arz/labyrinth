#include "libexhsearch/exhsearch.h"
#include "libexhsearch/graph_algorithms.h"
#include "libexhsearch/maze_graph.h"
#include "graphbuilder/text_graph_builder.h"
#include "mazes.h"
#include "util.h"


#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include <set>

using namespace labyrinth;

class ExhaustiveSearchTest : public ::testing::Test {
protected:

    void SetUp() override {
        buildGraph();
    }

    void buildGraph(const std::vector<std::string> & maze = mazes::big_component_maze,
                    const std::vector<OutPaths> leftover_out_paths = {OutPaths::North, OutPaths::East}) {
        TextGraphBuilder builder{};

        graph_ = builder.setMaze(maze)
            .withStandardShiftLocations()
            .buildGraph();
        graph_.setLeftoverOutPaths(getBitmask(leftover_out_paths));
    }

    MazeGraph graph_{0};
};

::testing::AssertionResult isCorrectPlayerActionSequence(const std::vector<labyrinth::exhsearch::PlayerAction> & actions,
                                                         const labyrinth::MazeGraph & original_graph,
                                                         const Location & player_start_location) {
    std::set<labyrinth::RotationDegreeType> valid_shift_rotations = {0, 90, 180, 270};
    labyrinth::MazeGraph graph{original_graph};
    auto shift_locations = graph.getShiftLocations();
    auto player_location_id = graph.getNode(player_start_location).node_id;
    for (const auto & action : actions) {
        if (std::find(shift_locations.begin(), shift_locations.end(), action.shift.location) == shift_locations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift location: " << action.shift.location;
        }
        if (valid_shift_rotations.find(action.shift.rotation) == valid_shift_rotations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift rotation: " << action.shift.rotation;
        }
        graph.shift(action.shift.location, action.shift.rotation);
        auto player_location = graph.getLocation(player_location_id, action.shift.location);
        if (!reachable::isReachable(graph, player_location, action.move_location)) {
            return ::testing::AssertionFailure() << "Invalid move: " << action.move_location << " is not reachable from " << player_location;
        }
        player_location_id = graph.getNode(action.move_location).node_id;
    }
    return ::testing::AssertionSuccess();
}

bool isOpposing(const Location & location1, const Location & location2, size_t extent) {
    auto border{static_cast<Location::IndexType>(extent - 1)};
    auto isOpposingIndex = [border](Location::IndexType index1, Location::IndexType index2) {
        return std::set<Location::IndexType>{index1, index2} == std::set<Location::IndexType>{0, border};
    };
    if (location1.getColumn() == location2.getColumn()) {
        return isOpposingIndex(location1.getRow(), location2.getRow());
    }
    else if (location1.getRow() == location2.getRow()) {
        return isOpposingIndex(location1.getColumn(), location2.getColumn());
    }
    return false;
}

::testing::AssertionResult respectPushbackRule(const std::vector<labyrinth::exhsearch::PlayerAction> & actions,
                                               size_t extent,
                                               const Location & previous_shift_location) {
    std::vector<Location> shift_locations;
    shift_locations.push_back(previous_shift_location);
    std::transform(actions.begin(), actions.end(), std::back_inserter(shift_locations), [](auto action) { return action.shift.location; });
    auto adjacent_opposing_locations = std::adjacent_find(shift_locations.begin(), shift_locations.end(),
                                                          [extent](auto loc1, auto loc2) {
        return isOpposing(loc1, loc2, extent);
    });
    if (adjacent_opposing_locations != shift_locations.end()) {
        return ::testing::AssertionFailure()
            << "Shift locations " << *adjacent_opposing_locations << " and " << *(adjacent_opposing_locations + 1) << " violate no-pushback rule.";
    }
    return ::testing::AssertionSuccess();


}

::testing::AssertionResult playerActionsReachObjective(const std::vector<labyrinth::exhsearch::PlayerAction> & actions,
                                                       labyrinth::MazeGraph & original_graph,
                                                       const Location & player_start_location,
                                                       labyrinth::NodeId objective_id) {

    labyrinth::MazeGraph graph{original_graph};
    auto player_location_id = graph.getNode(player_start_location).node_id;
    for (const auto & action : actions) {
        graph.shift(action.shift.location, action.shift.rotation);
        player_location_id = graph.getNode(action.move_location).node_id;
    }
    if (player_location_id == objective_id) {
        return ::testing::AssertionSuccess();
    }
    else {
        auto move_location = graph.getLocation(player_location_id, Location(-1, -1));
        auto objective_location = graph.getLocation(objective_id, Location(-1, -1));
        return ::testing::AssertionFailure() << "Last move to " << move_location << " does not reach objective at " << objective_location;
    }
}

void performTest(MazeGraph & graph,
                 const Location & player_location,
                 NodeId objective_id,
                 size_t expected_depth,
                 const Location & previous_shift = Location{-1, -1}) {

    auto actions = labyrinth::exhsearch::findBestActions(graph, player_location, objective_id, previous_shift);

    ASSERT_THAT(actions, testing::SizeIs(testing::Ge(1)));
    EXPECT_TRUE(isCorrectPlayerActionSequence(actions, graph, player_location));
    EXPECT_TRUE(playerActionsReachObjective(actions, graph, player_location, objective_id));
    EXPECT_TRUE(respectPushbackRule(actions, graph.getExtent(), previous_shift));
    EXPECT_THAT(actions, testing::SizeIs(expected_depth));
}

TEST_F(ExhaustiveSearchTest, d1_direct_path) {
    SCOPED_TRACE("d1_direct_path");
    auto objective_id = graph_.getNode(Location(6, 2)).node_id;
    Location player_location{3, 3};
    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, withObjectiveLeftover_shouldReturnOneCorrectMove) {
    SCOPED_TRACE("withObjectiveLeftover_shouldReturnOneCorrectMove");
    auto objective_id = graph_.getLeftover().node_id;
    Location player_location{6, 2};
    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, requiresRotatingLeftover_shouldReturnOneCorrectMove) {
    SCOPED_TRACE("requiresRotatingLeftover_shouldReturnOneCorrectMove");
    graph_.setLeftoverOutPaths(getBitmask("NW"));
    auto objective_id = graph_.getNode(Location{4, 0}).node_id;
    Location player_location{0, 0};
    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, d2_two_shifts) {
    SCOPED_TRACE("d2_two_shifts");
    auto objective_id = graph_.getNode(Location{6, 6}).node_id;
    Location player_location{3, 3};
    performTest(graph_, player_location, objective_id, 2);
}

TEST_F(ExhaustiveSearchTest, d2_long_running) {
    SCOPED_TRACE("d2_long_running");
    graph_.setLeftoverOutPaths(getBitmask("NES"));
    auto objective_id = graph_.getNode(Location{3, 2}).node_id;
    Location player_location{0, 5};

    performTest(graph_, player_location, objective_id, 2);
}

TEST_F(ExhaustiveSearchTest, d2_self_push_out) {
    SCOPED_TRACE("d2_self_push_out");
    buildGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    auto objective_id = graph_.getNode(Location{6, 6}).node_id;
    Location player_location{0, 6};

    performTest(graph_, player_location, objective_id, 2);
}

TEST_F(ExhaustiveSearchTest, d3_obj_push_out) {
    SCOPED_TRACE("d3_obj_push_out");
    buildGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    auto objective_id = graph_.getNode(Location{5, 1}).node_id;
    Location player_location{0, 6};

    performTest(graph_, player_location, objective_id, 3);
}

TEST_F(ExhaustiveSearchTest, d3_long_running) {
    SCOPED_TRACE("d3_long_running");
    buildGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::South});
    auto objective_id = graph_.getNode(Location{1, 1}).node_id;
    Location player_location{4, 6};

    performTest(graph_, player_location, objective_id, 3);
}

TEST_F(ExhaustiveSearchTest, withResultOfLengthTwoViolatingPushbackRule_shouldReturnThreeMoves) {
    SCOPED_TRACE("withResultOfLengthTwoViolatingPushbackRule_shouldReturnThreeMoves");
    buildGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::South});
    auto objective_id = graph_.getNode(Location{6, 6}).node_id;
    Location player_location{0, 4};

    performTest(graph_, player_location, objective_id, 3);
}

TEST_F(ExhaustiveSearchTest, withResultOfLengthOneViolatingGivenPreviousShift_shouldReturnTwoMoves) {
    SCOPED_TRACE("withResultOfLengthOneViolatingGivenPreviousShift_shouldReturnTwoMoves");
    buildGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::South});
    auto objective_id = graph_.getLeftover().node_id;
    Location player_location{6, 2};

    performTest(graph_, player_location, objective_id, 1);
    performTest(graph_, player_location, objective_id, 2, Location{0, 3});
}

TEST_F(ExhaustiveSearchTest, d4_generated_86s) { 
    SCOPED_TRACE("d4_generated_depth4");
    buildGraph(mazes::exh_depth_4_maze, {OutPaths::North, OutPaths::East});
    auto objective_id = graph_.getNode(Location{6, 7}).node_id;
    Location player_location{4, 2};

    performTest(graph_, player_location, objective_id, 4);
}

TEST_F(ExhaustiveSearchTest, withThreeByThree_shouldReturnOneMove) {
    SCOPED_TRACE("withThreeByThree_shouldReturnOneMove");
    buildGraph(mazes::three_by_three, { OutPaths::North, OutPaths::East });
    auto objective_id = graph_.getNode(Location{0, 2}).node_id;
    Location player_location{0, 0};

    performTest(graph_, player_location, objective_id, 1);
}
