#include "exhsearch.h"

#include "graph_algorithms.h"

#include "maze_graph.h"
#include "location.h"

#include <queue>

namespace graph {

namespace algorithm {

std::vector<ExhaustiveSearch::PlayerAction> ExhaustiveSearch::findBestActions(const Location & player_location, MazeGraph::NodeId objective_id) {
    // invariant: GameStateNode contains reachable nodes after shift has been carried out.
    std::queue<std::shared_ptr<GameStateNode>> game_states;
    auto player_location_id = graph_.getNodeId(player_location);
    std::shared_ptr<GameStateNode> root = std::make_shared<GameStateNode>();
    root->reached_nodes.emplace_back(0, player_location_id);
    game_states.push(root);
    while(!game_states.empty()) {
        auto current_state = game_states.front();
        game_states.pop();
        MazeGraph graph = createGraphFromState(graph_, current_state);
        // try all shifts
        auto shift_locations = graph.getShiftLocations();
        for(auto shift_location : shift_locations) {
            for(MazeGraph::RotationDegreeType rotation : {0, 90, 180, 270}) {
                MazeGraph graph_copy{graph};
                graph_copy.shift(shift_location, rotation);
                std::vector<Location> updated_player_locations;
                updated_player_locations.resize(current_state->reached_nodes.size());
                std::transform(current_state->reached_nodes.begin(), current_state->reached_nodes.end(), updated_player_locations.begin(),
                    [&graph_copy, &shift_location](reachable::ReachableNode reached_node) { return graph_copy.getLocation(reached_node.reached_id, shift_location); });
                auto updated_objective_location = graph_copy.getLocation(objective_id, Location(-1, -1));
                std::shared_ptr<GameStateNode> new_state = std::make_shared<GameStateNode>();
                new_state->parent = current_state;
                new_state->shift = ShiftAction{shift_location, rotation};
                // find reachable locations
                new_state->reached_nodes = reachable::multiSourceReachableLocations(graph_copy, updated_player_locations);
                // check for objective in reachable locations
                bool found = false;
                for(size_t reachable_index = 0; reachable_index < new_state->reached_nodes.size(); ++reachable_index) {
                    if(new_state->reached_nodes[reachable_index].reached_id == objective_id) {
                        // found -> build path and return
                        auto cur = new_state;
                        auto index = reachable_index;
                        std::vector<std::pair<ShiftAction, MazeGraph::NodeId>> id_actions;
                        while(!cur->isRoot()) {
                            id_actions.push_back(std::make_pair(cur->shift, cur->reached_nodes[index].reached_id));
                            index = cur->reached_nodes[index].parent_source_index;
                            cur = cur->parent;
                        }
                        std::vector<PlayerAction> actions;
                        MazeGraph reconstruction_graph{graph_};
                        for(auto id_based_action = id_actions.rbegin(); id_based_action != id_actions.rend(); ++id_based_action) {
                            ShiftAction shift = id_based_action->first;
                            reconstruction_graph.shift(shift.location, shift.rotation);
                            Location move_location = reconstruction_graph.getLocation(id_based_action->second, Location(-1, -1));
                            actions.push_back(PlayerAction{shift, move_location});
                        }
                        return actions;
                    }
                }
                // not found -> push state to Q
                game_states.push(new_state);
            }
        }
    }
    std::vector<ExhaustiveSearch::PlayerAction> result;
    return result;
}

MazeGraph ExhaustiveSearch::createGraphFromState(const MazeGraph & base_graph, const std::shared_ptr<ExhaustiveSearch::GameStateNode> current_state) {
    MazeGraph graph{base_graph};
    std::vector<ShiftAction> shifts;
    auto cur = current_state;
    while(!cur->isRoot()) {
        shifts.push_back(cur->shift);
        cur = cur->parent;
    }
    for(auto shift = shifts.rbegin(); shift != shifts.rend(); ++shift) {
        graph.shift(shift->location, shift->rotation);
    }
    return graph;
}

} // namespace algorithm
} // namespace graph