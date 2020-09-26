#include "solvers/exhsearch.h"
#include "solvers/location.h"
#include "solvers/maze_graph.h"

#include "benchmark/benchmark_reader.h"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

using namespace labyrinth;

namespace fs = std::filesystem;

using FracSeconds = std::chrono::duration<double>;

static void show_usage(const std::string& name) {
    std::cerr << "Usage: " << name << " INSTANCE_FOLDER OUT_CSV" << std::endl
              << "Where: " << std::endl
              << "\tINSTANCE_FOLDER\t\tcontains files ending with .txt in a specific format." << std::endl
              << "\tOUT_CSV\t\t\twill be created by the benchmark and will contain the results." << std::endl;
}

std::vector<FracSeconds> benchmark(const BenchmarkInstance& instance, size_t repeats) {
    std::cout << "Benchmarking instance " << instance.name << std::endl;
    MazeGraph graph = buildMazeGraph(instance);
    auto objective_id = objectiveIdFromLocation(graph, instance.objective);
    Location player_location = instance.player_locations[0];
    std::vector<FracSeconds> result{};
    for (size_t run = 0; run < repeats; run++) {
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

void run(const std::string& instance_folder, const std::string& out_filename, const size_t repeats = 10) {
    write_header(out_filename, repeats);
    for (const auto& file : fs::directory_iterator(instance_folder)) {
        if (file.is_regular_file() && file.path().extension() == ".txt") {
            const BenchmarkInstance instance = readInstance(file.path());
            std::vector<FracSeconds> durations = benchmark(instance, repeats);
            append_csv(out_filename, instance.name, durations);
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        show_usage(argv[0]);
        return 1;
    }
    run(argv[1], argv[2]);
    return 0;
}
