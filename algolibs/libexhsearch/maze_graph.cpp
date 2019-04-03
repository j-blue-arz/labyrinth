#include "maze_graph.h"
#include <algorithm>

namespace graph {

MazeGraph::MazeGraph(size_t extent) : extent_(extent) {
    NodeId current = 0;
    node_matrix_.resize(extent);
    for (auto row = 0; row < extent; row++) {
        node_matrix_[row].resize(extent);
        for (auto column = 0; column < extent; column++) {
            getNode(Location(row, column)).node_id = current++;
        }
    }
}

void MazeGraph::setOutPaths(const Location & location, const std::string & out_paths) {
    getNode(location).out_paths = out_paths;
}

bool MazeGraph::hasOutPath(const Location & location, const OutPathType & out_path) const noexcept {
    return hasOutPath(getNode(location), out_path);
}

MazeGraph::NodeId MazeGraph::getNodeId(const Location & location) const {
    return getNode(location).node_id;
}

MazeGraph::Neighbors MazeGraph::neighbors(const Location & location) const {
    return MazeGraph::Neighbors(*this, location, getNode(location));
}

size_t MazeGraph::getNumberOfNodes() const noexcept {
    return extent_ * extent_;
}

size_t MazeGraph::getExtent() const noexcept {
    return extent_;
}

const MazeGraph::Node & MazeGraph::getNode(const Location & location) const {
    return node_matrix_[location.getRow()][location.getColumn()];
}

MazeGraph::Node & MazeGraph::getNode(const Location & location) {
    return node_matrix_[location.getRow()][location.getColumn()];
}

bool MazeGraph::hasOutPath(const Node & node, const OutPathType & out_path) const noexcept {
    return node.out_paths.find(out_path) != std::string::npos;
}

bool MazeGraph::isInside(const Location & location) const noexcept {
    return (location.getRow() >= 0) &&
        (location.getColumn() >= 0) &&
        (location.getRow() < extent_) &&
        (location.getColumn() < extent_);
}

MazeGraph::OutPathType MazeGraph::mirrorOutPath(OutPathType out_path) noexcept {
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

Location::OffsetType MazeGraph::offsetFromOutPath(OutPathType out_path) noexcept {
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

MazeGraph::NeighborIterator MazeGraph::NeighborIterator::begin(const MazeGraph & graph, const Location & location, const Node & node) {
    return MazeGraph::NeighborIterator(0, graph, location, node);
}

MazeGraph::NeighborIterator MazeGraph::NeighborIterator::end(const MazeGraph & graph, const Location & location, const Node & node) {
    return MazeGraph::NeighborIterator(5, graph, location, node);
}

bool MazeGraph::NeighborIterator::operator==(const NeighborIterator & other) const noexcept {
    return index_ == other.index_;
}

bool MazeGraph::NeighborIterator::operator!=(const NeighborIterator & other) const noexcept {
    return !(*this == other);
}

MazeGraph::NeighborIterator::reference MazeGraph::NeighborIterator::operator*() const {
    auto out_path = node_.out_paths[index_];
    return location_ + offsetFromOutPath(out_path);
}

MazeGraph::NeighborIterator & MazeGraph::NeighborIterator::operator++() {
    index_++;
    moveToNextNeighbor();
    return *this;
}

MazeGraph::NeighborIterator MazeGraph::NeighborIterator::operator++(int) {
    auto result = NeighborIterator(*this);
    ++(*this);
    return result;
}

void MazeGraph::NeighborIterator::moveToNextNeighbor() {
    
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

MazeGraph::Neighbors::Neighbors(const MazeGraph & graph, const Location & location, const Node & node) :
    graph_(graph), location_(location), node_(node) {
}

MazeGraph::NeighborIterator MazeGraph::Neighbors::begin() {
    return MazeGraph::NeighborIterator::begin(graph_, location_, node_);
}

MazeGraph::NeighborIterator MazeGraph::Neighbors::end() {
    return MazeGraph::NeighborIterator::end(graph_, location_, node_);
}

std::ostream& operator<<(std::ostream & os, const MazeGraph & graph) {
    auto extent = graph.getExtent();
    std::string row_delimiter(extent * 4, '-');
    for (auto row = 0; row < extent; row++) {
        std::string lines[3] = { std::string(extent * 4, '#'), std::string(extent * 4, '#'), std::string(extent * 4, '#') };
        for (auto column = 0; column < extent; column++) {
            if (graph.hasOutPath(Location(row, column), 'N')) {
                lines[0][column * 4 + 1] = '.';
            }
            if (graph.hasOutPath(Location(row, column), 'E')) {
                lines[1][column * 4 + 2] = '.';
            }
            if (graph.hasOutPath(Location(row, column), 'S')) {
                lines[2][column * 4 + 1] = '.';
            }
            if (graph.hasOutPath(Location(row, column), 'W')) {
                lines[1][column * 4 + 0] = '.';
            }
            lines[1][column * 4 + 1] = '.';
            for (auto & line : lines) {
                line[column * 4 + 3] = '|';
            }
        }
        for (const auto & line : lines) {
            os << line << "\n";
        }
        os << row_delimiter << "\n";
    }
    os << std::endl;
    return os;
}

} // namespace graph
