#pragma once

#include "graph_builder.h"

#include "libexhsearch/static_graph.h"
#include "libexhsearch/location.h"

#include <string>
#include <vector>

namespace graph {

class TreeGraphBuilder : public GraphBuilder {
public:
    TreeGraphBuilder & setExtent(size_t extent);
    StaticGraph buildGraph() override;
private:
    using RotationDegreeType = int16_t;
    void recursivelyBuildTree(const Location & root, size_t size, RotationDegreeType rotation);
    void addLShapedPath(const Location & start, size_t size, RotationDegreeType rotation);
    Location addPath(const Location & start, size_t length, OutPath direction);
    Location setNeighbor(const Location & location, OutPath out_path);
    static OutPath mirrorOutPath(OutPath out_path) noexcept;
    static Location::OffsetType offsetFromOutPath(OutPath out_path) noexcept;
    static OutPath rotateOutPath(OutPath out_path, RotationDegreeType degree);
    static RotationDegreeType addRotations(RotationDegreeType rotation1, RotationDegreeType rotation2);

    
};

}