#include "extern.h"
#include "exhsearch.h"

labyrinth::Location mapLocation(const struct CLocation & location) noexcept {
    return labyrinth::Location{location.row, location.column};
}

labyrinth::Node mapNode(const struct CNode & node) noexcept {
    auto out_paths = static_cast<labyrinth::OutPaths>(node.out_paths);
    return labyrinth::Node{node.node_id, out_paths, node.rotation};
}

labyrinth::MazeGraph mapGraph(struct CGraph graph) {
    std::vector<labyrinth::Node> input_nodes;
    input_nodes.reserve(graph.num_nodes);
    for (size_t i = 0; i < graph.num_nodes; ++i) {
        input_nodes.push_back(mapNode(graph.nodes[i]));
    }
    auto extent = static_cast<labyrinth::MazeGraph::ExtentType>(graph.extent);
    labyrinth::MazeGraph maze_graph{extent, input_nodes};
    for (auto pos = 1; pos < extent; pos += 2) {
        maze_graph.addShiftLocation(labyrinth::Location{0, pos});
        maze_graph.addShiftLocation(labyrinth::Location{graph.extent - 1, pos});
        maze_graph.addShiftLocation(labyrinth::Location{pos, 0});
        maze_graph.addShiftLocation(labyrinth::Location{pos, graph.extent - 1});
    }
    return maze_graph;
}

struct CLocation locationToCLocation(const labyrinth::Location & location) noexcept {
    struct CLocation c_location = {location.getRow(), location.getColumn()};
    return c_location;
}

struct CAction actionToCAction(const labyrinth::exhsearch::PlayerAction & action) {
    struct CAction c_action = {locationToCLocation(action.shift.location), action.shift.rotation, locationToCLocation(action.move_location)};
    return c_action;
}

__declspec(dllexport) struct CAction find_action(struct CGraph * c_graph, struct CLocation * c_player_location, unsigned int objective_id,
                                                 struct CLocation * c_previous_shift_location) {
    auto graph = mapGraph(*c_graph);
    auto player_location = mapLocation(*c_player_location);
    auto previous_shift_location = mapLocation(*c_previous_shift_location);
    auto best_actions = labyrinth::exhsearch::findBestActions(
        graph,
        player_location,
        objective_id,
        previous_shift_location);
    struct CAction action = actionToCAction(best_actions[0]);
    return action;
}
