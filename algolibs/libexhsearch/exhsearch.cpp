#include "exhsearch.h"

#include "graph_algorithms.h"

#include "maze_graph.h"
#include "location.h"

namespace graph {

namespace algorithm {

std::pair<ExhaustiveSearch::ShiftAction, Location> ExhaustiveSearch::findBestMove(const Location & player_location, const Location & objective_location) {
    MazeGraph graph{graph_};
    auto player_id = graph.getNodeId(player_location);
    auto objective_id = graph.getNodeId(objective_location);

    auto shift_locations = graph.getShiftLocations();
    for(auto shift_location : shift_locations) {
        for(MazeGraph::RotationDegreeType rotation : {0, 90, 180, 270}) {
            MazeGraph graph_copy{graph};
            graph_copy.shift(shift_location, rotation);
            auto updated_player_location = graph_copy.getLocation(player_id, shift_location);
            auto updated_objective_location = graph_copy.getLocation(objective_id, Location(-1, -1));
            auto reachable_locations = reachableLocations(graph_copy, updated_player_location);
            if(std::find(reachable_locations.begin(), reachable_locations.end(), updated_objective_location) != reachable_locations.end()) {
                return std::make_pair(ExhaustiveSearch::ShiftAction{shift_location, rotation}, updated_objective_location);
            }
        }
    }
    return std::make_pair(ExhaustiveSearch::ShiftAction{Location(0, 0), 0}, Location(0, 0));
}

}

}
