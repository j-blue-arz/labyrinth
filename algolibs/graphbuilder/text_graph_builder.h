#pragma once
#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"

#include "graph_builder.h"

#include <string>
#include <vector>

namespace graph {

namespace mazes {
extern std::vector<std::string> big_component_maze_9;
} // namespace mazes

class TextGraphBuilder : public GraphBuilder {
public:
    /// Builds a StaticGraph from a text. See implementation file for an example.
    MazeGraph buildGraph() override;
    TextGraphBuilder & setMaze(const std::vector<std::string> & lines);
private:
    static const size_t lines_per_node = 4;

    static size_t first(size_t maze_index) { return maze_index * lines_per_node; }
    static size_t second(size_t maze_index) { return maze_index * lines_per_node + 1; }
    static size_t third(size_t maze_index) { return maze_index * lines_per_node + 2; }

    std::vector<std::string> lines_;
};

}