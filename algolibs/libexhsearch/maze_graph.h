#pragma once

#include "location.h"

#include <string>
#include <unordered_set>
#include <vector>


namespace labyrinth {

using NodeId = unsigned int;
using RotationDegreeType = int16_t;

using OutPathsIntegerType = uint8_t;
enum class OutPaths : OutPathsIntegerType {
    North = 1,
    East = 2,
    South = 4,
    West = 8
};

struct Node {
    NodeId node_id{0};
    OutPaths out_paths{static_cast<OutPaths>(0)};
    RotationDegreeType rotation{0};
};

bool hasOutPath(const Node & node, OutPaths out_path);

/// This class models a graph which represents a maze.
/// To construct such a graph, first construct an empty Graph with a fixed size.
/// Then set the maze cell at each location. A maze cell is defined by a String over the alphabet {N,S,E,W}.
class MazeGraph {
private:
    class Neighbors;
public:
    using SizeType = size_t;
    using ExtentType = int32_t;

    /// Constructor takes one argument, the extent of the quadratic maze in both directions.
    explicit MazeGraph(ExtentType extent);

    // Constructor argument is expected to be of size extent*extent + 1,
    // and specify the row-wise nodes of the maze. The last entry is the leftover.
    // node ids are expected to be unique.
    explicit MazeGraph(const std::vector<Node> & nodes);

    void setOutPaths(const Location & location, OutPaths out_paths);

    void addShiftLocation(const Location & location);

    void setLeftoverOutPaths(OutPaths out_paths);

    const Node & getNode(const Location & location) const {
        return node_matrix_[location.getRow() * extent_ + location.getColumn()];
    }

    Node & getNode(const Location & location) {
        return node_matrix_[location.getRow() * extent_ + location.getColumn()];
    }

    const Node & getLeftover() const {
        return leftover_;
    }

    const std::vector<Location> & getShiftLocations() const noexcept { return shift_locations_; };

    void shift(const Location & location, RotationDegreeType leftoverRotation);

    /// Returns the location of a given node identifier.
    /// If the location cannot be found in the maze, the second parameter is returned.
    Location getLocation(NodeId node_id, const Location & leftover_location) const;

    /// returns a range over neighboring locations.
    /// The returned object which has two member functions begin() and end(), so
    /// that it can be used in range-based for loop, e.g.
    /// for (auto neighbor_location : graph.neighbors(Location(0, 0))) { ... }
    Neighbors neighbors(const Location & location) const;

    SizeType getNumberOfNodes() const noexcept;

    ExtentType getExtent() const noexcept;

private:
    using OffsetType = Location::OffsetType;

    class NeighborIterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = Location;
        using difference_type = std::ptrdiff_t;
        using reference = Location;
        using pointer = void;

        static NeighborIterator begin(const MazeGraph & graph, const Location & location, const Node & node);
        static NeighborIterator end(const MazeGraph & graph, const Location & location, const Node & node);

        bool operator==(const NeighborIterator & other) const noexcept;
        bool operator!=(const NeighborIterator & other) const noexcept;

        reference operator*() const;
        pointer operator->() = delete;

        NeighborIterator & operator++();
        NeighborIterator operator++(int);
    private:
        NeighborIterator(OutPaths current_out_path, const MazeGraph & graph, const Location & location, const Node & node) :
            current_out_path_{current_out_path}, graph_{graph}, location_{location}, node_{node} {
            moveToNextNeighbor();
        };

        void moveToNextNeighbor();

        bool isNeighbor(OutPaths out_path);

        OutPaths current_out_path_;
        const MazeGraph & graph_;
        const Location location_;
        const Node & node_;
    };

    class Neighbors {
    public:
        explicit Neighbors(const MazeGraph & graph, const Location & location, const Node & node) noexcept;

        NeighborIterator begin();
        NeighborIterator end();

    private:
        const MazeGraph & graph_;
        const Location & location_;
        const Node & node_;
    };

    bool isInside(const Location & location) const {
        return (location.getRow() >= 0) &&
            (location.getColumn() >= 0) &&
            (location.getRow() < extent_) &&
            (location.getColumn() < extent_);
    }

    SizeType size_;
    ExtentType extent_;
    Node leftover_;
    std::vector<Node> node_matrix_;
    std::vector<Location> shift_locations_;
};

} // namespace labyrinth

namespace std {
std::ostream & operator<<(std::ostream & os, const labyrinth::MazeGraph & graph);
}

