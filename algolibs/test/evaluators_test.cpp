/**
 * Tests the Evaluators in evaluators.h in isolation
 */

#include "evaluators_test.h"
#include "solvers/evaluators.h"
#include "solvers/minimax.h"
#include "solvers_test.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

using namespace labyrinth;

namespace mm = labyrinth::solvers::minimax;

class EvaluatorsTest : public SolversTest {
protected:
    void SetUp() override { givenGraph(mazes::evaluators_test_maze, {OutPaths::North, OutPaths::East}); }

    static constexpr Location one_location_reachable = Location{0, 0};
    static constexpr Location four_locations_reachable = Location{0, 3};
    static constexpr Location twentyfive_locations_reachable = Location{3, 3};

    void whenWinEvaluatorIsUsed() {
        auto evaluator = mm::WinEvaluator{getSolverInstance()};
        mm::GameTreeNode game_tree_node{graph, player_location, opponent_location, previous_shift_location};
        result_ = evaluator.evaluate(game_tree_node);
    }

    void whenReachableLocationsHeuristicIsUsed() {
        auto evaluator = mm::ReachableLocationsHeuristic{};
        mm::GameTreeNode game_tree_node{graph, player_location, opponent_location, previous_shift_location};
        result_ = evaluator.evaluate(game_tree_node);
    }

    void thenEvaluationShouldBeTerminal() { ASSERT_TRUE(result_.is_terminal); }

    void thenEvaluationShouldNotBeTerminal() { ASSERT_FALSE(result_.is_terminal); }

    void thenEvaluationShouldBeNegative() { ASSERT_LT(result_.value, 0); }

    void thenEvaluationShouldBePositive() { ASSERT_GT(result_.value, 0); }

    void thenEvaluationShouldBeZero() { ASSERT_EQ(result_.value, 0); }

    mm::Evaluation result_{0};
};

TEST_F(EvaluatorsTest, givenOpponentReachedObjective_whenWinEvaluatorIsUsed_isTerminalAndNegative) {
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{6, 6});

    whenWinEvaluatorIsUsed();

    thenEvaluationShouldBeTerminal();
    thenEvaluationShouldBeNegative();
}

TEST_F(EvaluatorsTest, givenPlayerIsLocationOnObjective_whenWinEvaluatorIsUsed_isZeroAndNotTerminal) {
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{3, 3});

    whenWinEvaluatorIsUsed();

    thenEvaluationShouldNotBeTerminal();
    thenEvaluationShouldBeZero();
}

TEST_F(EvaluatorsTest, givenPlayerHasMoreFreedomOfMove_whenReachableHeuristicIsUsed_isGreaterThanZero) {
    givenPlayerLocations(twentyfive_locations_reachable, four_locations_reachable);

    whenReachableLocationsHeuristicIsUsed();

    thenEvaluationShouldBePositive();
    thenEvaluationShouldNotBeTerminal();
}

TEST_F(EvaluatorsTest, givenPlayerHasEqualFreedomOfMove_whenReachableHeuristicIsUsed_isZero) {
    givenPlayerLocations(four_locations_reachable, four_locations_reachable);

    whenReachableLocationsHeuristicIsUsed();

    thenEvaluationShouldBeZero();
    thenEvaluationShouldNotBeTerminal();
}

TEST_F(EvaluatorsTest, givenPlayerHasLessFreedomOfMove_whenReachableHeuristicIsUsed_isLessThanZero) {
    givenPlayerLocations(one_location_reachable, four_locations_reachable);

    whenReachableLocationsHeuristicIsUsed();

    thenEvaluationShouldBeNegative();
    thenEvaluationShouldNotBeTerminal();
}
