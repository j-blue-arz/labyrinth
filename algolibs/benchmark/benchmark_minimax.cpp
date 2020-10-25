#include "benchmark/benchmark.h"
#include "solvers/evaluators.h"
#include "solvers/location.h"
#include "solvers/maze_graph.h"
#include "solvers/minimax.h"

#include <vector>

namespace bench {

class MinimaxBenchmark : public AlgolibsBenchmark {
protected:
    std::vector<FracSeconds> benchmark(const BenchmarkInstance& instance, size_t repeats) const override {
        std::cout << "Benchmarking instance " << instance.name << std::endl;
        MazeGraph graph = reader::buildMazeGraph(instance);
        auto objective_id = reader::objectiveIdFromLocation(graph, instance.objective);
        Location player_location = instance.player_locations[0];
        Location opponent_location = instance.player_locations[1];
        solvers::SolverInstance solver_instance{
            graph, player_location, opponent_location, objective_id, labyrinth::Location{-1, -1}};
        std::vector<FracSeconds> result{};
        for (size_t run = 0; run < repeats; run++) {
            const auto start = std::chrono::steady_clock::now();
            const auto minimax_result = solvers::minimax::findBestAction(
                solver_instance, solvers::minimax::WinEvaluator{solver_instance}, instance.depth);
            const auto stop = std::chrono::steady_clock::now();
            const FracSeconds duration = FracSeconds(stop - start);
            result.push_back(duration);
            if (minimax_result.player_action.move_location == solvers::error_player_action.move_location) {
                std::cerr << "Error returned for " << instance.name << std::endl;
            }
        }
        return result;
    }
};

} // namespace bench

int main(int argc, char* argv[]) {
    if (argc < 3) {
        show_usage(argv[0]);
        return 1;
    }
    auto benchmark = bench::MinimaxBenchmark{};
    benchmark.run(argv[1], argv[2]);
    return 0;
}