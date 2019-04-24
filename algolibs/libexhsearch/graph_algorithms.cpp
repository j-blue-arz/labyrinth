#include "graph_algorithms.h"

#include <queue>

namespace graph {
namespace algorithm {

bool isReachable(const MazeGraph & graph, const Location & source, const Location & target) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes(), false);
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
    std::vector<bool> visited(graph.getNumberOfNodes(), false);
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

std::vector<Location> reachableLocations(const MazeGraph & graph, const std::vector<Location> & sources) {
    std::queue<Location> q;
    std::vector<bool> visited(graph.getNumberOfNodes(), false);
    for(auto source : sources) {
        q.push(source);
        visited[graph.getNodeId(source)] = true;
    }
    std::vector<Location> result;
    while(!q.empty()) {
        auto location = q.front();
        result.push_back(location);
        q.pop();
        visited[graph.getNodeId(location)] = true;
        for(auto neighbor_location : graph.neighbors(location)) {
            if(!visited[graph.getNodeId(neighbor_location)]) {
                q.push(neighbor_location);
            }
        }
    }
    return result;
}

} // namespace algorithm
} // namespace graph

