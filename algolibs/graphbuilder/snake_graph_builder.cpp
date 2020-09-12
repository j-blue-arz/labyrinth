#include "snake_graph_builder.h"

namespace labyrinth {

SnakeGraphBuilder& SnakeGraphBuilder::setExtent(size_t extent) {
    out_paths_.resize(extent);
    for (auto& row : out_paths_) {
        row.resize(extent);
    }
    return *this;
}

MazeGraph SnakeGraphBuilder::buildGraph() {
    const auto extent = out_paths_.size();
    setInnerColumns();
    setFirstColumn();
    setLastColumn();
    addOutPaths(Location{0, 0}, {OutPathPosition::East, OutPathPosition::West});
    const auto last_row = extent - 1;
    if (even(extent)) {
        addOutPaths(Location{last_row, 0}, {OutPathPosition::East, OutPathPosition::West});
    } else {
        addOutPaths(Location{last_row, extent - 1}, {OutPathPosition::East, OutPathPosition::West});
    }
    return constructGraph();
}

void SnakeGraphBuilder::setInnerColumns() {
    const auto extent = out_paths_.size();
    for (auto column = 1u; column < extent - 1; column++) {
        for (auto row = 0u; row < extent; row++) {
            addOutPaths(Location{row, column}, {OutPathPosition::East, OutPathPosition::West});
        }
    }
}

void SnakeGraphBuilder::setFirstColumn() {
    const auto extent = out_paths_.size();
    const auto column = 0;
    for (auto row = 1u; row < extent; row++) {
        if (odd(row)) {
            addOutPaths(Location{row, column}, {OutPathPosition::East, OutPathPosition::South});
        } else {
            addOutPaths(Location{row, column}, {OutPathPosition::North, OutPathPosition::East});
        }
    }
}

void SnakeGraphBuilder::setLastColumn() {
    const auto extent = out_paths_.size();
    const auto column = extent - 1;
    for (auto row = 0u; row < extent; row++) {
        if (even(row)) {
            addOutPaths(Location{row, column}, {OutPathPosition::South, OutPathPosition::West});
        } else {
            addOutPaths(Location{row, column}, {OutPathPosition::North, OutPathPosition::West});
        }
    }
}

} // namespace labyrinth
