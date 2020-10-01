#pragma once
#include "solvers/location.h"
#include "solvers/maze_graph.h"

#include "graph_builder.h"

#include <string>
#include <vector>

namespace labyrinth {

class TextGraphBuilder : public GraphBuilder {
public:
    /// Builds a StaticGraph from a text. See implementation file for an example.
    MazeGraph buildGraph() override;
    TextGraphBuilder& setMaze(const std::vector<std::string>& lines);

private:
    static const size_t lines_per_node = 4;

    static size_t first(size_t maze_index) { return maze_index * lines_per_node; }
    static size_t second(size_t maze_index) { return maze_index * lines_per_node + 1; }
    static size_t third(size_t maze_index) { return maze_index * lines_per_node + 2; }

    std::vector<std::string> lines_;
};

} // namespace labyrinth
