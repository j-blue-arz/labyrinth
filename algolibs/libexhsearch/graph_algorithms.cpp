#include "graph_algorithms.h"

#include <limits>
#include <queue>
#include <unordered_map>

namespace labyrinth {
namespace reachable {

bool isReachable(const MazeGraph& graph, const Location& source, const Location& target) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes() + 1, false);
    q.push(source);
    while (!q.empty()) {
        auto location = q.front();
        if (location == target) {
            return true;
        }
        q.pop();
        visited[graph.getNode(location).node_id] = true;
        for (const auto& neighbor_location : graph.neighbors(location)) {
            if (!visited[graph.getNode(neighbor_location).node_id]) {
                q.push(neighbor_location);
            }
        }
    }
    return false;
}

std::vector<Location> reachableLocations(const MazeGraph& graph, const Location& source) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes() + 1, false);
    q.push(source);
    visited[graph.getNode(source).node_id] = true;
    std::vector<Location> result;
    while (!q.empty()) {
        auto location = q.front();
        result.push_back(location);
        q.pop();
        visited[graph.getNode(location).node_id] = true;
        for (const auto& neighbor_location : graph.neighbors(location)) {
            if (!visited[graph.getNode(neighbor_location).node_id]) {
                q.push(neighbor_location);
            }
        }
    }
    return result;
}

std::vector<ReachableNode> multiSourceReachableLocations(const MazeGraph& graph, const std::vector<Location>& sources) {
    constexpr size_t no_parent = std::numeric_limits<size_t>::max();
    std::queue<Location> q;
    std::vector<size_t> parent_index(graph.getNumberOfNodes() + 1, no_parent);
    for (size_t i = 0; i < sources.size(); ++i) {
        q.push(sources[i]);
        parent_index[graph.getNode(sources[i]).node_id] = i;
    }
    while (!q.empty()) {
        auto location = q.front();
        q.pop();
        for (const auto& neighbor_location : graph.neighbors(location)) {
            if (no_parent == parent_index[graph.getNode(neighbor_location).node_id]) {
                parent_index[graph.getNode(neighbor_location).node_id] = parent_index[graph.getNode(location).node_id];
                q.push(neighbor_location);
            }
        }
    }
    std::vector<ReachableNode> result;
    result.reserve(sources.size());
    for (NodeId node_id = 0; node_id < parent_index.size(); ++node_id) {
        if (no_parent != parent_index[node_id]) {
            result.emplace_back(parent_index[node_id], node_id);
        }
    }
    return result;
}

} // namespace reachable
} // namespace labyrinth
