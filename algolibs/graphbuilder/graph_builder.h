#pragma once

#include "libexhsearch/maze_graph.h"

#include <bitset>

namespace graph {

class GraphBuilder {
public:
    virtual ~GraphBuilder() {};
    virtual MazeGraph buildGraph() = 0;
protected:
    using OutPathIntegerType = uint8_t;
    enum class OutPath : OutPathIntegerType {
        North = 0,
        East = 1,
        South = 2,
        West = 3
    };

    MazeGraph constructGraph();
    void addOutPath(const Location & location, OutPath);
    void addOutPaths(const Location & location, std::initializer_list<OutPath> out_paths);
    

    std::vector<std::vector<std::bitset<4>>> out_paths_;
};

}