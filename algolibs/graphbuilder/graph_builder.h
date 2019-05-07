#pragma once

#include "libexhsearch/maze_graph.h"

#include <bitset>

namespace graph {

class GraphBuilder {
protected:
    using OutPathIntegerType = uint8_t;
public:
    enum class OutPath : OutPathIntegerType {
        North = 0,
        East = 1,
        South = 2,
        West = 3
    };

    virtual ~GraphBuilder() {};
    virtual MazeGraph buildGraph() = 0;

    GraphBuilder & withStandardShiftLocations();
    GraphBuilder & withLeftoverOutPaths(std::initializer_list<OutPath> out_paths);
protected:
    using OutPaths = std::bitset<4>;
    MazeGraph constructGraph();

    void addOutPath(OutPaths & out_paths, OutPath out_path);
    void addOutPath(const Location & location, OutPath out_path);
    void addOutPaths(const Location & location, std::initializer_list<OutPath> out_paths);

    std::bitset<4> leftover_out_paths_;
    bool standard_shift_locations_{false};
    std::vector<std::vector<OutPaths>> out_paths_;
private:
    std::string outPathsToString(OutPaths out_paths);
};

}
