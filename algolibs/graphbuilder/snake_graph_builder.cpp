#include "snake_graph_builder.h"

namespace graph {

SnakeGraphBuilder & SnakeGraphBuilder::setExtent(size_t extent) {
    out_paths_.resize(extent);
    for (auto & row : out_paths_) {
        row.resize(extent);
    }
    return *this;
}

MazeGraph SnakeGraphBuilder::buildGraph() {
    const auto extent = out_paths_.size();
    setInnerColumns();
    setFirstColumn();
    setLastColumn();
    addOutPaths(Location(0, 0), { OutPath::East, OutPath::West });
    const auto last_row = extent - 1;
    if (even(extent)) {
        addOutPaths(Location(last_row, 0), { OutPath::East, OutPath::West });
    }
    else {
        addOutPaths(Location(last_row, extent - 1), { OutPath::East, OutPath::West });
    }
    return constructGraph();
}

void SnakeGraphBuilder::setInnerColumns() {
    const auto extent = out_paths_.size();
    for (auto column = 1; column < extent - 1; column++) {
        for (auto row = 0; row < extent; row++) {
            addOutPaths(Location(row, column), { OutPath::East, OutPath::West });
        }
    }
}

void SnakeGraphBuilder::setFirstColumn() {
    const auto extent = out_paths_.size();
    const auto column = 0;
    for (auto row = 1; row < extent; row++) {
        if (odd(row)) {
            addOutPaths(Location(row, column), { OutPath::East, OutPath::South });
        }
        else {
            addOutPaths(Location(row, column), { OutPath::North, OutPath::East });
        }
    }
}

void SnakeGraphBuilder::setLastColumn() {
    const auto extent = out_paths_.size();
    const auto column = extent - 1;
    for (auto row = 0; row < extent; row++) {
        if (even(row)) {
            addOutPaths(Location(row, column), { OutPath::South, OutPath::West });
        }
        else {
            addOutPaths(Location(row, column), { OutPath::North, OutPath::West });
        }
    }
}

}