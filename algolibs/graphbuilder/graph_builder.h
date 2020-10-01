#pragma once

#include "solvers/maze_graph.h"

#include <bitset>
#include <vector>

namespace labyrinth {

class GraphBuilder {
public:
    virtual ~GraphBuilder(){};
    virtual MazeGraph buildGraph() = 0;

    GraphBuilder() = default;
    GraphBuilder(const GraphBuilder&) = default;
    GraphBuilder& operator=(const GraphBuilder&) = default;
    GraphBuilder(GraphBuilder&&) = default;
    GraphBuilder& operator=(GraphBuilder&&) = default;

    GraphBuilder& withLeftoverOutPaths(const std::string& out_paths_string) noexcept;

    GraphBuilder& withStandardShiftLocations() noexcept;

protected:
    enum class OutPathPosition : size_t { North = 0, East = 1, South = 2, West = 3 };
    using OutPathBitset = std::bitset<4>;
    MazeGraph constructGraph();

    static void addOutPath(OutPathBitset& out_paths, OutPathPosition out_path);
    void addOutPath(const Location& location, OutPathPosition out_path);

    OutPathBitset leftover_out_paths_;
    bool standard_shift_locations_{false};
    std::vector<std::vector<OutPathBitset>> out_paths_;

private:
    static OutPaths outPathsForMazeGraph(OutPathBitset out_paths);
};

} // namespace labyrinth
