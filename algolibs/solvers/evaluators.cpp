#include "evaluators.h"

namespace labyrinth {
namespace solvers {
namespace minimax {
namespace factories {

std::unique_ptr<Evaluator> createWinEvaluator(solvers::SolverInstance solver_instance) {
    return std::make_unique<WinEvaluator>(solver_instance);
}

std::unique_ptr<Evaluator> createWinAndReachableLocationsEvaluator(solvers::SolverInstance solver_instance) {
    using Factor = MultiEvaluator::Factor;
    auto win_evaluator = std::make_unique<WinEvaluator>(solver_instance);
    auto reachable_heuristic = std::make_unique<ReachableLocationsHeuristic>();

    auto multi_evaluator = std::make_unique<MultiEvaluator>();
    multi_evaluator->addEvaluator(std::move(win_evaluator), Factor{100});
    multi_evaluator->addEvaluator(std::move(reachable_heuristic), Factor{1});
    return multi_evaluator;
}

std::unique_ptr<Evaluator> createWinAndObjectiveDistanceEvaluator(solvers::SolverInstance solver_instance) {
    using Factor = MultiEvaluator::Factor;
    auto win_evaluator = std::make_unique<WinEvaluator>(solver_instance);
    auto distance_heuristic = std::make_unique<ObjectiveChessboardDistance>(solver_instance);

    auto multi_evaluator = std::make_unique<MultiEvaluator>();
    multi_evaluator->addEvaluator(std::move(win_evaluator), Factor{100});
    multi_evaluator->addEvaluator(std::move(distance_heuristic), Factor{1});
    return multi_evaluator;
}
} // namespace factories
} // namespace minimax
} // namespace solvers
} // namespace labyrinth