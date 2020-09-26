/*
 * Contains common datastructures used for all search algorithms. 
*/
#include "maze_graph.h"

namespace labyrinth {

struct ShiftAction {
    Location location{0, 0};
    RotationDegreeType rotation{0};
};

struct PlayerAction {
    ShiftAction shift;
    Location move_location;
};

} // namespace labyrinth