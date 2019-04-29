#include "exhsearch.h"

#include "graph_algorithms.h"

#include "maze_graph.h"
#include "location.h"

namespace graph {

namespace algorithm {

std::vector<ExhaustiveSearch::PlayerAction> ExhaustiveSearch::findBestActions(const Location & player_location, MazeGraph::NodeId objective_id) {
    std::vector<ExhaustiveSearch::PlayerAction> actions;
    MazeGraph graph{graph_};
    auto player_id = graph.getNodeId(player_location);

    auto shift_locations = graph.getShiftLocations();
    for(auto shift_location : shift_locations) {
        for(MazeGraph::RotationDegreeType rotation : {0, 90, 180, 270}) {            
            MazeGraph graph_copy{graph}; 
            graph_copy.shift(shift_location, rotation);
            auto updated_player_location = graph_copy.getLocation(player_id, shift_location);
            auto updated_objective_location = graph_copy.getLocation(objective_id, Location(-1, -1));
            auto reachable_locations = reachableLocations(graph_copy, updated_player_location);
            if(std::find(reachable_locations.begin(), reachable_locations.end(), updated_objective_location) != reachable_locations.end()) {
                ExhaustiveSearch::PlayerAction action{ExhaustiveSearch::ShiftAction{shift_location, rotation}, updated_objective_location};
                actions.push_back(action);
                return actions;
            }
        }
    }
    return actions;
}

} // namespace algorithm
} // namespace graph