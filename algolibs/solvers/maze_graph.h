#pragma once

#include "location.h"

#include <string>
#include <vector>

namespace labyrinth {

using NodeId = unsigned int;

using RotationDegreeIntegerType = uint8_t;
enum class RotationDegreeType : RotationDegreeIntegerType { _0 = 0, _90 = 1, _180 = 2, _270 = 3 };

RotationDegreeType nextRotation(RotationDegreeType rotation);

using OutPathsIntegerType = uint8_t;
enum class OutPaths : OutPathsIntegerType { North = 1, East = 2, South = 4, West = 8 };

struct Node {
    NodeId node_id{0};
    OutPaths out_paths{static_cast<OutPaths>(0)};
    RotationDegreeType rotation{RotationDegreeType::_0};
};

bool hasOutPath(const Node& node, OutPaths out_path);

/// This class models a graph which represents a maze.
/// To construct such a graph, first construct an empty Graph with a fixed size.
/// Then set the maze cell at each location. A maze cell is defined by a String over the alphabet {N,S,E,W}.
class MazeGraph {
private:
    class NeighborIterator;

public:
    using SizeType = size_t;
    using ExtentType = int32_t;

    /// Constructor takes one argument, the extent of the quadratic maze in both directions.
    explicit MazeGraph(ExtentType extent);

    // Constructor argument is expected to be of size extent*extent + 1,
    // and specify the row-wise nodes of the maze. The last entry is the leftover.
    // node ids are expected to be unique.
    explicit MazeGraph(const std::vector<Node>& nodes);

    void setOutPaths(const Location& location, OutPaths out_paths);

    void addShiftLocation(const Location& location);

    void setLeftoverOutPaths(OutPaths out_paths);

    const Node& getNode(const Location& location) const {
        return node_matrix_[location.getRow() * extent_ + location.getColumn()];
    }

    Node& getNode(const Location& location) { return node_matrix_[location.getRow() * extent_ + location.getColumn()]; }

    const Node& getLeftover() const { return leftover_; }

    void shift(const Location& location, RotationDegreeType leftover_rotation);

    const std::vector<Location>& getShiftLocations() const noexcept { return shift_locations_; };

    /// Returns the location of a given node identifier.
    /// If the location cannot be found in the maze, the second parameter is returned.
    Location getLocation(NodeId node_id, const Location& leftover_location) const;

    /// returns an iterator over neighboring locations.
    NeighborIterator neighbors(const Location& location) const;

    SizeType getNumberOfNodes() const noexcept;

    ExtentType getExtent() const noexcept;

private:
    using OffsetType = Location::OffsetType;

    class NeighborIterator {
    public:
        NeighborIterator(OutPaths current_out_path, const MazeGraph& graph, const Location& location, const Node& node) :
            current_out_path_{current_out_path}, graph_{graph}, location_{location}, node_{node} {
            moveToNextNeighbor();
        };
        static NeighborIterator begin(const MazeGraph& graph, const Location& location, const Node& node);

        Location operator*() const;

        NeighborIterator& operator++();
        NeighborIterator operator++(int);

        bool isAtEnd() const;

    private:
        static constexpr auto sentinel_ = static_cast<OutPathsIntegerType>(OutPaths::West) << 1;

        void moveToNextNeighbor();

        bool isNeighbor(OutPaths out_path) const;

        OutPaths current_out_path_;
        const MazeGraph& graph_;
        const Location location_;
        const Node& node_;
    };

    bool isInside(const Location& location) const {
        return (location.getRow() >= 0) && (location.getColumn() >= 0) && (location.getRow() < extent_) &&
               (location.getColumn() < extent_);
    }

    SizeType size_;
    ExtentType extent_;
    Node leftover_;
    std::vector<Node> node_matrix_;
    std::vector<Location> shift_locations_;
};

Location::OffsetType getOffsetByShiftLocation(const Location& shift_location, MazeGraph::ExtentType extent) noexcept;

Location opposingShiftLocation(const Location& location, MazeGraph::ExtentType extent) noexcept;

Location translateLocationByShift(const Location& location,
                                  const Location& shift_location,
                                  MazeGraph::ExtentType extent) noexcept;

} // namespace labyrinth

namespace std {
std::ostream& operator<<(std::ostream& os, const labyrinth::MazeGraph& graph);
std::ostream& operator<<(std::ostream& os, labyrinth::RotationDegreeType rotation);
}
