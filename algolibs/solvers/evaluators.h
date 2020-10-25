#pragma once

#include "graph_algorithms.h"
#include "maze_graph.h"
#include "minimax.h"

#include <cmath>

namespace labyrinth {

namespace solvers {

namespace minimax {

class WinEvaluator : public Evaluator {
public:
    explicit WinEvaluator(const SolverInstance& solver_instance) : objective_id_{solver_instance.objective_id} {}

    /* The implementation of negamax does not use an alternating player index.
     * Therefore, the Evaluator always has to evaluate from the viewpoint of player 0.
     * For a GameTreeNode, the incoming player action is the opponent action. Hence,
     * The non-heuristic Evaluator will return -1 if the opponent has reached the objective.
     * However, if the current player is placed on the objective, it has to return 0 (not 1), because
     * The player has not actively reached the objective in his last move.
     */
    virtual Evaluation evaluate(const GameTreeNode& node) const override {
        if (node.getGraph().getNode(node.getOpponentLocation()).node_id == objective_id_) {
            return Evaluation{-1, true};
        } else {
            return 0;
        }
    }

private:
    NodeId objective_id_;
};
} // namespace minimax
} // namespace solvers
} // namespace labyrinth