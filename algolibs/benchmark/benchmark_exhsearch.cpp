#include "graphbuilder/text_graph_builder.h"

#include "libexhsearch/exhsearch.h"
#include "libexhsearch/location.h"
#include "libexhsearch/maze_graph.h"

#include "test/mazes.h"

#include <iostream>
#include <chrono>

using namespace labyrinth;

std::chrono::milliseconds benchmarkSearch(const MazeGraph & graph, const Location & source, int objective_id) {
    const auto start = std::chrono::high_resolution_clock::now();
    auto best_actions = exhsearch::findBestActions(graph, source, objective_id);
    const auto stop = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
}

void benchmark(size_t runs = 3) {
    TextGraphBuilder builder;
    builder.setMaze(mazes::exh_depth_4_maze);
    builder.withStandardShiftLocations();
    auto best = std::chrono::high_resolution_clock::duration::max();
    for (size_t run = 0; run < runs; run++) {
        const MazeGraph & graph = builder.buildGraph();
        auto objective_id = graph.getNode(Location{6, 7}).node_id;
        Location player_location{4, 2};
        auto duration = benchmarkSearch(graph, player_location, objective_id);
        if (best > duration) {
            best = duration;
        }
    }
    auto best_s = (std::chrono::duration_cast<std::chrono::milliseconds>(best)).count() / 1000.0;
    std::cout << "Best of " << runs << ": " << best_s << "s." << std::endl;
}



int main() {
    benchmark(5);
    std::cout << "Enter to exit." << std::endl;
    std::cin.ignore();
}
