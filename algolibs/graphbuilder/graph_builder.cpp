#include "graph_builder.h"

namespace labyrinth {

void GraphBuilder::addOutPath(OutPathBitset & out_paths, OutPathPosition out_path) {
    out_paths.set(static_cast<size_t>(out_path));
}

void GraphBuilder::addOutPath(const Location & location, OutPathPosition out_path) {
    addOutPath(out_paths_[location.getRow()][location.getColumn()], out_path);
}

void GraphBuilder::addOutPaths(const Location & location, std::vector<OutPathPosition> out_paths) {
    for (const auto & out_path : out_paths) {
        addOutPath(location, out_path);
    }
}

GraphBuilder & GraphBuilder::withStandardShiftLocations() noexcept {
    standard_shift_locations_ = true;
    return *this;
}

MazeGraph GraphBuilder::constructGraph() {
    MazeGraph::ExtentType extent = out_paths_.size();
    MazeGraph graph{extent};
    for (auto row = 0; row < extent; ++row) {
        for (auto column = 0; column < extent; ++column) {
            auto graph_out_paths = outPathsForMazeGraph(out_paths_[row][column]);
            graph.setOutPaths(Location{row, column}, graph_out_paths);
        }
    }
    auto leftover_out_paths = outPathsForMazeGraph(leftover_out_paths_);
    graph.setLeftoverOutPaths(leftover_out_paths);
    if (standard_shift_locations_) {
        for (auto pos = 1; pos < extent; pos += 2) {
            graph.addShiftLocation(Location{0, pos});
            graph.addShiftLocation(Location{extent - 1, pos});
            graph.addShiftLocation(Location{pos, 0});
            graph.addShiftLocation(Location{pos, extent - 1});
        }
    }
    return graph;
}

OutPaths GraphBuilder::outPathsForMazeGraph(GraphBuilder::OutPathBitset out_paths) {
    OutPathsIntegerType out_paths_int{0};
    auto all_positions = {OutPathPosition::North, OutPathPosition::East, OutPathPosition::South, OutPathPosition::West};
    for (OutPathPosition out_path : all_positions) {
        auto position = static_cast<size_t>(out_path);
        if (out_paths.test(position)) {
            out_paths_int += (1 << position);
        }
    }
    return static_cast<OutPaths>(out_paths_int);
}

}
