#include "graph_builder.h"
#include "graph_algorithms.h"
#include "location.h"
#include "static_graph.h"

#include <iostream>

using namespace graph;

int main(int argc, char* argv[])
{
	const StaticGraph graph = GraphBuilder::buildGraphFromText(mazes::big_component_maze_9);
	bool reachable = algorithm::isReachable(graph, Location(7, 8), Location(7, 7));
	std::cout << (reachable ? "is reachable" : "not reachable") << std::endl;
	std::cout << "Enter to exit." << std::endl;
	std::cin.ignore();
}