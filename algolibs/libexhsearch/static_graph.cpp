#include "static_graph.h"
#include <algorithm>

namespace graph {

StaticGraph::StaticGraph(size_t extent) : extent_(extent) {
    NodeId current = 0;
    node_matrix_.resize(extent);
    for (auto row = 0; row < extent; row++) {
        node_matrix_[row].resize(extent);
        for (auto column = 0; column < extent; column++) {
            getNode(Location(row, column)).node_id = current++;
        }
    }
}

void StaticGraph::setOutPaths(const Location & location, const std::string & out_paths) {
    getNode(location).out_paths = out_paths;
}

StaticGraph::NodeId StaticGraph::getNodeId(const Location & location) const {
    return getNode(location).node_id;
}

std::vector<Location> StaticGraph::neighbors(const Location & location) const {
    std::vector<Location> result;
    auto node = getNode(location);
    for (auto out_path_iterator = node.out_paths.cbegin(); out_path_iterator != node.out_paths.cend(); out_path_iterator++) {
        auto out_path = *out_path_iterator;
        const auto potential_location = location + offsetFromOutPath(out_path);
        if (isInRange(potential_location) && hasOutPath(getNode(potential_location), mirrorOutPath(out_path))) {
            result.push_back(potential_location);
        }
    }
    return result;
}

size_t StaticGraph::getNumberOfNodes() const noexcept {
    return extent_ * extent_;
}

size_t StaticGraph::getExtent() const noexcept {
    return extent_;
}

const StaticGraph::Node & StaticGraph::getNode(const Location & location) const {
    return node_matrix_[location.getRow()][location.getColumn()];
}

StaticGraph::Node & StaticGraph::getNode(const Location & location) {
    return node_matrix_[location.getRow()][location.getColumn()];
}

bool StaticGraph::hasOutPath(const Node & node, const OutPathType & out_path) const noexcept {
    return node.out_paths.find(out_path) != std::string::npos;
}

bool StaticGraph::isInRange(const Location & location) const noexcept {
    return (location.getRow() >= 0) &&
        (location.getColumn() >= 0) &&
        (location.getRow() < extent_) &&
        (location.getColumn() < extent_);
}

StaticGraph::OutPathType StaticGraph::mirrorOutPath(OutPathType out_path) noexcept {
    switch (out_path)
    {
    case 'N':
        return 'S';
    case 'E':
        return 'W';
    case 'S':
        return 'N';
    case 'W':
        return 'E';
    default:
        return 'C';
    }
}

Location::OffsetType StaticGraph::offsetFromOutPath(OutPathType out_path) noexcept {
    switch (out_path)
    {
    case 'N':
        return OffsetType{ -1, 0 };
    case 'E':
        return OffsetType{ 0, 1 };
    case 'S':
        return OffsetType{ 1, 0 };
    case 'W':
        return OffsetType{ 0, -1 };
    default:
        return OffsetType{ 0, 0 };
    }
}

} // namespace graph
