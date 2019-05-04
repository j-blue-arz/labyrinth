#include "exhsearch.h"

#include "graph_algorithms.h"

#include "maze_graph.h"
#include "location.h"

#include <algorithm>

namespace graph {

namespace algorithm {

std::vector<ExhaustiveSearch::PlayerAction> ExhaustiveSearch::findBestActions(const Location & player_location, MazeGraph::NodeId objective_id) {
    // invariant: GameStateNode contains reachable nodes after shift has been carried out.
	QueueType state_queue;
    StatePtr root = std::make_shared<GameStateNode>();
    root->reached_nodes.emplace_back(0, graph_.getNodeId(player_location));
    state_queue.push(root);
    while(!state_queue.empty()) {
        auto current_state = state_queue.front();
        state_queue.pop();
        MazeGraph graph = createGraphFromState(graph_, current_state);
        auto shift_locations = graph.getShiftLocations();
        for(auto shift_location : shift_locations) {
            for(MazeGraph::RotationDegreeType rotation : {0, 90, 180, 270}) {
				auto new_state = createNewState(graph, ShiftAction{ shift_location, rotation }, current_state);
				auto found_objective = std::find_if(new_state->reached_nodes.begin(), new_state->reached_nodes.end(),
					[objective_id](auto & reached_node) {return reached_node.reached_id == objective_id; });
				if (found_objective != new_state->reached_nodes.end()) {
					size_t reachable_index = found_objective - new_state->reached_nodes.begin();
					return reconstructActions(new_state, reachable_index);
				}
				else {
					state_queue.push(new_state);
				}
            }
        }
    }
	return std::vector<ExhaustiveSearch::PlayerAction>{};
}

MazeGraph ExhaustiveSearch::createGraphFromState(const MazeGraph & base_graph, StatePtr current_state) {
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

ExhaustiveSearch::StatePtr ExhaustiveSearch::createNewState(const MazeGraph& graph, const ShiftAction& shift, StatePtr current_state)
{
	MazeGraph graph_copy{ graph };
	graph_copy.shift(shift.location, shift.rotation);
	auto updated_player_locations = determineReachedLocations(current_state, graph_copy, shift.location);
	StatePtr new_state = std::make_shared<GameStateNode>(
		current_state,
		shift,
		reachable::multiSourceReachableLocations(graph_copy, updated_player_locations));
	return new_state;
}

std::vector<graph::algorithm::ExhaustiveSearch::PlayerAction> ExhaustiveSearch::reconstructActions(StatePtr new_state, size_t reachable_index) {
	auto cur = new_state;
	auto index = reachable_index;
	std::vector<std::pair<ShiftAction, MazeGraph::NodeId>> id_actions;
	while (!cur->isRoot()) {
		id_actions.push_back(std::make_pair(cur->shift, cur->reached_nodes[index].reached_id));
		index = cur->reached_nodes[index].parent_source_index;
		cur = cur->parent;
	}
	std::vector<PlayerAction> actions;
	MazeGraph reconstruction_graph{ graph_ };
	for (auto id_based_action = id_actions.rbegin(); id_based_action != id_actions.rend(); ++id_based_action) {
		ShiftAction shift = id_based_action->first;
		reconstruction_graph.shift(shift.location, shift.rotation);
		Location move_location = reconstruction_graph.getLocation(id_based_action->second, Location(-1, -1));
		actions.push_back(PlayerAction{ shift, move_location });
	}
	return actions;
}

std::vector<Location> ExhaustiveSearch::determineReachedLocations(StatePtr current_state, const MazeGraph & graph, Location shift_location) {
	std::vector<Location> updated_player_locations;
	updated_player_locations.resize(current_state->reached_nodes.size());
	std::transform(current_state->reached_nodes.begin(), current_state->reached_nodes.end(), updated_player_locations.begin(),
		[&graph, &shift_location](reachable::ReachableNode reached_node) { return graph.getLocation(reached_node.reached_id, shift_location); });
	return updated_player_locations;
}

} // namespace algorithm
} // namespace graph