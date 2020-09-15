#include "graphbuilder/text_graph_builder.h"

#include "libexhsearch/exhsearch.h"
#include "libexhsearch/location.h"
#include "libexhsearch/maze_graph.h"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <regex>
#include <string>

using namespace labyrinth;

namespace fs = std::filesystem;

using FracSeconds = std::chrono::duration<double>;

static void show_usage(std::string name) {
    std::cerr << "Usage: " << name << " INSTANCE_FOLDER OUT_CSV" << std::endl
              << "Where: " << std::endl
              << "\tINSTANCE_FOLDER\t\tcontains files ending with .txt in a specific format." << std::endl
              << "\tOUT_CSV\t\t\twill be created by the benchmark and will contain the results." << std::endl;
}

struct BenchmarkInstance {
    std::string name{};
    size_t depth;
    std::vector<std::string> maze_text{};
    Location objective{0, 0};
    std::vector<Location> player_locations{};
    std::string leftover_outpath_string{};
};

NodeId objective_id_from_location(const MazeGraph& graph, Location instance_objective_location) {
    if (instance_objective_location == Location(-1, -1)) {
        return graph.getLeftover().node_id;
    } else {
        return graph.getNode(instance_objective_location).node_id;
    }
}

std::vector<FracSeconds> benchmark(const BenchmarkInstance& instance, size_t repeats) {
    std::cout << "Benchmarking instance " << instance.name << std::endl;
    TextGraphBuilder builder;
    builder.setMaze(instance.maze_text).withStandardShiftLocations().setLeftoverOutPaths(instance.leftover_outpath_string);
    std::vector<FracSeconds> result{};
    for (size_t run = 0; run < repeats; run++) {
        const MazeGraph& graph = builder.buildGraph();
        auto objective_id = objective_id_from_location(graph, instance.objective);
        Location player_location = instance.player_locations[0];
        const auto start = std::chrono::steady_clock::now();
        auto best_actions = exhsearch::findBestActions(graph, player_location, objective_id);
        const auto stop = std::chrono::steady_clock::now();
        const FracSeconds duration = FracSeconds(stop - start);
        result.push_back(duration);
        if (best_actions.size() != instance.depth) {
            std::cerr << "Search depth mismatch for instance " << instance.name << ", expected " << instance.depth
                      << ", found" << best_actions.size() << std::endl;
        }
    }
    return result;
}

Location read_location(std::istream& stream) {
    Location::IndexType row, column;
    stream >> row >> column >> std::ws;
    return Location{row, column};
}

size_t extract_depth(const std::string& instance_name) {
    std::smatch depth_match;
    std::regex depth_regex{"_d([0-9]+)"};
    if (std::regex_search(instance_name, depth_match, depth_regex)) {
        return std::stoi(depth_match[1]);
    }
    return 0;
}

BenchmarkInstance read_instance(const fs::path instance_path) {
    std::ifstream instance_file(instance_path);
    BenchmarkInstance benchmark_instance;
    std::getline(instance_file, benchmark_instance.name);
    benchmark_instance.depth = extract_depth(benchmark_instance.name);
    MazeGraph::ExtentType graph_extent;
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
        benchmark_instance.player_locations.push_back(read_location(instance_file));
    }
    benchmark_instance.objective = read_location(instance_file);
    return benchmark_instance;
}

void write_header(const fs::path filename, const size_t repeats) {
    std::ofstream outfile{filename};
    if (outfile.is_open()) {
        outfile << "instance";
        for (size_t i = 0; i < repeats; i++) {
            outfile << ",time" << i << "[s]";
        }
        outfile << std::endl;
        outfile.close();
    }
}

void append_csv(const fs::path filename, const std::string& instance_name, const std::vector<FracSeconds>& durations) {
    std::ofstream outfile{filename, std::ios::app | std::ios::out};
    if (outfile.is_open()) {
        outfile << instance_name;
        for (auto duration : durations) {
            outfile << "," << duration.count();
        }
        outfile << std::endl;
        outfile.close();
    }
}

void run(const std::string& instance_folder, const std::string& out_filename) {
    const size_t repeats = 10;
    write_header(out_filename, repeats);
    for (const auto& file : fs::directory_iterator(instance_folder)) {
        if (file.is_regular_file() && file.path().extension() == ".txt") {
            const BenchmarkInstance instance = read_instance(file.path());
            std::vector<FracSeconds> durations = benchmark(instance, repeats);
            append_csv(out_filename, instance.name, durations);
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << argc << std::endl;
        show_usage(argv[0]);
        return 1;
    }
    run(argv[1], argv[2]);
    return 0;
}
