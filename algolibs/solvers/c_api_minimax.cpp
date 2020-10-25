#include "c_api.h"
#include "evaluators.h"
#include "minimax.h"
#include "solvers.h"
#include <iostream>

namespace slv = labyrinth::solvers;

PUBLIC_API struct CAction find_action(struct CGraph* c_graph,
                                      struct CPlayerLocations* c_player_locations,
                                      unsigned int objective_id,
                                      struct CLocation* c_previous_shift_location) {
    slv::SolverInstance solver_instance{mapGraph(*c_graph),
                                        mapLocationAtIndex(*c_player_locations, 0),
                                        mapLocationAtIndex(*c_player_locations, 1),
                                        objective_id,
                                        mapLocation(*c_previous_shift_location)};
    slv::minimax::WinEvaluator evaluator{solver_instance};
    auto best_action = slv::minimax::iterateMinimax(solver_instance, evaluator);

    return actionToCAction(best_action);
}

PUBLIC_API void abort_search() {
    slv::minimax::abortComputation();
}

PUBLIC_API struct CSearchStatus get_status() {
    auto status = slv::minimax::getSearchStatus();
    struct CSearchStatus search_status = {status.current_depth, status.is_terminal};
    return search_status;
}