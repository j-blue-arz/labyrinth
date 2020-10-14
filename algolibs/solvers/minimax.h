#pragma once

#include "solvers.h"

#include <future>

namespace labyrinth {

namespace minimax {

using ValueType = int32_t;

struct Evaluation {
    constexpr Evaluation(ValueType value) : value{value}, is_terminal{false} {}
    explicit Evaluation(ValueType value, bool is_terminal) : value{value}, is_terminal{is_terminal} {}

    ValueType value;
    bool is_terminal;
};

struct MinimaxResult {
    PlayerAction player_action;
    Evaluation evaluation;
};

struct SearchStatus {
    size_t current_depth;
    bool is_terminal;
};

static std::atomic_bool is_aborted = false;

/** Aborts the current computation. This is only safe to use if one algorithm (findBestAction or iterateMinimax) is called from
 * a single thread. Otherwise, this will abort all currently running computations in the best case, and might not have
 * any effect at all in the worst case.
 */
void abortComputation();

/** Searches for the minimax action, up to a given depth */
MinimaxResult findBestAction(const MazeGraph& graph,
                            const Location& player_location,
                            const Location& opponent_location,
                            const NodeId objective_id,
                            const size_t max_depth,
                            const Location& previous_shift_location = Location{-1, -1});

/** Searches for a minimax action, with increasing depths. 
 * The algorithm will run until either it is aborted or it finds a terminating result, 
 * i.e. one of the players is guaranteed to reach the objective.
*/
PlayerAction iterateMinimax(const MazeGraph& graph,
                            const Location& player_location,
                            const Location& opponent_location,
                            const NodeId objective_id,
                            const Location& previous_shift_location = Location{-1, -1});


SearchStatus getSearchStatus();



} // namespace minimax
} // namespace labyrinth