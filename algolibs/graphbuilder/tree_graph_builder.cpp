#include "tree_graph_builder.h"

#include "libexhsearch/maze_graph.h"

#include <string>

namespace labyrinth {

TreeGraphBuilder& TreeGraphBuilder::setExtent(size_t extent) {
    out_paths_.resize(extent);
    for (auto& row : out_paths_) {
        row.resize(extent);
    }
    return *this;
}

MazeGraph TreeGraphBuilder::buildGraph() {
    auto extent = out_paths_.size();
    addPath(Location{extent - 1, 0}, extent, OutPathPosition::East);
    addPath(Location{0, extent - 1}, extent, OutPathPosition::South);
    recursivelyBuildTree(Location{0, extent - 1}, extent, 0);

    return constructGraph();
}

// all names and comments assume rotation of 0
void TreeGraphBuilder::recursivelyBuildTree(const Location& root, size_t size, RotationDegreeType rotation) {
    if (size > 1) {
        // draw L rotated by 90 from root
        addLShapedPath(root, size, addRotations(rotation, 90));
        size_t half = size / 2;

        // correct orientations by rotation
        Location::OffsetType toSouth = offsetFromOutPath(rotateOutPath(OutPathPosition::South, rotation));
        Location::OffsetType toWest = offsetFromOutPath(rotateOutPath(OutPathPosition::West, rotation));
        Location::OffsetType toNorth = offsetFromOutPath(rotateOutPath(OutPathPosition::North, rotation));
        Location::OffsetType toEast = offsetFromOutPath(rotateOutPath(OutPathPosition::East, rotation));

        // corners of the current square
        auto offset = size - 1;
        Location north_east_corner = root;
        Location south_east_corner = north_east_corner + (toSouth * offset);
        Location south_west_corner = south_east_corner + (toWest * offset);
        Location north_west_corner = south_west_corner + (toNorth * offset);

        // south east quadrant, same orientation
        recursivelyBuildTree(root + (toSouth * half), half, rotation);
        // south west quadrant, rotated by 90
        recursivelyBuildTree(south_east_corner + (toWest * half), half, addRotations(rotation, 90));
        // north west quadrant, rotated by 180
        recursivelyBuildTree(south_west_corner + (toNorth * half), half, addRotations(rotation, 180));
        // north east quadrant, rotated by 270
        recursivelyBuildTree(north_west_corner + (toEast * half), half, addRotations(rotation, 270));
    }
}

void TreeGraphBuilder::addLShapedPath(const Location& start, size_t size, RotationDegreeType rotation) {
    Location corner = addPath(start, size, rotateOutPath(OutPathPosition::South, rotation));
    addPath(corner, size - 1, rotateOutPath(OutPathPosition::East, rotation));
}

Location TreeGraphBuilder::addPath(const Location& start, size_t length, OutPathPosition direction) {
    Location current = start;
    for (auto i = 0u; i < length - 1; ++i) {
        current = setNeighbor(current, direction);
    }
    return current;
}

Location TreeGraphBuilder::setNeighbor(const Location& location, OutPathPosition out_path) {
    addOutPath(location, out_path);
    Location neighborLocation = location + offsetFromOutPath(out_path);
    addOutPath(neighborLocation, mirrorOutPath(out_path));
    return neighborLocation;
}

TreeGraphBuilder::OutPathPosition TreeGraphBuilder::mirrorOutPath(OutPathPosition out_path) noexcept {
    return rotateOutPath(out_path, 180);
}

Location::OffsetType TreeGraphBuilder::offsetFromOutPath(OutPathPosition out_path) noexcept {
    switch (out_path) {
    case OutPathPosition::North:
        return Location::OffsetType{-1, 0};
    case OutPathPosition::East:
        return Location::OffsetType{0, 1};
    case OutPathPosition::South:
        return Location::OffsetType{1, 0};
    case OutPathPosition::West:
        return Location::OffsetType{0, -1};
    }
    return Location::OffsetType{0, 0};
}

TreeGraphBuilder::OutPathPosition TreeGraphBuilder::rotateOutPath(OutPathPosition out_path, RotationDegreeType degree) {
    int16_t numRightAngleRotations = degree / 90;
    return static_cast<TreeGraphBuilder::OutPathPosition>((static_cast<size_t>(out_path) + numRightAngleRotations) % 4);
}

TreeGraphBuilder::RotationDegreeType TreeGraphBuilder::addRotations(RotationDegreeType rotation1,
                                                                    RotationDegreeType rotation2) {
    return (rotation1 + rotation2 + 360) % 360;
}

} // namespace labyrinth
