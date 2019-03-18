#pragma once

#include "location.h"

#include <vector>
#include <string>

namespace graph {
/// This class models a graph which represents a maze.
/// To construct such a graph, first construct an empty StaticGraph with a fixed size.
/// Then set the maze cell at each location. A maze cell is defined by a String over the alphabet {N,S,E,W}.
class StaticGraph {
private:
    class Neighbors;
public:
    using NodeId = unsigned int;

    /// Constructor takes one argument, the extent of the quadratic maze in both directions.
    explicit StaticGraph(size_t extent);

    void setOutPaths(const Location & location, const std::string & out_paths);

    NodeId getNodeId(const Location & location) const;

    /// returns a range over neighboring locations. 
    /// The returned object which has two member functions begin() and end(), so 
    /// that it can be used in range-based for loop, e.g.
    /// for (auto neighbor_location : graph.neighbors(Location(0, 0))) { ... }
    Neighbors neighbors(const Location & location) const;

    size_t getNumberOfNodes() const noexcept;

    size_t getExtent() const noexcept;

private:
    using OffsetType = Location::OffsetType;
    using OutPathType = std::string::value_type;

    struct Node {
        std::string out_paths{ "" };
        NodeId node_id{ 0 };
    };

    class NeighborIterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = Location;
        using difference_type = std::ptrdiff_t;
        using reference = Location;
        using pointer = void;

        static NeighborIterator begin(const StaticGraph & graph, const Location & location, const Node & node);
        static NeighborIterator end(const StaticGraph & graph, const Location & location, const Node & node);

        bool operator==(const NeighborIterator & other) const noexcept;
        bool operator!=(const NeighborIterator & other) const noexcept;

        reference operator*() const;
        pointer operator->() = delete;

        NeighborIterator& operator++();
        NeighborIterator operator++(int);
    private:
        using NeighborIndex = unsigned int;
        NeighborIterator(NeighborIndex index, const StaticGraph & graph, const Location & location, const Node & node) :
            index_(index), graph_(graph), location_(location), node_(node) {
            moveToNextNeighbor();
        };

        void moveToNextNeighbor();

        NeighborIndex index_;
        const StaticGraph & graph_;
        const Location & location_;
        const Node & node_;
    };

    class Neighbors {
    public:
        explicit Neighbors(const StaticGraph & graph, const Location & location, const Node & node);

        NeighborIterator begin();
        NeighborIterator end();

    private:
        
        const StaticGraph & graph_;
        const Location & location_;
        const Node & node_;
    };

    const Node & getNode(const Location & location) const;
    Node & getNode(const Location & location);

    bool hasOutPath(const Node & node, const OutPathType & out_path) const noexcept;

    bool isInside(const Location & location) const noexcept;

    static OutPathType mirrorOutPath(OutPathType out_path) noexcept;

    static OffsetType offsetFromOutPath(OutPathType out_path) noexcept;

    size_t extent_;
    std::vector<std::vector<Node>> node_matrix_;
};
} // namespace graph
