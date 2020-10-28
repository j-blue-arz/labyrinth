#pragma once

#include "graph_algorithms.h"
#include "maze_graph.h"
#include "minimax.h"

#include <cmath>
#include <memory>
#include <utility>

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
    Evaluation evaluate(const GameTreeNode& node) const override {
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
    Evaluation evaluate(const GameTreeNode& node) const override {
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

    Evaluation evaluate(const GameTreeNode& node) const override {
        auto player_location = node.getPlayerLocation();
        auto opponent_location = node.getOpponentLocation();
        auto objective_location = node.getGraph().getLocation(objective_id_, Location{-1, -1});
        if (objective_location != Location{-1, -1}) {
            auto opponent_distance = chessboardDistance(opponent_location, objective_location);
            auto player_distance = chessboardDistance(player_location, objective_location);
            if (opponent_distance != 0 && player_distance != 0) {
                return opponent_distance - player_distance;
            } else {
                // If one of the players has reached the objective (distance == 0), then heuristic
                // is invalid, because the new location of the objective is unknown => stay neutral
                return 0;
            }
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

/**
 * Combines several other Evaluators with a linear combination.
 */
class MultiEvaluator : public Evaluator {
private:
    struct Operand;

public:
    struct Factor {
        Evaluation::ValueType value;
    };

    void addEvaluator(std::unique_ptr<Evaluator> evaluator, Factor factor) {
        evaluators_.push_back(Operand{std::move(evaluator), factor});
    }

    Evaluation evaluate(const GameTreeNode& node) const override {
        Evaluation result{0};
        for (const auto& operand : evaluators_) {
            result = result + (operand.evaluator->evaluate(node) * operand.factor.value);
        }
        return result;
    }

private:
    struct Operand {
        std::unique_ptr<Evaluator> evaluator;
        Factor factor;
    };

    std::vector<Operand> evaluators_;
};

} // namespace minimax
} // namespace solvers
} // namespace labyrinth