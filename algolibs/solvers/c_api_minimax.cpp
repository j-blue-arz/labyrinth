#include "c_api.h"
#include "evaluators.h"
#include "minimax.h"
#include "solvers.h"

#include <iostream>
#include <memory>

namespace solvers = labyrinth::solvers;
namespace mm = solvers::minimax;

PUBLIC_API struct CAction find_action(struct CGraph* c_graph,
                                      struct CPlayerLocations* c_player_locations,
                                      unsigned int objective_id,
                                      struct CLocation* c_previous_shift_location) {
    solvers::SolverInstance solver_instance{mapGraph(*c_graph),
                                        mapLocationAtIndex(*c_player_locations, 0),
                                        mapLocationAtIndex(*c_player_locations, 1),
                                        objective_id,
                                        mapLocation(*c_previous_shift_location)};
#if defined MINIMAX_WIN_EVALUATOR
    auto best_action = mm::iterateMinimax(solver_instance, mm::factories::createWinEvaluator(solver_instance));
#elif defined MINIMAX_REACHABLE_HEURISTIC
    auto best_action = mm::iterateMinimax(solver_instance, mm::factories::createWinAndReachableLocationsEvaluator(solver_instance));
#elif defined MINIMAX_DISTANCE_HEURISTIC
    auto best_action = mm::iterateMinimax(solver_instance, mm::factories::createWinAndObjectiveDistanceEvaluator(solver_instance));
#else
    auto best_action = mm::iterateMinimax(solver_instance, std::make_unique<mm::WinEvaluator>(solver_instance));
#endif

    return actionToCAction(best_action);
}

PUBLIC_API void abort_search() {
    mm::abortComputation();
}

PUBLIC_API struct CSearchStatus get_status() {
    auto status = mm::getSearchStatus();
    struct CSearchStatus search_status = {status.current_depth, status.is_terminal};
    return search_status;
}
