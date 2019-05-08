#pragma once

#include "maze_graph.h"
#include "graph_algorithms.h"

#include <queue>

namespace graph {

namespace algorithm {

class ExhaustiveSearch {
private:
    using NodeId = MazeGraph::NodeId;
public:
    struct ShiftAction {
        Location location{0, 0};
        MazeGraph::RotationDegreeType rotation{0};
    };

    struct PlayerAction {
        ShiftAction shift;
        Location move_location;
    };

    explicit ExhaustiveSearch(const MazeGraph & graph) : graph_{graph} {}

    std::vector<PlayerAction> findBestActions(
        const Location & source,
        MazeGraph::NodeId objective_id,
        const Location & previous_shift_location = Location{-1, -1});

private:
    // The algorithm searches for a path reaching the objective in a tree of game states.
    // For each analyzed succession of shift actions, it keeps track of all reachable locations.
    // The root of this game tree is the initial graph given in the constructor.
    // Each other game state is reached from its parent game state with a GameStateTransition, 
    // i.e. with a shift action and the set of then-reachable nodes.

    // To be able to reconstruct the player actions, the reachable nodes have to include their source node in the previous game state
    // Therefore, they are computed and stored as pairs, where the second entry is the NodeId of the reached node, and the first entry 
    // is the index of the source node in the respective parent array.

    struct GameStateNode;
    using StatePtr = std::shared_ptr<GameStateNode>;

    struct GameStateNode {
        explicit GameStateNode(StatePtr parent, const ShiftAction & shift, const std::vector<reachable::ReachableNode> & reached_nodes)
            : parent{parent}, shift{shift}, reached_nodes{reached_nodes} {}
        explicit GameStateNode() : parent{nullptr} {}

        StatePtr parent{nullptr};
        ShiftAction shift{};
        std::vector<reachable::ReachableNode> reached_nodes;


        bool isRoot() { return parent == nullptr; }
    };

    using QueueType = std::queue<std::shared_ptr<GameStateNode>>;

    MazeGraph createGraphFromState(const MazeGraph & base_graph, StatePtr current_state);
    StatePtr createNewState(const MazeGraph & graph, const ShiftAction & shift, StatePtr current_state);
    std::vector<PlayerAction> reconstructActions(StatePtr new_state, size_t reachable_index);
    std::vector<Location> determineReachedLocations(StatePtr current_state, const MazeGraph & graph, Location shift_location);
    Location opposingShiftLocation(const Location & location);


    const MazeGraph & graph_;

};

} // namespace algorithm
} // namespace graph
