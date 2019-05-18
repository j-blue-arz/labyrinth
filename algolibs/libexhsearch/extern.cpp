#include "extern.h"
#include "exhsearch.h"

labyrinth::Location mapLocation(struct CLocation location) noexcept {
    return labyrinth::Location{location.row, location.column};
}

labyrinth::MazeGraph::InputNode mapNode(struct CNode node) noexcept {
    return labyrinth::MazeGraph::InputNode{node.node_id, node.out_paths, node.rotation};
}

labyrinth::MazeGraph mapGraph(struct CGraph graph) {
    auto num_nodes = graph.extent * graph.extent + 1;
    std::vector<labyrinth::MazeGraph::InputNode> input_nodes;
    input_nodes.reserve(num_nodes);
    for (size_t i = 0; i < num_nodes; ++i) {
        input_nodes.push_back(mapNode(graph.nodes[i]));
    }
    return labyrinth::MazeGraph{num_nodes, input_nodes};
}

__declspec(dllexport) struct CAction find_action(struct CGraph cgraph, struct CLocation player_location, unsigned int objective_id) {
    auto graph = mapGraph(cgraph);
    auto best_actions = labyrinth::exhsearch::findBestActions(graph, mapLocation(player_location), objective_id, mapLocation(cgraph.last_shift_location));
    struct CAction action;
    return action;
}
