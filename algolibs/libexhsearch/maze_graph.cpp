#include "maze_graph.h"
#include "location.h"
#include <algorithm>
#include <array>

namespace labyrinth {

MazeGraph::MazeGraph(size_t extent) : extent_{extent} {
    NodeId current = 0;
    node_matrix_.resize(extent);
    for (auto row = 0; row < extent; row++) {
        node_matrix_[row].resize(extent);
        for (auto column = 0; column < extent; column++) {
            getNode(Location{row, column}).node_id = current++;
        }
    }
    leftover_.node_id = current;
}

void MazeGraph::setOutPaths(const Location & location, const std::string & out_paths) {
    getNode(location).out_paths = out_paths;
}

void MazeGraph::addShiftLocation(const Location & location) {
    if (std::find(shift_locations_.begin(), shift_locations_.end(), location) == shift_locations_.end()) {
        shift_locations_.push_back(location);
    }
}

void MazeGraph::setLeftoverOutPaths(const std::string & out_paths) {
    leftover_.out_paths = out_paths;
}

bool MazeGraph::hasOutPath(const Location & location, const OutPathType & out_path) const {
    return hasOutPath(getNode(location), out_path);
}

MazeGraph::NodeId MazeGraph::getNodeId(const Location & location) const {
    return getNode(location).node_id;
}

MazeGraph::NodeId MazeGraph::getLeftoverNodeId() const noexcept {
    return leftover_.node_id;
}

Location MazeGraph::getLocation(MazeGraph::NodeId node_id, const Location & leftover_location) const {
    Location result = leftover_location;
    for (Location::IndexType row = 0; row < extent_; ++row) {
        for (Location::IndexType column = 0; column < extent_; ++column) {
            if (node_matrix_[row][column].node_id == node_id) {
                return Location{row, column};
            }
        }
    }
    return leftover_location;
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

void MazeGraph::shift(const Location & location, RotationDegreeType leftoverRotation) {
    OffsetType::OffsetValueType row_offset{0}, column_offset{0};
    if (location.getRow() == 0) {
        row_offset = 1;
    }
    else if (location.getRow() == extent_ - 1) {
        row_offset = -1;
    }
    else if (location.getColumn() == 0) {
        column_offset = 1;
    }
    else if (location.getColumn() == extent_ - 1) {
        column_offset = -1;
    }
    const OffsetType offset{row_offset, column_offset};
    std::vector<Location> line{};
    line.reserve(extent_);
    Location current = location;
    for (size_t i = 0; i < extent_; ++i) {
        line.push_back(current);
        current = current + offset;
    }
    const Node updated_leftover = getNode(line.back());
    for (auto to = line.rbegin(), from = std::next(to); from != line.rend(); ++to, ++from) {
        getNode(*to) = getNode(*from);
    }
    leftover_.rotation = leftoverRotation;
    getNode(line.front()) = leftover_;
    leftover_ = updated_leftover;
}

const MazeGraph::Node & MazeGraph::getNode(const Location & location) const {
    return node_matrix_[location.getRow()][location.getColumn()];
}

MazeGraph::Node & MazeGraph::getNode(const Location & location) {
    return node_matrix_[location.getRow()][location.getColumn()];
}

bool MazeGraph::hasOutPath(const Node & node, const OutPathType & out_path) const {
    auto out_path_to_check = rotateOutPath(out_path, -node.rotation);
    return node.out_paths.find(out_path_to_check) != std::string::npos;
}

bool MazeGraph::isInside(const Location & location) const noexcept {
    return (location.getRow() >= 0) &&
        (location.getColumn() >= 0) &&
        (location.getRow() < extent_) &&
        (location.getColumn() < extent_);
}

MazeGraph::OutPathType MazeGraph::rotateOutPath(OutPathType out_path, RotationDegreeType rotation) {
    static const std::string out_path_rotation{"NESW"};
    const auto rotations = rotation / 90;
    return out_path_rotation[(out_path_rotation.find(out_path) + rotations + 4) % 4];
}

MazeGraph::OutPathType MazeGraph::mirrorOutPath(OutPathType out_path) noexcept {
    switch (out_path) {
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
    switch (out_path) {
    case 'N':
        return OffsetType{-1, 0};
    case 'E':
        return OffsetType{0, 1};
    case 'S':
        return OffsetType{1, 0};
    case 'W':
        return OffsetType{0, -1};
    default:
        return OffsetType{0, 0};
    }
}

MazeGraph::NeighborIterator MazeGraph::NeighborIterator::begin(const MazeGraph & graph, const Location & location, const Node & node) {
    return MazeGraph::NeighborIterator{0, graph, location, node};
}

MazeGraph::NeighborIterator MazeGraph::NeighborIterator::end(const MazeGraph & graph, const Location & location, const Node & node) {
    return MazeGraph::NeighborIterator{5, graph, location, node};
}

bool MazeGraph::NeighborIterator::operator==(const NeighborIterator & other) const noexcept {
    return index_ == other.index_;
}

bool MazeGraph::NeighborIterator::operator!=(const NeighborIterator & other) const noexcept {
    return !(*this == other);
}

MazeGraph::NeighborIterator::reference MazeGraph::NeighborIterator::operator*() const {
    auto out_path = node_.out_paths[index_];
    out_path = rotateOutPath(out_path, node_.rotation);
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
        out_path = rotateOutPath(out_path, node_.rotation);
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

MazeGraph::Neighbors::Neighbors(const MazeGraph & graph, const Location & location, const Node & node) noexcept :
    graph_{graph}, location_{location}, node_{node} {}

MazeGraph::NeighborIterator MazeGraph::Neighbors::begin() {
    return MazeGraph::NeighborIterator::begin(graph_, location_, node_);
}

MazeGraph::NeighborIterator MazeGraph::Neighbors::end() {
    return MazeGraph::NeighborIterator::end(graph_, location_, node_);
}

} // namespace graph

namespace std {

std::ostream & operator<<(std::ostream & os, const labyrinth::MazeGraph & graph) {
    const auto extent = graph.getExtent();
    std::string row_delimiter(extent * 4, '-');
    for (size_t row = 0; row < extent; row++) {
        std::array<std::string, 3> lines = {std::string(extent * 4, '#'), std::string(extent * 4, '#'), std::string(extent * 4, '#')};
        for (size_t column = 0; column < extent; column++) {
            if (graph.hasOutPath(labyrinth::Location(row, column), 'N')) {
                lines[0][column * 4 + 1] = '.';
            }
            if (graph.hasOutPath(labyrinth::Location(row, column), 'E')) {
                lines[1][column * 4 + 2] = '.';
            }
            if (graph.hasOutPath(labyrinth::Location(row, column), 'S')) {
                lines[2][column * 4 + 1] = '.';
            }
            if (graph.hasOutPath(labyrinth::Location(row, column), 'W')) {
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
}

