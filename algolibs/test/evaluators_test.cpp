/**
 * Tests the Evaluators in evaluators.h in isolation
 */

#include "evaluators_test.h"
#include "solvers/evaluators.h"
#include "solvers/minimax.h"
#include "solvers_test.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include <cstdarg>
#include <utility>

using namespace labyrinth;

namespace mm = labyrinth::solvers::minimax;

class EvaluatorsTest : public SolversTest {
protected:
    using Factor = mm::MultiEvaluator::Factor;
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

    void whenObjectiveChessboardDistanceIsUsed() {
        auto evaluator = mm::ObjectiveChessboardDistance{getSolverInstance()};
        mm::GameTreeNode game_tree_node{graph, player_location, opponent_location, previous_shift_location};
        result_ = evaluator.evaluate(game_tree_node);
    }

    void whenMultiEvaluatorIsUsed(Factor win_evaluator_factor, Factor reachable_heuristic_factor) {
        auto multi_evaluator = mm::MultiEvaluator{};
        multi_evaluator.addEvaluator(std::make_unique<mm::WinEvaluator>(getSolverInstance()), win_evaluator_factor);
        multi_evaluator.addEvaluator(std::make_unique<mm::ReachableLocationsHeuristic>(), reachable_heuristic_factor);
        mm::GameTreeNode game_tree_node{graph, player_location, opponent_location, previous_shift_location};
        result_ = multi_evaluator.evaluate(game_tree_node);
    }

    void thenEvaluationShouldBeTerminal() { ASSERT_TRUE(result_.is_terminal); }

    void thenEvaluationShouldNotBeTerminal() { ASSERT_FALSE(result_.is_terminal); }

    void thenEvaluationShouldBeNegative() { ASSERT_LT(result_.value, 0); }

    void thenEvaluationShouldBePositive() { ASSERT_GT(result_.value, 0); }

    void thenEvaluationShouldBeLessThan(mm::Evaluation::ValueType value) { ASSERT_LT(result_.value, value); }

    void thenEvaluationShouldBe(mm::Evaluation::ValueType value) { ASSERT_EQ(result_.value, value); }

    mm::Evaluation result_{0};
};

TEST_F(EvaluatorsTest, givenOpponentReachedObjective_whenWinEvaluatorIsUsed_isTerminalAndNegative) {
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{6, 6});

    whenWinEvaluatorIsUsed();

    thenEvaluationShouldBeTerminal();
    thenEvaluationShouldBe(-1);
}

TEST_F(EvaluatorsTest, givenPlayerIsLocationOnObjective_whenWinEvaluatorIsUsed_isZeroAndNotTerminal) {
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{3, 3});

    whenWinEvaluatorIsUsed();

    thenEvaluationShouldNotBeTerminal();
    thenEvaluationShouldBe(0);
}

TEST_F(EvaluatorsTest, givenPlayerHasMoreFreedomOfMove_whenReachableHeuristicIsUsed_isGreaterThanZero) {
    givenPlayerLocations(twentyfive_locations_reachable, four_locations_reachable);

    whenReachableLocationsHeuristicIsUsed();

    thenEvaluationShouldBePositive();
}

TEST_F(EvaluatorsTest, givenPlayerHasEqualFreedomOfMove_whenReachableHeuristicIsUsed_isZero) {
    givenPlayerLocations(four_locations_reachable, four_locations_reachable);

    whenReachableLocationsHeuristicIsUsed();

    thenEvaluationShouldBe(0);
}

TEST_F(EvaluatorsTest, givenPlayerHasLessFreedomOfMove_whenReachableHeuristicIsUsed_isLessThanZero) {
    givenPlayerLocations(one_location_reachable, four_locations_reachable);

    whenReachableLocationsHeuristicIsUsed();

    thenEvaluationShouldBeNegative();
}

TEST_F(EvaluatorsTest, givenPlayerIsCloserToObjective_whenObjectiveChessboardDistanceIsUsed_isExpectedValue) {
    givenPlayerLocations(Location{0, 0}, Location{6, 6});
    givenObjectiveAt(Location{2, 2});

    whenObjectiveChessboardDistanceIsUsed();

    thenEvaluationShouldBe(2);
}

TEST_F(EvaluatorsTest, givenOpponentIsCloserToObjective_whenObjectiveChessboardDistanceIsUsed_isExpectedValue) {
    givenPlayerLocations(Location{2, 6}, Location{4, 5});
    givenObjectiveAt(Location{6, 1});

    whenObjectiveChessboardDistanceIsUsed();

    thenEvaluationShouldBe(-1);
}

TEST_F(EvaluatorsTest, givenSameDistanceToObjective_whenObjectiveChessboardDistanceIsUsed_isExpectedValue) {
    givenPlayerLocations(Location{5, 0}, Location{6, 1});
    givenObjectiveAt(Location{3, 3});

    whenObjectiveChessboardDistanceIsUsed();

    thenEvaluationShouldBe(0);
}

TEST_F(EvaluatorsTest, givenObjectiveOnLeftover_whenObjectiveChessboardDistanceIsUsed_isZero) {
    givenPlayerLocations(Location{5, 0}, Location{6, 1});
    givenObjectiveOnLeftover();

    whenObjectiveChessboardDistanceIsUsed();

    thenEvaluationShouldBe(0);
}

TEST_F(EvaluatorsTest, givenOpponentReachedObjective_whenCombinedEvaluatorIsUsed_isTerminalAndRespectsReachableLocations) {
    givenPlayerLocations(four_locations_reachable, twentyfive_locations_reachable);
    givenObjectiveAt(Location{3, 3});

    whenMultiEvaluatorIsUsed(Factor{100}, Factor{1});

    thenEvaluationShouldBeTerminal();
    thenEvaluationShouldBeLessThan(100);
}
