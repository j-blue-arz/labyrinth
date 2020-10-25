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

class ReachableLocationsHeuristic : public Evaluator {
public:
    explicit ReachableLocationsHeuristic() {}

    virtual Evaluation evaluate(const GameTreeNode& node) const override {
        auto player_reachable = reachable::reachableLocations(node.getGraph(), node.getPlayerLocation());
        auto opponent_reachable = reachable::reachableLocations(node.getGraph(), node.getOpponentLocation());
        auto player_diameter = static_cast<Evaluation::ValueType>(std::sqrt(player_reachable.size()));
        auto opponent_diameter = static_cast<Evaluation::ValueType>(std::sqrt(opponent_reachable.size()));
        auto value = player_diameter - opponent_diameter;
        return value;
    }
};

class ObjectiveChessboardDistance : public Evaluator {
public:
    explicit ObjectiveChessboardDistance(const SolverInstance& solver_instance) :
        objective_id_{solver_instance.objective_id} {}

    virtual Evaluation evaluate(const GameTreeNode& node) const override {
        auto player_location = node.getPlayerLocation();
        auto opponent_location = node.getOpponentLocation();
        auto objective_location = node.getGraph().getLocation(objective_id_, Location{-1, -1});
        if (objective_location != Location{-1, -1}) {
            return chessboardDistance(opponent_location, objective_location) -
                   chessboardDistance(player_location, objective_location);
        } else {
            // If the objective is on the leftover, the current player can insert
            // it anywhere on the border. It is therefore difficult to determine
            // any heuristic distance metric for this case. => stay neutral
            return 0;
        }
    }

private:
    Location::IndexType chessboardDistance(const Location& a, const Location& b) const {
        return std::max(std::abs(a.getColumn() - b.getColumn()), std::abs(a.getRow() - b.getRow()));
    }

    NodeId objective_id_;
};
} // namespace minimax
} // namespace solvers
} // namespace labyrinth