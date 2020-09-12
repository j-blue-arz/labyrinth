#pragma once

#include "graph_builder.h"

#include "libexhsearch/location.h"
#include "libexhsearch/maze_graph.h"

#include <string>
#include <vector>

namespace labyrinth {

class TreeGraphBuilder : public GraphBuilder {
public:
    TreeGraphBuilder& setExtent(size_t extent);
    MazeGraph buildGraph() override;

private:
    using RotationDegreeType = int16_t;
    void recursivelyBuildTree(const Location& root, size_t size, RotationDegreeType rotation);
    void addLShapedPath(const Location& start, size_t size, RotationDegreeType rotation);
    Location addPath(const Location& start, size_t length, OutPathPosition direction);
    Location setNeighbor(const Location& location, OutPathPosition out_path);
    static OutPathPosition mirrorOutPath(OutPathPosition out_path) noexcept;
    static Location::OffsetType offsetFromOutPath(OutPathPosition out_path) noexcept;
    static OutPathPosition rotateOutPath(OutPathPosition out_path, RotationDegreeType degree);
    static RotationDegreeType addRotations(RotationDegreeType rotation1, RotationDegreeType rotation2);
};

} // namespace labyrinth
