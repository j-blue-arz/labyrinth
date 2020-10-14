#include "c_api.h"
#include "exhsearch.h"
#include <iostream>

PUBLIC_API struct CAction find_action(struct CGraph* c_graph,
                                      struct CPlayerLocations* c_player_locations,
                                      unsigned int objective_id,
                                      struct CLocation* c_previous_shift_location) {
    auto graph = mapGraph(*c_graph);
    auto player_location = mapLocationAtIndex(*c_player_locations, 0);
    auto previous_shift_location = mapLocation(*c_previous_shift_location);
    auto best_actions =
        labyrinth::exhsearch::findBestActions(graph, player_location, objective_id, previous_shift_location);

    if (best_actions.empty()) {
        return errorAction();
    } else {
        return actionToCAction(best_actions[0]);
    }
}

PUBLIC_API void abort_search() {
    labyrinth::exhsearch::abortComputation();
}

PUBLIC_API struct CSearchStatus get_status() {
    struct CSearchStatus search_status = {0, false};
    return search_status;
}
