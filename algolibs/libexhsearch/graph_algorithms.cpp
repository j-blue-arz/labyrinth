#include "graph_algorithms.h"

#include <limits>
#include <queue>

namespace graph {
namespace reachable {

bool isReachable(const MazeGraph & graph, const Location & source, const Location & target) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes() + 1, false);
    q.push(source);
    while (!q.empty()) {
        auto location = q.front();
        if (location == target) {
            return true;
        }
        q.pop();
        visited[graph.getNodeId(location)] = true;
        for (auto neighbor_location : graph.neighbors(location)) {
            if (!visited[graph.getNodeId(neighbor_location)]) {
                q.push(neighbor_location);
            }
        }
    }
    return false;
}

std::vector<Location> reachableLocations(const MazeGraph & graph, const Location & source) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes() + 1, false);
    q.push(source);
    visited[graph.getNodeId(source)] = true;
    std::vector<Location> result;
    while (!q.empty()) {
        auto location = q.front();
        result.push_back(location);
        q.pop();
        visited[graph.getNodeId(location)] = true;
        for (auto neighbor_location : graph.neighbors(location)) {
            if (!visited[graph.getNodeId(neighbor_location)]) {
                q.push(neighbor_location);
            }
        }
    }
    return result;
}

std::vector<ReachableNode> multiSourceReachableLocations(const MazeGraph & graph, const std::vector<Location> & sources) {
    const size_t no_parent = std::numeric_limits<size_t>::max();
    std::queue<Location> q;
    std::vector<size_t> parent_index(graph.getNumberOfNodes() + 1, no_parent);
    for(size_t i = 0; i < sources.size(); ++i) {
        q.push(sources[i]);
        parent_index[graph.getNodeId(sources[i])] = i;
    }
    while(!q.empty()) {
        auto location = q.front();
        q.pop();
        for(auto neighbor_location : graph.neighbors(location)) {
            if(no_parent == parent_index[graph.getNodeId(neighbor_location)]) {
                parent_index[graph.getNodeId(neighbor_location)] = parent_index[graph.getNodeId(location)];
                q.push(neighbor_location);
            }
        }
    }
    std::vector<ReachableNode> result;
    for(MazeGraph::NodeId node_id = 0; node_id < parent_index.size(); ++node_id) {
        if(no_parent != parent_index[node_id]) {
            result.emplace_back(parent_index[node_id], node_id);
        }
    }
    return result;
}

} // namespace algorithm
} // namespace graph

