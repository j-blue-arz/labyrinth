#include "graph_algorithms.h"

#include <limits>
#include <queue>
#include <unordered_map>

namespace labyrinth {
namespace reachable {

bool isReachable(const MazeGraph& graph, const Location& source, const Location& target) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes(), false);
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
    std::vector<bool> visited(graph.getNumberOfNodes(), false);
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
    std::vector<ReachableNode> result;
    result.reserve(sources.size());
    std::vector<size_t> parent_indices(graph.getNumberOfNodes(), no_parent);
    std::queue<Location> q;
    for (size_t i = 0; i < sources.size(); ++i) {
        q.push(sources[i]);
        parent_indices[graph.getNode(sources[i]).node_id] = i;
        result.emplace_back(i, sources[i]);
    }
    while (!q.empty()) {
        auto location = q.front();
        auto parent_index = parent_indices[graph.getNode(location).node_id];
        q.pop();
        for (const auto& neighbor_location : graph.neighbors(location)) {
            if (no_parent == parent_indices[graph.getNode(neighbor_location).node_id]) {
                parent_indices[graph.getNode(neighbor_location).node_id] = parent_index;
                q.push(neighbor_location);
                result.emplace_back(parent_index, neighbor_location);
            }
        }
    }
    return result;
}

} // namespace reachable
} // namespace labyrinth
