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
    const bench::BenchmarkInstance instance = bench::reader::readInstance(filename);
    MazeGraph graph = bench::reader::buildMazeGraph(instance);
    auto objective_id = bench::reader::objectiveIdFromLocation(graph, instance.objective);
    Location player_location = instance.player_locations[0];
    solvers::SolverInstance solver_instance{graph, player_location, Location{-1, -1}, objective_id, Location{-1, -1}};
    auto best_actions = solvers::exhsearch::findBestActions(solver_instance);
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
