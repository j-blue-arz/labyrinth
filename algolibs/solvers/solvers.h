#pragma once
/*
 * Contains common datastructures used for all search algorithms.
 */
#include "maze_graph.h"

#include <ostream>

namespace labyrinth {

struct ShiftAction {
    Location location{0, 0};
    RotationDegreeType rotation{0};
};

struct PlayerAction {
    ShiftAction shift;
    Location move_location;
};

static const PlayerAction error_player_action = PlayerAction{ShiftAction{}, Location{-1, -1}};

} // namespace labyrinth

namespace std {
std::ostream& operator<<(std::ostream& stream, const labyrinth::PlayerAction& player_action);
} // namespace std