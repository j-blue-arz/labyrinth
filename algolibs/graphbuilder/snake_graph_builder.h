#pragma once
#include "libexhsearch/maze_graph.h"
#include "libexhsearch/location.h"

#include "graph_builder.h"

#include <string>
#include <vector>

namespace labyrinth {

class SnakeGraphBuilder : public GraphBuilder {
public:

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
    MazeGraph buildGraph() override;

    SnakeGraphBuilder & setExtent(size_t extent);
private:
    static bool even(size_t x) noexcept { return x % 2 == 0; }
    static bool odd(size_t x) noexcept { return x % 2 == 1; }
    void setInnerColumns();
    void setFirstColumn();
    void setLastColumn();
};

}
