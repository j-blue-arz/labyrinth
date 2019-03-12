#include "graph_builder.h"

namespace graph {

namespace mazes {
std::vector<std::string> big_component_maze_9 = {
    "###|#.#|#.#|###|#.#|#.#|###|###|#.#|",
    "#..|#..|...|...|#..|..#|...|...|#..|",
    "#.#|###|###|#.#|###|###|#.#|#.#|###|",
    "------------------------------------",
    "###|###|#.#|#.#|#.#|#.#|#.#|#.#|#.#|",
    "...|...|#.#|#..|#.#|...|..#|#..|#.#|",
    "#.#|#.#|#.#|###|#.#|###|#.#|#.#|#.#|",
    "------------------------------------",
    "#.#|#.#|#.#|#.#|#.#|#.#|#.#|#.#|#.#|",
    "#..|#..|..#|#..|..#|#.#|..#|#..|..#|",
    "#.#|#.#|#.#|#.#|#.#|#.#|#.#|#.#|#.#|",
    "------------------------------------",
    "#.#|#.#|#.#|###|#.#|###|###|###|#.#|",
    "..#|..#|#..|...|...|...|...|...|...|",
    "###|#.#|###|#.#|###|#.#|#.#|#.#|###|",
    "------------------------------------",
    "###|#.#|###|#.#|###|#.#|###|#.#|###|",
    "#..|..#|#..|#..|...|#..|...|#..|...|",
    "#.#|###|#.#|#.#|#.#|###|###|#.#|#.#|",
    "------------------------------------",
    "###|#.#|###|#.#|#.#|#.#|#.#|#.#|#.#|",
    "..#|#..|...|...|#.#|#..|..#|...|#.#|",
    "#.#|#.#|###|###|#.#|#.#|#.#|###|#.#|",
    "------------------------------------",
    "#.#|#.#|###|###|#.#|#.#|#.#|###|#.#|",
    "#..|...|...|...|#.#|#..|..#|...|..#|",
    "###|###|#.#|###|#.#|###|#.#|###|#.#|",
    "------------------------------------",
    "###|###|#.#|#.#|#.#|#.#|#.#|#.#|#.#|",
    "...|...|#.#|#..|#..|...|..#|#..|#.#|",
    "#.#|#.#|#.#|###|#.#|###|#.#|#.#|#.#|",
    "------------------------------------",
    "#.#|#.#|#.#|###|#.#|###|###|###|#.#|",
    "..#|..#|#..|...|...|...|...|...|...|",
    "###|#.#|###|#.#|###|#.#|#.#|#.#|###|",
    "------------------------------------" };
}

StaticGraph GraphBuilder::buildGraphFromText(const std::vector<std::string> & lines) {
    size_t extent{ lines.size() / lines_per_node };
    StaticGraph graph{ extent };
    for (auto row = 0; row < extent; row++) {
        for (auto column = 0; column < extent; column++) {
            std::string out_paths;
            if (lines[first(row)][second(column)] == '.') {
                out_paths += "N";
            }
            if (lines[second(row)][third(column)] == '.') {
                out_paths += "E";
            }
            if (lines[third(row)][second(column)] == '.') {
                out_paths += "S";
            }
            if (lines[second(row)][first(column)] == '.') {
                out_paths += "W";
            }
            graph.setOutPaths(Location(row, column), out_paths);
        }
    }
    return graph;
}

StaticGraph GraphBuilder::buildSnakeGraph(const size_t extent) {
    StaticGraph graph{ extent };
    setInnerColumnsOfSnakeGraph(graph);
    setFirstColumnOfSnakeGraph(graph);
    setLastColumnOfSnakeGraph(graph);
    graph.setOutPaths(Location(0, 0), "EW");
    const auto last_row = extent - 1;
    if (even(extent)) {
        graph.setOutPaths(Location(last_row, 0), "EW");
    }
    else {
        graph.setOutPaths(Location(last_row, extent - 1), "EW");
    }
    return graph;
}

void GraphBuilder::setInnerColumnsOfSnakeGraph(StaticGraph & graph) {
    const auto extent = graph.getExtent();
    for (auto column = 1; column < extent - 1; column++) {
        for (auto row = 0; row < extent; row++) {
            graph.setOutPaths(Location(row, column), "EW");
        }
    }
}

void GraphBuilder::setFirstColumnOfSnakeGraph(StaticGraph & graph) {
    const auto extent = graph.getExtent();
    const auto column = 0;
    for (auto row = 1; row < extent; row++) {
        if (odd(row)) {
            graph.setOutPaths(Location(row, column), "ES");
        }
        else {
            graph.setOutPaths(Location(row, column), "NE");
        }
    }
}

void GraphBuilder::setLastColumnOfSnakeGraph(StaticGraph & graph) {
    
    const auto extent = graph.getExtent();
    const auto column = extent - 1;
    for (auto row = 0; row < extent; row++) {
        if (even(row)) {
            graph.setOutPaths(Location(row, column), "SW");
        }
        else {
            graph.setOutPaths(Location(row, column), "NW");
        }
    }
}

}