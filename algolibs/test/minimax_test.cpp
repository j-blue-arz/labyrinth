/** Tests for the minimax algorithm.
 * There are currently four types of test cases:
 * - reachableWithOneAction
 * - cannotPreventOpponent
 * - prevent_opponent_then_reach
 * - prevent_opponent_then_cannot_reach
 */
#include "minimax_test.h"
#include "graphbuilder/text_graph_builder.h"
#include "solvers/graph_algorithms.h"
#include "solvers/maze_graph.h"
#include "solvers/minimax.h"
#include "util.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include <chrono>
#include <functional>
#include <future>
#include <thread>

using namespace labyrinth;
using namespace labyrinth::testutils;
using namespace std::chrono_literals;

class MinimaxTest : public ::testing::Test {
private:
    using duration_clock = std::chrono::steady_clock;

protected:
    void givenGraph(const std::vector<std::string>& maze, const std::vector<OutPaths>& leftover_out_paths) {
        TextGraphBuilder builder{};

        graph = builder.setMaze(maze).withStandardShiftLocations().buildGraph();
        graph.setLeftoverOutPaths(getBitmask(leftover_out_paths));
    }

    void givenPlayerLocations(const Location& player_location, const Location& opponent_location) {
        this->player_location = player_location;
        this->opponent_location = opponent_location;
    }

    void givenObjectiveAt(const Location& location) { objective_id = graph.getNode(location).node_id; }

    void givenPreviousShift(const Location& location) { previous_shift_location = location; }

    void givenFindBestActionAsync() {
        start = duration_clock::now();
        future_action = std::async(std::launch::async,
                                   minimax::iterateMinimax,
                                   graph,
                                   player_location,
                                   opponent_location,
                                   objective_id,
                                   previous_shift_location);
    }

    void givenSleepFor(duration_clock::duration duration) { std::this_thread::sleep_for(duration); }

    void whenFindBestAction() {
        result =
            minimax::iterateMinimax(graph, player_location, opponent_location, objective_id, previous_shift_location);
    }

    void whenFindBestActionWithDepth(size_t depth) {
        minimax_result = minimax::findBestAction(
            graph, player_location, opponent_location, objective_id, depth, previous_shift_location);
        result = minimax_result.player_action;
    }

    void whenComputationIsAborted() {
        minimax::abortComputation();
        result = future_action.get();
        stop = duration_clock::now();
    }

    void thenActionIsValid() { ASSERT_TRUE(isValidPlayerAction(result, graph, player_location)); }

    void thenActionReachesObjective() { ASSERT_TRUE(actionReachesObjective(result, graph, objective_id)); }

    void thenMinimaxResultShouldBeTerminal() { ASSERT_TRUE(minimax_result.evaluation.is_terminal); }

    void thenMinimaxResultShouldBeNegative() { ASSERT_LT(minimax_result.evaluation.value, 0); }

    void thenShiftLocationIs(const Location& location) { EXPECT_EQ(result.shift.location, location); }

    void thenShiftLocationIsNot(const Location& location) { EXPECT_NE(result.shift.location, location); }

    void thenMoveLocationIs(const Location& location) { EXPECT_EQ(result.move_location, location); }

    void thenComputationRanForLessThan(duration_clock::duration expected_duration) {
        const std::chrono::duration<double> duration = std::chrono::duration<double>(stop - start);
        ASSERT_THAT(duration, testing::Lt(expected_duration));
    }

    ::testing::AssertionResult isValidPlayerAction(const PlayerAction& action,
                                                   const labyrinth::MazeGraph& graph,
                                                   const Location& player_start_location) {
        std::set<labyrinth::RotationDegreeType> valid_shift_rotations = {0, 90, 180, 270};
        labyrinth::MazeGraph graph_copy{graph};
        auto shift_locations = graph_copy.getShiftLocations();
        auto player_location = player_start_location;
        if (std::find(shift_locations.begin(), shift_locations.end(), action.shift.location) == shift_locations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift location: " << action.shift.location;
        }
        if (valid_shift_rotations.find(action.shift.rotation) == valid_shift_rotations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift rotation: " << action.shift.rotation;
        }
        graph_copy.shift(action.shift.location, action.shift.rotation);
        player_location = translateLocationByShift(player_location, action.shift.location, graph_copy.getExtent());
        if (!reachable::isReachable(graph_copy, player_location, action.move_location)) {
            return ::testing::AssertionFailure()
                   << "Invalid move: " << action.move_location << " is not reachable from " << player_location;
        }
        return ::testing::AssertionSuccess();
    }

    ::testing::AssertionResult actionReachesObjective(const PlayerAction& action,
                                                      const labyrinth::MazeGraph& graph,
                                                      const labyrinth::NodeId objective_id) {
        labyrinth::MazeGraph graph_copy{graph};
        graph_copy.shift(action.shift.location, action.shift.rotation);
        if (graph_copy.getNode(action.move_location).node_id != objective_id) {
            auto objective_location = graph_copy.getLocation(objective_id, Location(-1, -1));
            return ::testing::AssertionFailure()
                   << "Move to " << action.move_location << " does not reach objective at " << objective_location;
        }

        return ::testing::AssertionSuccess();
    }

    MazeGraph graph{0};
    Location player_location;
    Location opponent_location;
    NodeId objective_id;
    Location previous_shift_location{-1, -1};
    size_t max_depth;

    PlayerAction result;
    minimax::MinimaxResult minimax_result{PlayerAction{}, 0};

    duration_clock::time_point start;
    duration_clock::time_point stop;
    std::future<labyrinth::PlayerAction> future_action;
};

TEST_F(MinimaxTest, findBestAction__reachableWithOneAction__returnsCorrectMove) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{0, 3});

    whenFindBestAction();

    thenActionIsValid();
    thenActionReachesObjective();
}

TEST_F(MinimaxTest, findBestAction__cannotPreventOpponent__terminatesWithValidAction) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::South});
    givenPlayerLocations(Location{3, 2}, Location{0, 4});
    givenObjectiveAt(Location{0, 5});

    whenFindBestAction();

    thenActionIsValid();
}

TEST_F(MinimaxTest, findBestAction__cannotPreventOpponent__isTerminalAndNegative) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::South});
    givenPlayerLocations(Location{3, 2}, Location{0, 4});
    givenObjectiveAt(Location{0, 5});

    whenFindBestActionWithDepth(2);

    thenMinimaxResultShouldBeTerminal();
    thenMinimaxResultShouldBeNegative();
}

TEST_F(MinimaxTest, findBestAction__opponentCannotPreventReachNextMove__returnsExpectedAction) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{6, 6}, Location{0, 0});
    givenObjectiveAt(Location{0, 6});

    whenFindBestAction();

    thenActionIsValid();
    thenShiftLocationIs(Location{0, 5});
    thenMoveLocationIs(Location{6, 5});
}

TEST_F(MinimaxTest, findBestAction__preventOpponent__returnsExpectedShift) {
    givenGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{2, 6});
    givenObjectiveAt(Location{0, 6});

    whenFindBestActionWithDepth(2);

    thenActionIsValid();
    thenShiftLocationIs(Location{1, 6});
}

TEST_F(MinimaxTest, findBestAction__bestActionViolatesPreviousShift__doesReturnDifferentShift) {
    givenGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{2, 6});
    givenObjectiveAt(Location{0, 6});
    givenPreviousShift(Location{1, 0});

    whenFindBestActionWithDepth(2);

    thenActionIsValid();
    thenShiftLocationIsNot(Location{1, 6});
}

TEST_F(MinimaxTest, findBestAction__whenAborted__shouldReturnQuicklyWithResult) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{6, 6}, Location{0, 0});
    givenObjectiveAt(Location{0, 6});
    givenFindBestActionAsync();
    givenSleepFor(20ms);

    whenComputationIsAborted();

    thenComputationRanForLessThan(30ms);
    thenActionIsValid();
}