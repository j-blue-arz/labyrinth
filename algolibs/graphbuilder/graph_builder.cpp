#include "graph_builder.h"

namespace graph {

void GraphBuilder::addOutPath(const Location & location, OutPath out_path) {
    out_paths_[location.getRow()][location.getColumn()].set(static_cast<size_t>(out_path));
}

void GraphBuilder::addOutPaths(const Location & location, std::initializer_list<OutPath> out_paths) {
    for (auto out_path : out_paths) {
        addOutPath(location, out_path);
    }
}

MazeGraph GraphBuilder::constructGraph() {
    size_t extent = out_paths_.size();
    MazeGraph graph(extent);
    for (int row = 0; row < extent; ++row) {
        for (int column = 0; column < extent; ++column) {
            std::string graph_out_paths;
            if (out_paths_[row][column].test(static_cast<size_t>(OutPath::North))) {
                graph_out_paths.append("N");
            }
            if (out_paths_[row][column].test(static_cast<size_t>(OutPath::East))) {
                graph_out_paths.append("E");
            }
            if (out_paths_[row][column].test(static_cast<size_t>(OutPath::South))) {
                graph_out_paths.append("S");
            }
            if (out_paths_[row][column].test(static_cast<size_t>(OutPath::West))) {
                graph_out_paths.append("W");
            }
            graph.setOutPaths(Location(row, column), graph_out_paths);
        }
    }
    return graph;
}

}