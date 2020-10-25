#include "benchmark/benchmark.h"
#include "solvers/exhsearch.h"
#include "solvers/location.h"
#include "solvers/maze_graph.h"

#include <vector>

namespace bench {

class ExhsearchBenchmark : public AlgolibsBenchmark {
protected:
    std::vector<FracSeconds> benchmark(const BenchmarkInstance& instance, size_t repeats) const override {
        std::cout << "Benchmarking instance " << instance.name << std::endl;
        MazeGraph graph = reader::buildMazeGraph(instance);
        auto objective_id = reader::objectiveIdFromLocation(graph, instance.objective);
        Location player_location = instance.player_locations[0];
        solvers::SolverInstance solver_instance{graph, player_location, Location{-1, -1}, objective_id, Location{-1, -1}};
        std::vector<FracSeconds> result{};
        for (size_t run = 0; run < repeats; run++) {
            const auto start = std::chrono::steady_clock::now();
            auto best_actions = solvers::exhsearch::findBestActions(solver_instance);
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
};
} // namespace bench

int main(int argc, char* argv[]) {
    if (argc < 3) {
        show_usage(argv[0]);
        return 1;
    }
    auto benchmark = bench::ExhsearchBenchmark{};
    benchmark.run(argv[1], argv[2]);
    return 0;
}
