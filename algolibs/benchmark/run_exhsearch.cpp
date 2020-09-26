#include "solvers/exhsearch.h"
#include "solvers/location.h"
#include "solvers/maze_graph.h"

#include "benchmark/benchmark_reader.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

using namespace labyrinth;

namespace fs = std::filesystem;

static void show_usage(const std::string& name) {
    std::cerr << "Usage: " << name << " INSTANCE_FILE" << std::endl
              << "Where: " << std::endl
              << "\tINSTANCE_FILE\t\tis a file ending with .txt in a specific format." << std::endl;
}

void run(const std::string& filename) {
    const BenchmarkInstance instance = readInstance(filename);
    MazeGraph graph = buildMazeGraph(instance);
    auto objective_id = objectiveIdFromLocation(graph, instance.objective);
    Location player_location = instance.player_locations[0];
    auto best_actions = exhsearch::findBestActions(graph, player_location, objective_id);
    if (best_actions.size() != instance.depth) {
        std::cerr << "Search depth mismatch for instance " << instance.name << ", expected " << instance.depth
                  << ", found" << best_actions.size() << std::endl;
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        show_usage(argv[0]);
        return 1;
    }
    run(argv[1]);
    return 0;
}
