#include "solvers.h"

namespace std {
std::ostream& operator<<(std::ostream& stream, const labyrinth::solvers::PlayerAction& player_action) {
    stream << "{shift: [" << player_action.shift.location << ", " << player_action.shift.rotation
           << "], move: " << player_action.move_location << "}";
    return stream;
}
} // namespace std