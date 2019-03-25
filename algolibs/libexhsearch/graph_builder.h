#pragma once
#include "static_graph.h"
#include "location.h"

#include <string>
#include <vector>

namespace graph {

namespace mazes {
extern std::vector<std::string> big_component_maze_9;
} // namespace mazes

class GraphBuilder {
public:
    /// Builds a StaticGraph from a text. See implementation file for an example.
    static StaticGraph buildGraphFromText(const std::vector<std::string> & lines);

    /// Builds a StaticGraph which represents a long path without any branches, e.g.
    /// ###|###|###|
    /// ...|...|..#|
    /// ###|###|#.#|
    /// ------------
    /// ###|###|#.#|
    /// #..|...|..#|
    /// #.#|###|###|
    /// ------------
    /// #.#|###|###|
    /// #..|...|...|
    /// ###|###|###|
    /// ------------
    /// parameter extent controls the height and width of the graph. The path has a length of
    /// extent * extent, i.e. the number of nodes in the graph.
    static StaticGraph buildSnakeGraph(size_t extent);
private:
    static const size_t lines_per_node = 4;

    static size_t first(size_t maze_index) { return maze_index * lines_per_node; }
    static size_t second(size_t maze_index) { return maze_index * lines_per_node + 1; }
    static size_t third(size_t maze_index) { return maze_index * lines_per_node + 2; }

    static bool even(size_t x) { return x % 2 == 0; }
    static bool odd(size_t x) { return x % 2 == 1; }
    static void setInnerColumnsOfSnakeGraph(StaticGraph & graph);
    static void setFirstColumnOfSnakeGraph(StaticGraph & graph);
    static void setLastColumnOfSnakeGraph(StaticGraph & graph);
};

}