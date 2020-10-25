#pragma once
#include "graphbuilder/text_graph_builder.h"
#include "solvers/maze_graph.h"
#include "solvers/minimax.h"
#include "util.h"

#include "gmock/gmock.h"
#include "gtest/gtest.h"

using namespace labyrinth;

class SolversTest : public ::testing::Test {
public:
    virtual ~SolversTest() {}

protected:
    void givenGraph(const std::vector<std::string>& maze, const std::vector<OutPaths>& leftover_out_paths) {
        TextGraphBuilder builder{};

        graph = builder.setMaze(maze).withStandardShiftLocations().buildGraph();
        graph.setLeftoverOutPaths(labyrinth::testutils::getBitmask(leftover_out_paths));
    }

    void givenPlayerLocations(const Location& player_location, const Location& opponent_location) {
        this->player_location = player_location;
        this->opponent_location = opponent_location;
    }

    void givenObjectiveAt(const Location& location) { objective_id = graph.getNode(location).node_id; }

    void givenPreviousShift(const Location& location) { previous_shift_location = location; }

    solvers::SolverInstance getSolverInstance() const {
        return solvers::SolverInstance{graph, player_location, opponent_location, objective_id, previous_shift_location};
    }

    MazeGraph graph{0};
    Location player_location;
    Location opponent_location;
    NodeId objective_id{0};
    Location previous_shift_location{-1, -1};
};