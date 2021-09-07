#include "exhsearch.h"
#include "graph_algorithms.h"
#include "maze_graph.h"
#include "solvers.h"

#include <iostream>

#include <emscripten/bind.h>

namespace labyrinth {

Node* createNode(NodeId node_id, OutPathsIntegerType out_paths_bitmask, short rotation) {
    Node* node = new Node();
    node->node_id = node_id;
    node->out_paths = static_cast<OutPaths>(out_paths_bitmask);
    node->rotation = static_cast<RotationDegreeType>((rotation / 90 + 4) % 4);
    return node;
}

solvers::PlayerAction errorAction() {
    Location errorLocation{-1, -1};
    return solvers::PlayerAction{solvers::ShiftAction{errorLocation, RotationDegreeType::_0}, errorLocation};
}

struct LocationValueObject {
    Location::IndexType row;
    Location::IndexType column;
};

solvers::PlayerAction findBestAction(const MazeGraph& graph,
                                     LocationValueObject player_location,
                                     NodeId objective_id,
                                     LocationValueObject previous_shift_location) {
    labyrinth::solvers::SolverInstance solver_instance{
        graph,
        Location{player_location.row, player_location.column},
        labyrinth::Location{-1, -1},
        objective_id,
        Location{previous_shift_location.row, previous_shift_location.column}};
    auto best_actions = solvers::exhsearch::findBestActions(solver_instance);
    if (best_actions.empty()) {
        return errorAction();
    } else {
        return best_actions[0];
    }
}

void addShiftLocationForGraph(MazeGraph& graph, LocationValueObject location) {
    Location loc{location.row, location.column};
    graph.addShiftLocation(loc);
}

EMSCRIPTEN_BINDINGS(libexhsearch) {
    emscripten::class_<Location>("Location")
        .constructor<Location::IndexType, Location::IndexType>()
        .property("row", &Location::getRow)
        .property("column", &Location::getColumn);

    emscripten::value_object<solvers::ShiftAction>("ShiftAction")
        .field("location", &solvers::ShiftAction::location)
        .field("rotation", &solvers::ShiftAction::rotation);

    emscripten::value_object<solvers::PlayerAction>("PlayerAction")
        .field("shift", &solvers::PlayerAction::shift)
        .field("move_location", &solvers::PlayerAction::move_location);

    emscripten::value_object<LocationValueObject>("LocationValueObject")
        .field("row", &LocationValueObject::row)
        .field("column", &LocationValueObject::column);

    emscripten::class_<Node>("Node") //
        .constructor(&createNode);

    emscripten::register_vector<Node>("vectorOfNode");

    emscripten::class_<MazeGraph>("MazeGraph")
        .constructor<const std::vector<Node>&>()
        .function("addShiftLocation", &addShiftLocationForGraph);

    emscripten::function("findBestAction", &findBestAction);
}

} // namespace labyrinth
