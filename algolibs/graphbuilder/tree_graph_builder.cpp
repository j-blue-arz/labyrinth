#include "tree_graph_builder.h"

#include "libexhsearch/static_graph.h"

#include <string>

namespace graph {

TreeGraphBuilder & TreeGraphBuilder::setExtent(size_t extent) {
    out_paths_.resize(extent);
    for (auto & row : out_paths_) {
        row.resize(extent);
    }
    return *this;
}

StaticGraph TreeGraphBuilder::buildGraph() {
    auto extent = out_paths_.size();
    addPath(Location(extent - 1, 0), extent, OutPath::East);
    addPath(Location(0, extent - 1), extent, OutPath::South);
    recursivelyBuildTree(Location(0, extent - 1), extent, 0);
    
    return constructGraph();
}

// all names and comments assume rotation of 0
void TreeGraphBuilder::recursivelyBuildTree(const Location & root, size_t size, RotationDegreeType rotation) {
    if (size > 1) {
        // draw L rotated by 90 from root
        addLShapedPath(root, size, addRotations(rotation, 90));
        size_t half = size / 2;

        // correct orientations by rotation
        Location::OffsetType toSouth = offsetFromOutPath(rotateOutPath(OutPath::South, rotation));
        Location::OffsetType toWest = offsetFromOutPath(rotateOutPath(OutPath::West, rotation));
        Location::OffsetType toNorth = offsetFromOutPath(rotateOutPath(OutPath::North, rotation));
        Location::OffsetType toEast = offsetFromOutPath(rotateOutPath(OutPath::East, rotation));

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

void TreeGraphBuilder::addLShapedPath(const Location & start, size_t size, RotationDegreeType rotation) {
    Location corner = addPath(start, size, rotateOutPath(OutPath::South, rotation));
    addPath(corner, size - 1, rotateOutPath(OutPath::East, rotation));
}

Location TreeGraphBuilder::addPath(const Location & start, size_t length, OutPath direction) {
    Location current = start;
    for (int i = 0; i < length - 1; ++i) {
        current = setNeighbor(current, direction);
    }
    return current;
}

Location TreeGraphBuilder::setNeighbor(const Location & location, OutPath out_path) {
    addOutPath(location, out_path);
    Location neighborLocation = location + offsetFromOutPath(out_path);
    addOutPath(neighborLocation, mirrorOutPath(out_path));
    return neighborLocation;
}

TreeGraphBuilder::OutPath TreeGraphBuilder::mirrorOutPath(OutPath out_path) noexcept {
    switch (out_path) {
    case OutPath::North:
        return OutPath::South;
    case OutPath::East:
        return OutPath::West;
    case OutPath::South:
        return OutPath::North;
    case OutPath::West:
        return OutPath::East;
    }
}

Location::OffsetType TreeGraphBuilder::offsetFromOutPath(OutPath out_path) noexcept {
    switch (out_path) {
    case OutPath::North:
        return Location::OffsetType{ -1, 0 };
    case OutPath::East:
        return Location::OffsetType{ 0, 1 };
    case OutPath::South:
        return Location::OffsetType{ 1, 0 };
    case OutPath::West:
        return Location::OffsetType{ 0, -1 };
    }
}

TreeGraphBuilder::OutPath TreeGraphBuilder::rotateOutPath(OutPath out_path, RotationDegreeType degree) {
    int16_t numRightAngleRotations = degree / 90;
    return static_cast<TreeGraphBuilder::OutPath>((static_cast<OutPathIntegerType>(out_path) + numRightAngleRotations) % 4);
}

TreeGraphBuilder::RotationDegreeType TreeGraphBuilder::addRotations(RotationDegreeType rotation1, RotationDegreeType rotation2) {
    return (rotation1 + rotation2 + 360) % 360;
}


}