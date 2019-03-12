#pragma once

#include "location.h"

#include <vector>
#include <string>

namespace graph {
/// This class models a graph which represents a maze.
/// To construct such a graph, first construct an empty StaticGraph with a fixed size.
/// Then set the maze cell at each location. A maze cell is defined by a String over the alphabet {N,S,E,W}.
class StaticGraph {
public:
    using NodeId = unsigned int;

    /// Constructor takes one argument, the extent of the quadratic maze in both directions.
    explicit StaticGraph(size_t extent);

    void setOutPaths(const Location & location, const std::string & out_paths);

    NodeId getNodeId(const Location & location) const;

    std::vector<Location> neighbors(const Location & location) const;

    size_t getNumberOfNodes() const noexcept;

    size_t getExtent() const noexcept;

private:
    using OffsetType = Location::OffsetType;
    using OutPathType = std::string::value_type;

    struct Node {
        std::string out_paths{ "" };
        NodeId node_id{0};
    };

    const Node & getNode(const Location & location) const;
    Node & getNode(const Location & location);

    bool hasOutPath(const Node & node, const OutPathType & out_path) const noexcept;

    bool isInRange(const Location & location) const noexcept;

    static OutPathType mirrorOutPath(OutPathType out_path) noexcept;

    static OffsetType offsetFromOutPath(OutPathType out_path) noexcept;

    size_t extent_;
    std::vector<std::vector<Node>> node_matrix_;
};
} // namespace graph