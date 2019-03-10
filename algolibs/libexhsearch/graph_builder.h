#pragma once
#include "static_graph.h"

#include <string>
#include <vector>

namespace graph {

namespace mazes {
extern std::vector<std::string> big_component_maze_9;
} // namespace mazes

class GraphBuilder {
public:
	static StaticGraph buildGraphFromText(std::vector<std::string> lines);
private:
	static size_t first(size_t maze_index) { return maze_index * 4; }
	static size_t second(size_t maze_index) { return maze_index * 4 + 1; }
	static size_t third(size_t maze_index) { return maze_index * 4 + 2; }
};

}