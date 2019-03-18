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

StaticGraph::Neighbors StaticGraph::neighbors(const Location & location) const {
    return StaticGraph::Neighbors(*this, location, getNode(location));
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

bool StaticGraph::isInside(const Location & location) const noexcept {
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

StaticGraph::NeighborIterator StaticGraph::NeighborIterator::begin(const StaticGraph & graph, const Location & location, const Node & node) {
    return StaticGraph::NeighborIterator(0, graph, location, node);
}

StaticGraph::NeighborIterator StaticGraph::NeighborIterator::end(const StaticGraph & graph, const Location & location, const Node & node) {
    return StaticGraph::NeighborIterator(5, graph, location, node);
}

bool StaticGraph::NeighborIterator::operator==(const NeighborIterator & other) const noexcept {
    return index_ == other.index_;
}

bool StaticGraph::NeighborIterator::operator!=(const NeighborIterator & other) const noexcept {
    return !(*this == other);
}

StaticGraph::NeighborIterator::reference StaticGraph::NeighborIterator::operator*() const {
    auto out_path = node_.out_paths[index_];
    return location_ + offsetFromOutPath(out_path);
}

StaticGraph::NeighborIterator & StaticGraph::NeighborIterator::operator++() {
    index_++;
    moveToNextNeighbor();
    return *this;
}

StaticGraph::NeighborIterator StaticGraph::NeighborIterator::operator++(int) {
    auto result = NeighborIterator(*this);
    ++(*this);
    return result;
}

void StaticGraph::NeighborIterator::moveToNextNeighbor() {
    
    while (index_ < node_.out_paths.size()) {
        auto out_path = node_.out_paths[index_];
        const auto potential_location = location_ + offsetFromOutPath(out_path);
        if (graph_.isInside(potential_location) && graph_.hasOutPath(graph_.getNode(potential_location), mirrorOutPath(out_path))) {
            break;
        }
        index_++;
    }
    if (index_ == node_.out_paths.size()) {
        index_ = 5;
    }
}

StaticGraph::Neighbors::Neighbors(const StaticGraph & graph, const Location & location, const Node & node) :
    graph_(graph), location_(location), node_(node) {
}

StaticGraph::NeighborIterator StaticGraph::Neighbors::begin() {
    return StaticGraph::NeighborIterator::begin(graph_, location_, node_);
}

StaticGraph::NeighborIterator StaticGraph::Neighbors::end() {
    return StaticGraph::NeighborIterator::end(graph_, location_, node_);
}

} // namespace graph
