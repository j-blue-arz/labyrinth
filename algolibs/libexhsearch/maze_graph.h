#pragma once

#include "location.h"

#include <string>
#include <unordered_set>
#include <vector>


namespace labyrinth {
/// This class models a graph which represents a maze.
/// To construct such a graph, first construct an empty Graph with a fixed size.
/// Then set the maze cell at each location. A maze cell is defined by a String over the alphabet {N,S,E,W}.
class MazeGraph {
private:
    class Neighbors;
public:
    using NodeId = unsigned int;
    using OutPathType = std::string::value_type;
    using RotationDegreeType = int16_t;

    struct InputNode {
        NodeId node_id{0};
        uint8_t out_paths_bit_mask{0};
        RotationDegreeType rotation{0};
    };

    /// Constructor takes one argument, the extent of the quadratic maze in both directions.
    explicit MazeGraph(size_t extent);

    // Constructor takes two arguments. Second argument is expected to be of size extent*extent + 1,
    // and specify the row-wise nodes of the maze. The last entry is the leftover.
    // node ids are expected to be unique.
    explicit MazeGraph(size_t extent, std::vector<InputNode> nodes);

    void setOutPaths(const Location & location, const std::string & out_paths);

    void addShiftLocation(const Location & location);

    void setLeftoverOutPaths(const std::string & out_paths);

    const std::vector<Location> & getShiftLocations() const noexcept { return shift_locations_; };

    void shift(const Location & location, RotationDegreeType leftoverRotation);

    bool hasOutPath(const Location & location, const OutPathType & out_path) const;

    bool leftoverHasOutPath(const OutPathType & out_path) const;

    NodeId getNodeId(const Location & location) const;

    NodeId getLeftoverNodeId() const noexcept;

    /// Returns the location of a given node identifier.
    /// If the location cannot be found in the maze, the second parameter is returned.
    Location getLocation(NodeId node_id, const Location & leftover_location) const;

    /// returns a range over neighboring locations. 
    /// The returned object which has two member functions begin() and end(), so 
    /// that it can be used in range-based for loop, e.g.
    /// for (auto neighbor_location : graph.neighbors(Location(0, 0))) { ... }
    Neighbors neighbors(const Location & location) const;

    size_t getNumberOfNodes() const noexcept;

    size_t getExtent() const noexcept;

private:
    using OffsetType = Location::OffsetType;

    struct Node {
        NodeId node_id{0};
        std::string out_paths{""};
        RotationDegreeType rotation{0};
    };

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
        using NeighborIndex = unsigned int;
        NeighborIterator(NeighborIndex index, const MazeGraph & graph, const Location & location, const Node & node) :
            index_{index}, graph_{graph}, location_{location}, node_{node} {
            moveToNextNeighbor();
        };

        void moveToNextNeighbor();

        NeighborIndex index_;
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

    const Node & getNode(const Location & location) const;
    Node & getNode(const Location & location);

    bool hasOutPath(const Node & node, const OutPathType & out_path) const;

    bool isInside(const Location & location) const noexcept;

    size_t extent_;
    Node leftover_;
    std::vector<Node> node_matrix_;
    std::vector<Location> shift_locations_;
};

} // namespace graph

namespace std {
std::ostream & operator<<(std::ostream & os, const labyrinth::MazeGraph & graph);
}

