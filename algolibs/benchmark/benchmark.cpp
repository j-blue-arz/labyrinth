#include "graphbuilder/snake_graph_builder.h"
#include "graphbuilder/tree_graph_builder.h"

#include "libexhsearch/graph_algorithms.h"
#include "libexhsearch/location.h"
#include "libexhsearch/maze_graph.h"

#include <iostream>
#include <chrono>
#include <functional>
#include <random>

using namespace graph;
using namespace std::chrono;

using QuerySupplier = std::function<std::vector<std::pair<Location, Location>>()>;

void runQueries(const MazeGraph & graph, std::vector<std::pair<Location, Location>> & queries) {
    volatile bool reachable;
    for (const auto & pair : queries) {
        reachable &= algorithm::isReachable(graph, pair.first, pair.second);
    }
}


void runBenchmark(const MazeGraph & graph, size_t runs, QuerySupplier query_supplier) {
    // warmup
    std::vector<std::pair<Location, Location>> queries = query_supplier();
    size_t number = queries.size();
    runQueries(graph, queries);
    auto best = high_resolution_clock::duration::max();
    for (size_t run = 0; run < runs; run++) {
        queries = query_supplier();
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

std::vector<std::pair<Location, Location>> createSnakeGraphQueries(size_t extent, size_t number)
{
    std::default_random_engine rng;
    std::uniform_int_distribution<int> dist(0, static_cast<int>(extent - 1));
    std::vector<std::pair<Location, Location>> queries;
    queries.reserve(number);
    for (auto i = 0; i < number / 2; i++) {
        queries.push_back(std::make_pair(Location(0, dist(rng)), Location(extent - 1, dist(rng))));
        queries.push_back(std::make_pair(Location(extent - 1, dist(rng)), Location(0, dist(rng))));
    }
    std::random_shuffle(queries.begin(), queries.end());
    return queries;
}

std::vector<std::pair<Location, Location>> createTreeGraphQueries(size_t extent, size_t number) {
    std::vector<std::pair<Location, Location>> queries;
    std::default_random_engine rng;
    std::uniform_int_distribution<int> dist(0, static_cast<int>(extent - 2));
    queries.reserve(number);
    for (auto i = 0; i < number / 2; i++) {
        queries.push_back(std::make_pair(Location(extent - 1, dist(rng)), Location(dist(rng), 0)));
        queries.push_back(std::make_pair(Location(dist(rng), 0), Location(extent - 1, dist(rng))));
    }
    std::random_shuffle(queries.begin(), queries.end());
    return queries;
}

void benchmarkSnakeGraph(size_t runs = 3, size_t number = 1000, const std::initializer_list<size_t> & extents = { 7, 14, 28 }) {
    for (auto extent : extents) {
        std::cout << "Benchmarking isReachable() for snake graph with extent " << extent << ", "
            << "running " << number << " queries, " << runs << " times." << std::endl;
        SnakeGraphBuilder builder;
        const MazeGraph & graph = builder.setExtent(extent).buildGraph();
        runBenchmark(graph, runs, [extent, number]() {return createSnakeGraphQueries(extent, number); });
    }
}

void benchmarkTreeGraph(size_t runs = 3, size_t number = 1000, const std::initializer_list<size_t> & extents = { 8, 16, 32 }) {
    for (auto extent : extents) {
        std::cout << "Benchmarking isReachable() for tree graph with extent " << extent << ", "
            << "running " << number << " queries, " << runs << " times." << std::endl;
        TreeGraphBuilder builder;
        const MazeGraph & graph = builder.setExtent(extent).buildGraph();
        runBenchmark(graph, runs, [extent, number]() {return createTreeGraphQueries(extent, number); });
    }
}



int main(int argc, char* argv[]) {
    benchmarkSnakeGraph(10, 2000, { 28 });
    benchmarkTreeGraph(10, 2000, { 32 });
    std::cout << "Enter to exit." << std::endl;
    std::cin.ignore();
}