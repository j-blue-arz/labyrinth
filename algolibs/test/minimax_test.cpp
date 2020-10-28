/**
 * Tests minimax implementation.
 *
 * Most testcases assert certain return values (or their properties) of a call to either
 * the iterative deepening or the fixed-depth minimax.
 * These testcases are parameterized over different Evaluators.
 *
 * One testcase asserts that the algorithm aborts quickly when asked to do so.
 */

#include "minimax_test.h"
#include "solvers/evaluators.h"
#include "solvers/exhsearch.h"
#include "solvers/graph_algorithms.h"
#include "solvers/minimax.h"
#include "solvers_test.h"
#include "util.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include <algorithm>
#include <chrono>
#include <functional>
#include <future>
#include <iterator>
#include <memory>
#include <thread>

using namespace labyrinth;
using namespace labyrinth::testutils;
using namespace std::chrono_literals;

namespace mm = labyrinth::solvers::minimax;

using EvaluatorFactory = std::unique_ptr<mm::Evaluator> (*)(solvers::SolverInstance);

std::unique_ptr<mm::Evaluator> createWinEvaluator(solvers::SolverInstance solver_instance) {
    return std::make_unique<mm::WinEvaluator>(solver_instance);
}

std::unique_ptr<mm::Evaluator> createWinAndReachedLocationsEvaluator(solvers::SolverInstance solver_instance) {
    using Factor = mm::MultiEvaluator::Factor;
    auto win_evaluator = std::make_unique<mm::WinEvaluator>(solver_instance);
    auto reachable_heuristic = std::make_unique<mm::ReachableLocationsHeuristic>();

    auto multi_evaluator = std::make_unique<mm::MultiEvaluator>();
    multi_evaluator->addEvaluator(std::move(win_evaluator), Factor{100});
    multi_evaluator->addEvaluator(std::move(reachable_heuristic), Factor{1});
    return multi_evaluator;
}

std::unique_ptr<mm::Evaluator> createWinAndObjectiveDistanceEvaluator(solvers::SolverInstance solver_instance) {
    using Factor = mm::MultiEvaluator::Factor;
    auto win_evaluator = std::make_unique<mm::WinEvaluator>(solver_instance);
    auto distance_heuristic = std::make_unique<mm::ObjectiveChessboardDistance>(solver_instance);

    auto multi_evaluator = std::make_unique<mm::MultiEvaluator>();
    multi_evaluator->addEvaluator(std::move(win_evaluator), Factor{100});
    multi_evaluator->addEvaluator(std::move(distance_heuristic), Factor{1});
    return multi_evaluator;
}

const std::vector<EvaluatorFactory> evaluator_factories = {&createWinEvaluator, &createWinAndReachedLocationsEvaluator, &createWinAndObjectiveDistanceEvaluator};
const std::vector<std::string> names = {"OnlyWin", "WinAndReachedLocations", "WinAndObjectiveDistance"};

class MinimaxTest : public SolversTest, public ::testing::WithParamInterface<size_t> {
private:
    using duration_clock = std::chrono::steady_clock;

protected:
    using DegreeType = uint16_t;

    void givenFindBestActionAsync() {
        solvers::SolverInstance solver_instance{
            graph, player_location, opponent_location, objective_id, previous_shift_location};
        start = duration_clock::now();
        future_action = std::async(
            std::launch::async, mm::iterateMinimax, solver_instance, std::make_unique<mm::WinEvaluator>(solver_instance));
    }

    void givenSleepFor(duration_clock::duration duration) { std::this_thread::sleep_for(duration); }

    void whenFindBestAction() {
        solvers::SolverInstance solver_instance{
            graph, player_location, opponent_location, objective_id, previous_shift_location};
        result = mm::iterateMinimax(solver_instance, getEvaluator(solver_instance));
    }

    void whenFindBestActionWithDepth(size_t depth) {
        solvers::SolverInstance solver_instance{
            graph, player_location, opponent_location, objective_id, previous_shift_location};

        minimax_result = mm::findBestAction(solver_instance, getEvaluator(solver_instance), depth);
        result = minimax_result.player_action;
    }

    void whenComputationIsAborted() {
        mm::abortComputation();
        result = future_action.get();
        stop = duration_clock::now();
    }

    void thenActionIsValid() { ASSERT_TRUE(isValidPlayerAction(result, graph, player_location)); }

    void thenActionReachesObjective() { ASSERT_TRUE(actionReachesObjective(result, graph, objective_id)); }

    void thenMinimaxResultShouldBeTerminal() { ASSERT_TRUE(minimax_result.evaluation.is_terminal); }

    void thenMinimaxResultShouldBeNegative() { ASSERT_LT(minimax_result.evaluation.value, 0); }

    void thenShiftLocationIs(const Location& location) { EXPECT_EQ(result.shift.location, location); }

    void thenShiftLocationIsNot(const Location& location) { EXPECT_NE(result.shift.location, location); }

    void thenShiftRotationIsOneOf(const std::vector<DegreeType>& rotation_degrees) {
        std::vector<RotationDegreeType> rotations{};
        std::transform(
            rotation_degrees.begin(), rotation_degrees.end(), std::back_inserter(rotations), [](DegreeType degree) {
                return static_cast<RotationDegreeType>(degree / 90);
            });
        ASSERT_THAT(rotations, testing::Contains(result.shift.rotation));
    };

    void thenMoveLocationIs(const Location& location) { EXPECT_EQ(result.move_location, location); }

    void thenComputationRanForLessThan(duration_clock::duration expected_duration) {
        const std::chrono::duration<double> duration = std::chrono::duration<double>(stop - start);
        ASSERT_THAT(duration, testing::Lt(expected_duration));
    }

    void thenOpponentCannotReachObjective() {
        ASSERT_TRUE(opponentCannotReachAfterPlayerAction(result, graph, opponent_location, objective_id));
    }

    ::testing::AssertionResult isValidPlayerAction(const solvers::PlayerAction& action,
                                                   const MazeGraph& graph,
                                                   const Location& player_start_location) {
        MazeGraph graph_copy{graph};
        auto shift_locations = graph_copy.getShiftLocations();
        auto player_location = player_start_location;
        if (std::find(shift_locations.begin(), shift_locations.end(), action.shift.location) == shift_locations.end()) {
            return ::testing::AssertionFailure() << "Invalid shift location: " << action.shift.location;
        }
        graph_copy.shift(action.shift.location, action.shift.rotation);
        player_location = translateLocationByShift(player_location, action.shift.location, graph_copy.getExtent());
        if (!reachable::isReachable(graph_copy, player_location, action.move_location)) {
            return ::testing::AssertionFailure()
                   << "Invalid move: " << action.move_location << " is not reachable from " << player_location;
        }
        return ::testing::AssertionSuccess();
    }

    ::testing::AssertionResult actionReachesObjective(const solvers::PlayerAction& action,
                                                      const MazeGraph& graph,
                                                      const NodeId objective_id) {
        MazeGraph graph_copy{graph};
        graph_copy.shift(action.shift.location, action.shift.rotation);
        if (graph_copy.getNode(action.move_location).node_id != objective_id) {
            auto objective_location = graph_copy.getLocation(objective_id, Location(-1, -1));
            return ::testing::AssertionFailure()
                   << "Move to " << action.move_location << " does not reach objective at " << objective_location;
        }

        return ::testing::AssertionSuccess();
    }

    ::testing::AssertionResult opponentCannotReachAfterPlayerAction(const solvers::PlayerAction& action,
                                                                    const MazeGraph& graph,
                                                                    Location opponent_location,
                                                                    const NodeId objective_id) {
        MazeGraph graph_copy{graph};
        graph_copy.shift(result.shift.location, result.shift.rotation);
        opponent_location = translateLocationByShift(opponent_location, result.shift.location, graph_copy.getExtent());
        solvers::SolverInstance solver_instance{
            graph, opponent_location, Location{-1, -1}, objective_id, Location{-1, -1}};
        auto actions = solvers::exhsearch::findBestActions(solver_instance);
        if (actions.size() == 1) {
            return ::testing::AssertionFailure()
                   << "Player action " << action << " lets opponent reach objective afterwards with " << actions[0];
        }
        return ::testing::AssertionSuccess();
    }

    size_t max_depth;

    solvers::PlayerAction result;
    mm::MinimaxResult minimax_result{solvers::PlayerAction{}, 0};

    duration_clock::time_point start;
    duration_clock::time_point stop;
    std::future<labyrinth::solvers::PlayerAction> future_action;

private:
    std::unique_ptr<mm::Evaluator> getEvaluator(const solvers::SolverInstance& solver_instance) {
        return (*evaluator_factories[GetParam()])(solver_instance);
    }
};

TEST_P(MinimaxTest, findBestAction__reachableWithOneAction__returnsCorrectMove) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{0, 3});

    whenFindBestAction();

    thenActionIsValid();
    thenActionReachesObjective();
}

TEST_P(MinimaxTest, findBestAction__cannotPreventOpponent__terminatesWithValidAction) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::South});
    givenPlayerLocations(Location{3, 2}, Location{0, 4});
    givenObjectiveAt(Location{0, 5});

    whenFindBestAction();

    thenActionIsValid();
}

TEST_P(MinimaxTest, findBestAction__cannotPreventOpponent__isTerminalAndNegative) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::South});
    givenPlayerLocations(Location{3, 2}, Location{0, 4});
    givenObjectiveAt(Location{0, 5});

    whenFindBestActionWithDepth(2);

    thenMinimaxResultShouldBeTerminal();
    thenMinimaxResultShouldBeNegative();
}

TEST_P(MinimaxTest, findBestAction__opponentCannotPreventReachNextMove__returnsExpectedAction) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{6, 6}, Location{0, 0});
    givenObjectiveAt(Location{0, 6});

    whenFindBestAction();

    thenActionIsValid();
    thenShiftLocationIs(Location{0, 5});
    thenMoveLocationIs(Location{6, 5});
}

TEST_P(MinimaxTest, findBestAction__preventOpponent__returnsExpectedShift) {
    givenGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{2, 6});
    givenObjectiveAt(Location{0, 6});

    whenFindBestActionWithDepth(2);

    thenActionIsValid();
    thenShiftLocationIs(Location{1, 6});
    thenShiftRotationIsOneOf({90, 180, 270});
}

TEST_P(MinimaxTest, findBestAction__bestActionViolatesPreviousShift__doesReturnDifferentShift) {
    givenGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{2, 6});
    givenObjectiveAt(Location{0, 6});
    givenPreviousShift(Location{1, 0});

    whenFindBestActionWithDepth(2);

    thenActionIsValid();
    thenShiftLocationIsNot(Location{1, 6});
}

TEST_P(MinimaxTest, findBestAction__opponentAndObjectiveOppositeOfBoardButPreventPossible__shouldPreventOpponent) {
    givenGraph(mazes::difficult_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{0, 0}, Location{5, 6});
    givenObjectiveAt(Location{5, 0});

    whenFindBestActionWithDepth(2);

    thenActionIsValid();
    thenOpponentCannotReachObjective();
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

INSTANTIATE_TEST_SUITE_P(,
                         MinimaxTest,
                         ::testing::Values(0, 1, 2),
                         [](const testing::TestParamInfo<MinimaxTest::ParamType>& info) {
                             return names[info.param];
                         });
