#include "exhsearch.h"

#include "graph_algorithms.h"

#include "maze_graph.h"
#include "location.h"

#include <algorithm>
#include <memory>

// The algorithm searches for a path reaching the objective in a tree of game states.
// For each analyzed succession of shift actions, it keeps track of all reachable locations.
// The root of this game tree is the initial graph given in the constructor.
// Each other game state is reached from its parent game state with a GameStateTransition,
// i.e. with a shift action and the set of then-reachable nodes.

// To be able to reconstruct the player actions,
// the reachable nodes have to include their source node in the previous game state
// Therefore, they are computed and stored as pairs, where the second entry is the NodeId of the reached node,
// and the first entry is the index of the source node in the respective parent array.

namespace labyrinth {

namespace exhsearch {

namespace { // anonymous namespace for file-internal linkage

struct GameStateNode;
using StatePtr = std::shared_ptr<GameStateNode>;

struct GameStateNode {
    explicit GameStateNode(StatePtr parent, const ShiftAction& shift,
        const std::vector<reachable::ReachableNode>& reached_nodes)
        : parent{parent}, shift{shift}, reached_nodes{reached_nodes} {}
    explicit GameStateNode() noexcept : parent{nullptr} {}

    StatePtr parent{nullptr};
    ShiftAction shift{};
    std::vector<reachable::ReachableNode> reached_nodes;


    bool isRoot() noexcept { return parent == nullptr; }
};

using QueueType = std::queue<std::shared_ptr<GameStateNode>>;

MazeGraph createGraphFromState(const MazeGraph& base_graph, StatePtr current_state) {
    MazeGraph graph{base_graph};
    std::vector<ShiftAction> shifts;
    auto cur = current_state;
    while (!cur->isRoot()) {
        shifts.push_back(cur->shift);
        cur = cur->parent;
    }
    for (auto shift = shifts.rbegin(); shift != shifts.rend(); ++shift) {
        graph.shift(shift->location, shift->rotation);
    }
    return graph;
}

std::vector<Location> determineReachedLocations(const GameStateNode& current_state, const MazeGraph& graph,
    Location shift_location) {
    std::vector<Location> updated_player_locations;
    updated_player_locations.resize(current_state.reached_nodes.size());
    std::transform(current_state.reached_nodes.begin(), current_state.reached_nodes.end(),
        updated_player_locations.begin(),
        [&graph, &shift_location](reachable::ReachableNode reached_node) {
            return graph.getLocation(reached_node.reached_id, shift_location);
        });
    return updated_player_locations;
}

StatePtr createNewState(const MazeGraph& graph, const ShiftAction& shift, StatePtr current_state) {
    MazeGraph graph_copy{graph};
    graph_copy.shift(shift.location, shift.rotation);
    auto updated_player_locations = determineReachedLocations(*current_state, graph_copy, shift.location);
    StatePtr new_state = std::make_shared<GameStateNode>(
        current_state,
        shift,
        reachable::multiSourceReachableLocations(graph_copy, updated_player_locations));
    return new_state;
}

std::vector<PlayerAction> reconstructActions(const MazeGraph& base_graph, StatePtr new_state, size_t reachable_index) {
    auto cur = new_state;
    auto index = reachable_index;
    std::vector<std::pair<ShiftAction, NodeId>> id_actions;
    while (!cur->isRoot()) {
        id_actions.push_back(std::make_pair(cur->shift, cur->reached_nodes[index].reached_id));
        index = cur->reached_nodes[index].parent_source_index;
        cur = cur->parent;
    }
    std::vector<PlayerAction> actions;
    MazeGraph reconstruction_graph{base_graph};
    for (auto id_based_action = id_actions.rbegin(); id_based_action != id_actions.rend(); ++id_based_action) {
        ShiftAction shift = id_based_action->first;
        reconstruction_graph.shift(shift.location, shift.rotation);
        Location move_location = reconstruction_graph.getLocation(id_based_action->second, Location(-1, -1));
        actions.push_back(PlayerAction{shift, move_location});
    }
    return actions;
}

Location opposingShiftLocation(const Location& location, MazeGraph::ExtentType extent) noexcept {
    const auto row = location.getRow();
    const auto column = location.getColumn();
    if (column == 0) {
        return Location{row, extent - 1};
    }
    else if (row == 0) {
        return Location{extent - 1, column};
    }
    else if (column == extent - 1) {
        return Location{row, 0};
    }
    else if (row == extent - 1) {
        return Location{0, column};
    }
    return location;
}

OutPaths combineOutPaths(OutPaths out_paths1, OutPaths out_paths2) {
    return static_cast<OutPaths>(static_cast<OutPathsIntegerType>(out_paths1) |
        static_cast<OutPathsIntegerType>(out_paths2));
}

std::vector<RotationDegreeType> determineRotations(const Node& node) {
    auto north_south = combineOutPaths(OutPaths::North, OutPaths::South);
    auto east_west = combineOutPaths(OutPaths::East, OutPaths::West);
    if (node.out_paths == north_south || node.out_paths == east_west) {
        return std::vector<RotationDegreeType>{0, 90};
    }
    else {
        return std::vector<RotationDegreeType>{0, 90, 180, 270};
    }
}



} // anonymous namespace

std::vector<PlayerAction> findBestActions(const MazeGraph& graph,
    const Location& player_location, NodeId objective_id, const Location& previous_shift_location) {
    // invariant: GameStateNode contains reachable nodes after shift has been carried out.
    QueueType state_queue;
    StatePtr root = std::make_shared<GameStateNode>();
    root->reached_nodes.emplace_back(0, graph.getNode(player_location).node_id);
    root->shift = ShiftAction{previous_shift_location, 0};
    state_queue.push(root);
    while (!state_queue.empty()) {
        auto current_state = state_queue.front();
        state_queue.pop();
        MazeGraph current_graph = createGraphFromState(graph, current_state);
        auto shift_locations = current_graph.getShiftLocations();
        auto invalid_shift_location = opposingShiftLocation(current_state->shift.location, graph.getExtent());
        for (const auto& shift_location : shift_locations) {
            if (shift_location == invalid_shift_location) {
                continue;
            }
            auto rotations = determineRotations(current_graph.getLeftover());
            for (RotationDegreeType rotation : rotations) {
                auto new_state = createNewState(current_graph, ShiftAction{shift_location, rotation}, current_state);
                auto found_objective = std::find_if(new_state->reached_nodes.begin(), new_state->reached_nodes.end(),
                    [objective_id](auto& reached_node) {return reached_node.reached_id == objective_id; });
                if (found_objective != new_state->reached_nodes.end()) {
                    const size_t reachable_index = found_objective - new_state->reached_nodes.begin();
                    return reconstructActions(graph, new_state, reachable_index);
                }
                else {
                    state_queue.push(new_state);
                }
            }
        }
    }
    return std::vector<PlayerAction>{};
}

} // namespace algorithm
} // namespace graph
