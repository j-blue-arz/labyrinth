#include "graph_builder.h"
#include "graph_algorithms.h"
#include "location.h"
#include "static_graph.h"

#include <iostream>
#include <chrono>
#include <random>

using namespace graph;
using namespace std::chrono;

void runQueries(const StaticGraph & graph, std::vector<std::pair<Location, Location>> & queries) {
    volatile bool reachable;
    for (const auto & pair : queries) {
        reachable &= algorithm::isReachable(graph, pair.first, pair.second);
    }
}

std::vector<std::pair<Location, Location>> createSnakeGraphQueries(int extent, size_t number)
{
    std::default_random_engine rng;
    std::uniform_int_distribution<int> dist(0, extent - 1);
    std::vector<std::pair<Location, Location>> queries;
    queries.reserve(number);
    for (auto i = 0; i < number / 2; i++) {
        queries.push_back(std::make_pair(Location(0, dist(rng)), Location(extent - 1, dist(rng))));
        queries.push_back(std::make_pair(Location(extent - 1, dist(rng)), Location(0, dist(rng))));
    }
    std::random_shuffle(queries.begin(), queries.end());
    return queries;
}

void benchmarkSnakeGraph(size_t runs = 3, size_t number = 1000, const std::initializer_list<size_t> & extents = { 7, 14, 28 }) {
    for (auto extent : extents) {
        std::cout << "Benchmarking isReachable() for snake graph with extent " << extent << ", " 
            << "running " << number << " queries, " << runs << " times." << std::endl;
        const StaticGraph & graph = GraphBuilder::buildSnakeGraph(extent);
        // warmup
        std::vector<std::pair<Location, Location>> queries = createSnakeGraphQueries(extent, number);
        runQueries(graph, queries);
        auto best = high_resolution_clock::duration::max();
        for (size_t run = 0; run < runs; run++) {
            queries = createSnakeGraphQueries(extent, number);
            auto start = high_resolution_clock::now();
            runQueries(graph, queries);
            auto stop = high_resolution_clock::now();
            auto duration = duration_cast<milliseconds>(stop - start);
            if (best > duration) {
                best = duration;
            }
        }
        auto perQuery = duration_cast<microseconds>(best / number);
        std::cout << "Best run took " << perQuery.count() << "us per query." << std::endl;
    }
    
}



int main(int argc, char* argv[]) {
    benchmarkSnakeGraph(10, 2000, {28});
    std::cout << "Enter to exit." << std::endl;
    std::cin.ignore();
}