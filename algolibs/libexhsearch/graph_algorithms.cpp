#include "graph_algorithms.h"

#include "static_graph.h"
#include <queue>

namespace graph {
namespace algorithm {

bool isReachable(const StaticGraph & graph, const Location & source, const Location & target) {
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

} // namespace algorithm
} // namespace graph

