#include "exhsearch_test.h"
#include "graphbuilder/text_graph_builder.h"
#include "solvers/exhsearch.h"
#include "solvers/graph_algorithms.h"
#include "solvers/maze_graph.h"
#include "util.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include <chrono>
#include <future>
#include <set>
#include <thread>

using namespace labyrinth;
using namespace labyrinth::testutils;

namespace exh = labyrinth::solvers::exhsearch;

class ExhaustiveSearchTest : public ::testing::Test {
protected:
    void SetUp() override { buildGraph(); }

    void buildGraph(const std::vector<std::string>& maze = mazes::big_component_maze,
                    const std::vector<OutPaths>& leftover_out_paths = {OutPaths::North, OutPaths::East}) {
        TextGraphBuilder builder{};

        graph_ = builder.setMaze(maze).withStandardShiftLocations().buildGraph();
        graph_.setLeftoverOutPaths(getBitmask(leftover_out_paths));
    }

    MazeGraph graph_{0};
};

::testing::AssertionResult isCorrectPlayerActionSequence(const std::vector<solvers::PlayerAction>& actions,
                                                         const MazeGraph& original_graph,
                                                         const Location& player_start_location) {
    MazeGraph graph{original_graph};
    auto shift_locations = graph.getShiftLocations();
    auto player_location = player_start_location;
    for (const auto& action : actions) {
        if (std::find(shift_locations.begin(), shift_locations.end(), action.shift.location) == shift_locations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift location: " << action.shift.location;
        }
        graph.shift(action.shift.location, action.shift.rotation);
        player_location = translateLocationByShift(player_location, action.shift.location, graph.getExtent());
        if (!reachable::isReachable(graph, player_location, action.move_location)) {
            return ::testing::AssertionFailure()
                   << "Invalid move: " << action.move_location << " is not reachable from " << player_location;
        }
        player_location = action.move_location;
    }
    return ::testing::AssertionSuccess();
}

bool isOpposing(const Location& location1, const Location& location2, size_t extent) {
    auto border{static_cast<Location::IndexType>(extent - 1)};
    auto isOpposingIndex = [border](Location::IndexType index1, Location::IndexType index2) {
        return std::set<Location::IndexType>{index1, index2} == std::set<Location::IndexType>{0, border};
    };
    if (location1.getColumn() == location2.getColumn()) {
        return isOpposingIndex(location1.getRow(), location2.getRow());
    } else if (location1.getRow() == location2.getRow()) {
        return isOpposingIndex(location1.getColumn(), location2.getColumn());
    }
    return false;
}

::testing::AssertionResult respectPushbackRule(const std::vector<solvers::PlayerAction>& actions,
                                               size_t extent,
                                               const Location& previous_shift_location) {
    std::vector<Location> shift_locations;
    shift_locations.push_back(previous_shift_location);
    std::transform(actions.begin(), actions.end(), std::back_inserter(shift_locations), [](auto action) {
        return action.shift.location;
    });
    auto adjacent_opposing_locations =
        std::adjacent_find(shift_locations.begin(), shift_locations.end(), [extent](auto loc1, auto loc2) {
            return isOpposing(loc1, loc2, extent);
        });
    if (adjacent_opposing_locations != shift_locations.end()) {
        return ::testing::AssertionFailure() << "Shift locations " << *adjacent_opposing_locations << " and "
                                             << *(adjacent_opposing_locations + 1) << " violate no-pushback rule.";
    }
    return ::testing::AssertionSuccess();
}

::testing::AssertionResult playerActionsReachObjective(const std::vector<solvers::PlayerAction>& actions,
                                                       MazeGraph& original_graph,
                                                       const Location& player_start_location,
                                                       NodeId objective_id) {

    MazeGraph graph{original_graph};
    auto player_location_id = graph.getNode(player_start_location).node_id;
    for (const auto& action : actions) {
        graph.shift(action.shift.location, action.shift.rotation);
        player_location_id = graph.getNode(action.move_location).node_id;
    }
    if (player_location_id == objective_id) {
        return ::testing::AssertionSuccess();
    } else {
        auto move_location = graph.getLocation(player_location_id, Location(-1, -1));
        auto objective_location = graph.getLocation(objective_id, Location(-1, -1));
        return ::testing::AssertionFailure()
               << "Last move to " << move_location << " does not reach objective at " << objective_location;
    }
}

void performTest(MazeGraph& graph,
                 const Location& player_location,
                 NodeId objective_id,
                 size_t expected_depth,
                 const Location& previous_shift = Location{-1, -1}) {
    solvers::SolverInstance solver_instance{graph, player_location, Location{-1, -1}, objective_id, previous_shift};
    auto actions = exh::findBestActions(solver_instance);

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
    buildGraph(mazes::three_by_three, {OutPaths::North, OutPaths::East});
    auto objective_id = graph_.getNode(Location{0, 2}).node_id;
    Location player_location{0, 0};

    performTest(graph_, player_location, objective_id, 1);
}

TEST_F(ExhaustiveSearchTest, depth4Instance_whenAborted_shouldReturnQuicklyWithoutResult) {
    SCOPED_TRACE("depth4Instance_whenAborted_shouldReturnQuicklyWithoutResult");
    using namespace std::chrono_literals;
    buildGraph(mazes::exh_depth_4_maze, {OutPaths::North, OutPaths::East});
    auto objective_id = graph_.getNode(Location{6, 7}).node_id;
    Location player_location{4, 2};
    Location previous_shift{-1, -1};
    solvers::SolverInstance solver_instance{graph_, player_location, Location{-1, -1}, objective_id, previous_shift};

    const auto start = std::chrono::steady_clock::now();
    auto future_actions = std::async(std::launch::async, exh::findBestActions, solver_instance);
    std::this_thread::sleep_for(1ms);
    exh::abortComputation();
    auto actions = future_actions.get();
    const auto stop = std::chrono::steady_clock::now();
    const std::chrono::duration<double> duration = std::chrono::duration<double>(stop - start);

    ASSERT_THAT(duration.count(), testing::Lt(0.01));
    ASSERT_THAT(actions, testing::IsEmpty());
}

TEST_F(ExhaustiveSearchTest, depth4Instance_whenAborted_runsFineAfterwards) {
    SCOPED_TRACE("depth4Instance_whenAborted_runsFineAfterwards");
    buildGraph(mazes::exh_depth_4_maze, {OutPaths::North, OutPaths::East});
    auto objective_id = graph_.getNode(Location{6, 7}).node_id;
    Location player_location{4, 2};
    Location previous_shift{-1, -1};
    solvers::SolverInstance solver_instance{graph_, player_location, Location{-1, -1}, objective_id, previous_shift};

    auto future_actions = std::async(exh::findBestActions, solver_instance);
    exh::abortComputation();
    auto actions = future_actions.get();

    performTest(graph_, player_location, objective_id, 4);
}
