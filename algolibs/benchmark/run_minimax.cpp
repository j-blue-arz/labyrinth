#include "solvers/evaluators.h"
#include "solvers/location.h"
#include "solvers/maze_graph.h"
#include "solvers/minimax.h"

#include "benchmark/benchmark_reader.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

using namespace labyrinth;

namespace mm = solvers::minimax;

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
    Location opponent_location = instance.player_locations[1];
    solvers::SolverInstance solver_instance{
        graph, player_location, opponent_location, objective_id, labyrinth::Location{-1, -1}};
    auto minimax_result = mm::findBestAction(solver_instance, mm::WinEvaluator{solver_instance}, instance.depth);
    if (minimax_result.player_action.move_location == labyrinth::solvers::error_player_action.move_location) {
        std::cerr << "Error returned for " << instance.name << std::endl;
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
