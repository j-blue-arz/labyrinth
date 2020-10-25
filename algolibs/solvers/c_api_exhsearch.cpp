#include "c_api.h"
#include "exhsearch.h"
#include <iostream>

PUBLIC_API struct CAction find_action(struct CGraph* c_graph,
                                      struct CPlayerLocations* c_player_locations,
                                      unsigned int objective_id,
                                      struct CLocation* c_previous_shift_location) {
    labyrinth::solvers::SolverInstance solver_instance{mapGraph(*c_graph),
                                                       mapLocationAtIndex(*c_player_locations, 0),
                                                       labyrinth::Location{-1, -1},
                                                       objective_id,
                                                       mapLocation(*c_previous_shift_location)};
    auto best_actions = labyrinth::solvers::exhsearch::findBestActions(solver_instance);

    if (best_actions.empty()) {
        return errorAction();
    } else {
        return actionToCAction(best_actions[0]);
    }
}

PUBLIC_API void abort_search() {
    labyrinth::solvers::exhsearch::abortComputation();
}

PUBLIC_API struct CSearchStatus get_status() {
    struct CSearchStatus search_status = {0, false};
    return search_status;
}
