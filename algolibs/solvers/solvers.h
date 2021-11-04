#pragma once
/*
 * Contains common datastructures used for all search algorithms.
 */
#include "maze_graph.h"

#include <ostream>

namespace labyrinth {

namespace solvers {

struct SolverInstance {
    MazeGraph graph{0};
    Location player_location{-1, -1};
    Location opponent_location{-1, -1};
    NodeId objective_id{0};
    Location previous_shift_location{-1, -1};
};

struct ShiftAction {
    Location location{0, 0};
    RotationDegreeType rotation{RotationDegreeType::_0};
};

struct PlayerAction {
    ShiftAction shift;
    Location move_location;
};

static const PlayerAction error_player_action = PlayerAction{ShiftAction{}, Location{-1, -1}};
} // namespace solvers
} // namespace labyrinth

namespace std {
std::ostream& operator<<(std::ostream& stream, const labyrinth::solvers::PlayerAction& player_action);
} // namespace std