#pragma once

#include "maze_graph.h"
#include "graph_algorithms.h"

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

    explicit ExhaustiveSearch(const MazeGraph & graph) : graph_(graph) {}

    std::vector<PlayerAction> findBestActions(const Location & source, MazeGraph::NodeId objective_id);
private:
    // The algorithm searches for a path reaching the objective in a tree of game states.
    // For each analyzed succession of shift actions, it keeps track of all reachable locations.
    // The root of this game tree is the initial graph given in the constructor.
    // Each other game state is reached from its parent game state with a GameStateTransition, 
    // i.e. with a shift action and the set of then-reachable nodes.

    // To be able to reconstruct the player actions, the reachable nodes have to include their source node in the previous game state
    // Therefore, they are computed and stored as pairs, where the second entry is the NodeId of the reached node, and the first entry 
    // is the index of the source node in the respective parent array.
    
    struct GameStateNode {
        ShiftAction shift{};
        std::vector<reachable::ReachableNode> reached_nodes;
        std::shared_ptr<GameStateNode> parent{nullptr};

        bool isRoot() { return parent == nullptr; }
    };

    MazeGraph createGraphFromState(const MazeGraph & base_graph, std::shared_ptr<GameStateNode> current_state);



    const MazeGraph & graph_;
};

}
}