#pragma once

#include "graphbuilder/text_graph_builder.h"

#include "solvers/location.h"

#include <filesystem>
#include <fstream>
#include <regex>
#include <string>

namespace fs = std::filesystem;
namespace bench {

struct BenchmarkInstance {
    std::string name{};
    size_t depth;
    std::vector<std::string> maze_text{};
    labyrinth::Location objective{0, 0};
    std::vector<labyrinth::Location> player_locations{};
    std::string leftover_outpath_string{};
};

namespace reader {
namespace { // anonymous namespace for file-internal linkage

size_t extractDepth(const std::string& instance_name) {
    std::smatch depth_match;
    std::regex depth_regex{"_d([0-9]+)"};
    if (std::regex_search(instance_name, depth_match, depth_regex)) {
        return std::stoi(depth_match[1]);
    }
    return 0;
}

labyrinth::Location readLocation(std::istream& stream) {
    labyrinth::Location::IndexType row, column;
    stream >> row >> column >> std::ws;
    return labyrinth::Location{row, column};
}

} // namespace

BenchmarkInstance readInstance(const fs::path instance_path) {
    std::ifstream instance_file(instance_path);
    BenchmarkInstance benchmark_instance;
    std::getline(instance_file, benchmark_instance.name);
    benchmark_instance.depth = extractDepth(benchmark_instance.name);
    labyrinth::MazeGraph::ExtentType graph_extent;
    size_t num_players;
    instance_file >> graph_extent >> num_players >> std::ws;
    benchmark_instance.maze_text.reserve(graph_extent * 4);
    for (auto i = 0; i < graph_extent * 4; i++) {
        std::string line;
        std::getline(instance_file, line);
        benchmark_instance.maze_text.push_back(line);
    }
    std::getline(instance_file, benchmark_instance.leftover_outpath_string);
    for (auto i = 0u; i < num_players; i++) {
        benchmark_instance.player_locations.push_back(readLocation(instance_file));
    }
    benchmark_instance.objective = readLocation(instance_file);
    return benchmark_instance;
}

labyrinth::NodeId objectiveIdFromLocation(const labyrinth::MazeGraph& graph,
                                          labyrinth::Location instance_objective_location) {
    if (instance_objective_location == labyrinth::Location(-1, -1)) {
        return graph.getLeftover().node_id;
    } else {
        return graph.getNode(instance_objective_location).node_id;
    }
}

labyrinth::MazeGraph buildMazeGraph(const BenchmarkInstance& benchmark_instance) {
    labyrinth::TextGraphBuilder builder{};
    return builder.setMaze(benchmark_instance.maze_text)
        .withStandardShiftLocations()
        .withLeftoverOutPaths(benchmark_instance.leftover_outpath_string)
        .buildGraph();
}

} // namespace reader
} // namespace bench
