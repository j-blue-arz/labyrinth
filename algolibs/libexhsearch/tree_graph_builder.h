#pragma once
#include "static_graph.h"
#include "location.h"

#include <bitset>
#include <string>
#include <vector>

namespace graph {

class TreeGraphBuilder {
public:
    StaticGraph buildGraph(size_t extent);
private:
    using RotationDegreeType = int16_t;
    using OutPathIntegerType = uint8_t;
    enum class OutPath : OutPathIntegerType {
        North = 0,
        East = 1,
        South = 2,
        West = 3
    };
    void recursivelyBuildTree(const Location & root, size_t size, RotationDegreeType rotation);
    void addLShapedPath(const Location & start, size_t size, RotationDegreeType rotation);
    Location addPath(const Location & start, size_t length, OutPath direction);
    Location setNeighbor(const Location & location, OutPath out_path);
    void addOutPath(const Location & location, OutPath out_path);
    StaticGraph constructGraph();
    static OutPath mirrorOutPath(OutPath out_path) noexcept;
    static Location::OffsetType offsetFromOutPath(OutPath out_path) noexcept;
    static OutPath rotateOutPath(OutPath out_path, RotationDegreeType degree);
    static RotationDegreeType addRotations(RotationDegreeType rotation1, RotationDegreeType rotation2);

    std::vector<std::vector<std::bitset<4>>> out_paths_;
};

}