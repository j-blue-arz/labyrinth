/**
 * Tests the Evaluators in evaluators.h in isolation
 */

#include "solvers/evaluators.h"
#include "solvers/minimax.h"
#include "minimax_test.h"
#include "solvers_test.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

using namespace labyrinth;

namespace mm = labyrinth::solvers::minimax;

class EvaluatorsTest : public SolversTest {
protected:
    
    void whenWinEvaluatorIsUsed() {
        auto evaluator = mm::WinEvaluator{getSolverInstance()};
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

TEST_F(EvaluatorsTest, givenOpponentReachedObjective_whenWinEvaluatorisUsed_isTerminalAndNegative) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{6, 6});

    whenWinEvaluatorIsUsed();

    thenEvaluationShouldBeTerminal();
    thenEvaluationShouldBeNegative();
}

TEST_F(EvaluatorsTest, givenPlayerIsLocationOnObjective_whenWinEvaluatorisUsed_isZeroAndNotTerminal) {
    givenGraph(mazes::big_component_maze, {OutPaths::North, OutPaths::East});
    givenPlayerLocations(Location{3, 3}, Location{6, 6});
    givenObjectiveAt(Location{3, 3});

    whenWinEvaluatorIsUsed();

    thenEvaluationShouldNotBeTerminal();
    thenEvaluationShouldBeZero();
}
