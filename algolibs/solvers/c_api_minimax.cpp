#include "c_api.h"
#include "minimax.h"
#include <iostream>

PUBLIC_API struct CAction find_action(struct CGraph* c_graph,
                                      struct CPlayerLocations* c_player_locations,
                                      unsigned int objective_id,
                                      struct CLocation* c_previous_shift_location) {
    auto graph = mapGraph(*c_graph);
    auto player_location = mapLocationAtIndex(*c_player_locations, 0);
    auto opponent_location = mapLocationAtIndex(*c_player_locations, 1);
    auto previous_shift_location = mapLocation(*c_previous_shift_location);
    auto best_action =
        labyrinth::minimax::iterateMinimax(graph, player_location, opponent_location, objective_id, previous_shift_location);

    return actionToCAction(best_action);
}

PUBLIC_API void abort_search() {
    labyrinth::minimax::abortComputation();
}

PUBLIC_API struct CSearchStatus get_status() {
    auto status = labyrinth::minimax::getSearchStatus();
    struct CSearchStatus search_status = {status.current_depth, status.is_terminal};
    return search_status;
}