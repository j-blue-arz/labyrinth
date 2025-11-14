#pragma once

#include "solvers.h"

#include <array>
#include <future>

namespace labyrinth {

namespace solvers {

namespace minimax {

/**
 * Represents a node in the game tree for two players.
 *
 * Each node represents a current state of the maze. As minimax algorithm is essentially a depth-first search, it is ok
 * to store this MazeGraph instance explicitly. A node has a reference to a PlayerAction. The state of the board is the
 * result of applying this action on the parent's board. A node offers an iterator over all it's possible child nodes.
 * From the viewpoint of a GameTreeNode, it is always player 0 who performs the action.
 */
class GameTreeNode {
private:
    class ChildrenIterator;

public:
    explicit GameTreeNode(MazeGraph& graph,
                          const Location& player_location,
                          const Location& opponent_location,
                          const Location& previous_shift_location) :
        graph_{graph},
        player_locations_{player_location, opponent_location},
        previous_shift_location_{previous_shift_location} {}

    MazeGraph& getGraph() const noexcept { return graph_; }

    const Location& getPlayerLocation() const { return player_locations_[0]; }

    const Location& getOpponentLocation() const { return player_locations_[1]; }

    const Location& getPreviousShiftLocation() const { return previous_shift_location_; }

private:
    MazeGraph& graph_;
    std::array<Location, 2> player_locations_;
    Location previous_shift_location_;
};

/**
 * The value type of a game state in the minimax algorithm.
 *
 * Is returned by an Evaluator, and holds the actual (scalar) value and a flag
 * designating if the node is terminal, i.e. if the algorithm should not continue searching
 * along the current path.
 * This is typically the case if the objective has been reached. *
 */
struct Evaluation {
    using ValueType = int32_t;

    constexpr Evaluation(ValueType value) : value{value}, is_terminal{false} {}
    explicit Evaluation(ValueType value, bool is_terminal) : value{value}, is_terminal{is_terminal} {}

    ValueType value;
    bool is_terminal;
};

inline bool operator>(const Evaluation& lhs, const Evaluation& rhs) noexcept;

inline bool operator>=(const Evaluation& lhs, const Evaluation& rhs) noexcept;

Evaluation operator-(const Evaluation& evaluation) noexcept;

Evaluation operator+(const Evaluation& evaluation1, const Evaluation& evaluation2) noexcept;

Evaluation operator*(const Evaluation& evaluation, Evaluation::ValueType factor) noexcept;

struct MinimaxResult {
    PlayerAction player_action;
    Evaluation evaluation;
};

struct SearchStatus {
    size_t current_depth;
    bool is_terminal;
};

/**
 * Evaluates a GameTreeNode for the minimax algorithm.
 *
 * Returns a value and a flag if the objective was reached.
 */
class Evaluator {
public:
    virtual ~Evaluator() {}
    virtual Evaluation evaluate(const GameTreeNode& node) const = 0;
};

static std::atomic_bool is_aborted = false;

/** Aborts the current computation. This is only safe to use if one algorithm (findBestAction or iterateMinimax) is
 * called from a single thread. Otherwise, this will abort all currently running computations in the best case, and
 * might not have any effect at all in the worst case.
 */
void abortComputation();

/** Searches for the minimax action, up to a given depth */
MinimaxResult findBestAction(const SolverInstance& solver_instance, std::unique_ptr<Evaluator> evaluator, const size_t max_depth);

/** Searches for a minimax action, with increasing depths.
 * The algorithm will run until either it is aborted or it finds a terminating result,
 * i.e. one of the players is guaranteed to reach the objective.
 */
PlayerAction iterateMinimax(const SolverInstance& solver_instance, std::unique_ptr<Evaluator> evaluator);

SearchStatus getSearchStatus();

} // namespace minimax
} // namespace solvers
} // namespace labyrinth