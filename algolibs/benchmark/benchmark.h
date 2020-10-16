#pragma once

#include "benchmark/benchmark_reader.h"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

static void show_usage(const std::string& name) {
    std::cerr << "Usage: " << name << " INSTANCE_FOLDER OUT_CSV" << std::endl
              << "Where: " << std::endl
              << "\tINSTANCE_FOLDER\t\tcontains files ending with .txt in a specific format." << std::endl
              << "\tOUT_CSV\t\t\twill be created by the benchmark and will contain the results." << std::endl;
}

namespace fs = std::filesystem;

namespace bench {

using FracSeconds = std::chrono::duration<double>;
using namespace labyrinth;

class AlgolibsBenchmark {
public:
    void run(const std::string& instance_folder, const std::string& out_filename, const size_t repeats = 10) const {
        write_header(out_filename, repeats);
        for (const auto& file : fs::directory_iterator(instance_folder)) {
            if (file.is_regular_file() && file.path().extension() == ".txt") {
                const BenchmarkInstance instance = reader::readInstance(file.path());
                std::vector<FracSeconds> durations = benchmark(instance, repeats);
                append_csv(out_filename, instance.name, durations);
            }
        }
    }

    virtual ~AlgolibsBenchmark() {}

protected:
    virtual std::vector<FracSeconds> benchmark(const BenchmarkInstance& instance, size_t repeats) const = 0;

private:
    void write_header(const fs::path filename, const size_t repeats) const {
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

    void append_csv(const fs::path filename,
                    const std::string& instance_name,
                    const std::vector<FracSeconds>& durations) const {
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
};

} // namespace bench