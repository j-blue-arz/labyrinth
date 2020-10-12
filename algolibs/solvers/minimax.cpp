#include "minimax.h"

#include "graph_algorithms.h"

#include "location.h"
#include "maze_graph.h"

#include <algorithm>
#include <memory>
#include <optional>

/**
 * The minimax algorithm searches for the optimal action to play in a two-player zero-sum game.
 * It traverses the game tree and assigns a value to each node (=state of the game).
 * The algorithm recursively searches for the action which maximizes the minimum values of the opponent's possible following moves.
 *
 * This implementation is divided into four parts:
 * - The GameTreeNode class contains the labyrinth game logic. It allows iterating over the possible moves.
 * - The Evaluator determines a value for a given GameTreeNode.
 * - The negamax implementation in MinimaxRunner traverses the game tree by creating GameTreeNodes.
 * - The iterative deepening algorithm iteratively calls the minimax algorithm with increasing depths.
 */

namespace labyrinth {

namespace minimax {

namespace { // anonymous namespace for file-internal linkage

class GameTreeNode;
using NodePtr = std::shared_ptr<GameTreeNode>;

/**
 * Represents a node in the game tree for two players.
 *
 * Each node represents a current state of the maze. As minimax algorithm is essentially a depth-first search, it is ok to
 * store this MazeGraph instance explicitly.
 * A node has a reference to a PlayerAction.
 * The state of the board is the result of applying this action on the parent's board.
 * A node offers an iterator over all it's possible next PlayerActions.
 * From the viewpoint of a GameTreeNode, it is always player 0 who performs the action.
 * Therefore, the player locations are swapped in the constructor.
 */
class GameTreeNode {
private:
    class PlayerActionRange;

public:
    explicit GameTreeNode(const MazeGraph& graph,
                          const PlayerAction& previous_player_action,
                          const Location& player_location) :
        graph_{graph},
        player_locations_{player_location, previous_player_action.move_location},
        previous_shift_location_{previous_player_action.shift.location} {}

    /// Returns a range over possible PlayerActions.
    /// The returned object has two member functions begin() and end(), so
    /// that it can be used in range-based for loop, e.g.
    /// for (auto player_action : node.possible_actions()) { ... }
    PlayerActionRange possibleActions() const { return PlayerActionRange(*this); }

    const MazeGraph& getGraph() const noexcept { return graph_; }

    const Location& getPlayerLocation() const { return player_locations_[0]; }

    const Location& getOpponentLocation() const { return player_locations_[1]; }

    const Location& getPreviousShiftLocation() const { return previous_shift_location_; }

private:
    class PlayerActionIterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = PlayerAction;
        using difference_type = std::ptrdiff_t;
        using reference = PlayerAction;
        using pointer = void;

        static PlayerActionIterator begin(const GameTreeNode& node) { return PlayerActionIterator{node}; }
        static PlayerActionIterator end(const GameTreeNode& node) { return PlayerActionIterator{node, true}; }

        bool operator==(const PlayerActionIterator& other) const noexcept {
            if (other.is_at_end_) {
                return is_at_end_;
            } else if (is_at_end_) {
                return false;
            } else {
                return current_rotation_ == other.current_rotation_ &&
                       current_shift_location_ == other.current_shift_location_ &&
                       current_move_location_ == other.current_move_location_;
            }
        }

        bool operator!=(const PlayerActionIterator& other) const noexcept { return !(*this == other); }

        reference operator*() const {
            return PlayerAction{ShiftAction{*current_shift_location_, current_rotation_}, *current_move_location_};
        }

        pointer operator->() = delete;

        PlayerActionIterator& operator++() {
            ++current_move_location_;
            if (current_move_location_ == possible_move_locations_.end()) {
                nextShift();
            }
            return *this;
        }

        PlayerActionIterator operator++(int) {
            auto result = PlayerActionIterator(*this);
            ++(*this);
            return result;
        }

    private:
        explicit PlayerActionIterator(const GameTreeNode& node, bool is_at_end = false) :
            current_rotation_{0},
            current_shift_location_{node.getGraph().getShiftLocations().begin()},
            is_at_end_(is_at_end),
            node_{node} {
            if (!is_at_end_) {
                invalid_shift_location_ =
                    opposingShiftLocation(node_.getPreviousShiftLocation(), node_.getGraph().getExtent());
                skipInvalidShiftLocation();
                initPossibleMoves();
            }
        }

        void nextShift() {
            current_rotation_ += 90;
            if (current_rotation_ == 360) {
                current_rotation_ = 0;
                ++current_shift_location_;
                if (current_shift_location_ != node_.getGraph().getShiftLocations().end()) {
                    skipInvalidShiftLocation();
                }
                if (current_shift_location_ == node_.getGraph().getShiftLocations().end()) {
                    is_at_end_ = true;
                }
            }
            initPossibleMoves();
        }

        void skipInvalidShiftLocation() {
            if (invalid_shift_location_ == *current_shift_location_) {
                ++current_shift_location_;
            }
        }

        void initPossibleMoves() {
            if (!is_at_end_) {
                MazeGraph shifted_graph{node_.getGraph()};
                shifted_graph.shift(*current_shift_location_, current_rotation_);
                auto translated_player_location = translateLocationByShift(
                    node_.getPlayerLocation(), *current_shift_location_, shifted_graph.getExtent());
                possible_move_locations_ = reachable::reachableLocations(shifted_graph, translated_player_location);
            } else {
                possible_move_locations_.resize(0);
            }
            current_move_location_ = possible_move_locations_.begin();
        }

        RotationDegreeType current_rotation_;
        std::vector<Location>::const_iterator current_shift_location_;
        std::vector<Location> possible_move_locations_;
        std::vector<Location>::const_iterator current_move_location_;
        Location invalid_shift_location_;
        bool is_at_end_;
        const GameTreeNode& node_;
    };

    class PlayerActionRange {
    public:
        explicit PlayerActionRange(const GameTreeNode& node) : node_{node} {}
        PlayerActionIterator begin() const { return PlayerActionIterator::begin(node_); }
        PlayerActionIterator end() const { return PlayerActionIterator::end(node_); }

    private:
        const GameTreeNode& node_;
    };

    MazeGraph graph_;
    std::array<Location, 2> player_locations_;
    Location previous_shift_location_;
};

inline bool operator>(const Evaluation& lhs, const Evaluation& rhs) noexcept {
    return lhs.value > rhs.value;
}

Evaluation operator-(const Evaluation& evaluation) noexcept {
    return Evaluation{-evaluation.value, evaluation.is_terminal};
}

/**
 * Evaluates a GameTreeNode for the minimax algorithm.
 *
 * Returns a value and a flag if the objective was reached.
 */
class Evaluator {
public:
    using Evaluation = minimax::Evaluation;
    explicit Evaluator(NodeId objective_id) : objective_id_{objective_id} {}

    /* The implementation of negamax does not use an alternating player index.
     * Therefore, the Evaluator always has to evaluate from the viewpoint of player 0.
     * For a GameTreeNode, the incoming player action is the opponent action. Hence,
     * The non-heuristic Evaluator will return -1 if the opponent has reached the objective.
     * However, if the current player is placed on the objective, it has to return 0 (not 1), because
     * The player has not actively reached the objective in his last move.
     */
    Evaluation evaluate(const GameTreeNode& node) const {
        if (node.getGraph().getNode(node.getOpponentLocation()).node_id == objective_id_) {
            return Evaluation{-1, true};
        } else {
            return 0;
        }
    }

private:
    NodeId objective_id_;
};

/**
 * Encapsulates the negamax implementation with its required data.
 * Is able to store data between consecutive negamax runs.
 */
class MinimaxRunner {
public:
    constexpr static Evaluation infinity{10000};

    explicit MinimaxRunner(const Evaluator& evaluator, size_t max_depth) :
        evaluator_{evaluator}, max_depth_{max_depth}, best_action_{error_player_action} {}

    MinimaxResult runMinimax(const MazeGraph& graph,
                             const Location& player_location,
                             const Location& opponent_location,
                             const Location& previous_shift_location = Location{-1, -1}) {
        const auto previous_action = PlayerAction{
            ShiftAction{previous_shift_location, graph.getNode(previous_shift_location).rotation}, opponent_location};
        auto root = std::make_shared<GameTreeNode>(graph, previous_action, player_location);
        const auto& evaluation = negamax(root);
        return MinimaxResult{best_action_, evaluation};
    }

    /**
     * This implementation of negamax does not use an alternating player index.
     * Therefore, the Evaluator always has to evaluate from the viewpoint of player 0.
     */
    Evaluation negamax(NodePtr node, size_t depth = 0) {
        auto evaluation = evaluator_.evaluate(*node);
        if (depth == max_depth_ or evaluation.is_terminal) {
            return evaluation;
        }
        auto best_value = -infinity;
        for (auto action : node->possibleActions()) {
            MazeGraph graph{node->getGraph()};
            graph.shift(action.shift.location, action.shift.rotation);
            auto new_opponent_location =
                translateLocationByShift(node->getOpponentLocation(), action.shift.location, graph.getExtent());
            auto child_node = std::make_shared<GameTreeNode>(graph, action, new_opponent_location);
            auto negamax_value = -negamax(child_node, depth + 1);
            if (negamax_value > best_value) {
                best_value = negamax_value;
                if (depth == 0) {
                    best_action_ = action;
                }
            }
            if (is_aborted) {
                break;
            }
        }
        return best_value;
    }

    void setMaxDepth(size_t depth) { max_depth_ = depth; }

    const PlayerAction& getBestAction() const { return best_action_; }

private:
    const Evaluator& evaluator_;
    size_t max_depth_;
    PlayerAction best_action_;
};

} // namespace

MinimaxResult findBestAction(const MazeGraph& graph,
                             const Location& player_location,
                             const Location& opponent_location,
                             const NodeId objective_id,
                             const size_t max_depth,
                             const Location& previous_shift_location) {
    is_aborted = false;
    Evaluator evaluator{objective_id};
    MinimaxRunner runner{evaluator, max_depth};
    return runner.runMinimax(graph, player_location, opponent_location, previous_shift_location);
}

/**
 * Iterative Deepening implementation. Runs minimax with increasing depths.
 */
PlayerAction iterateMinimax(const MazeGraph& graph,
                            const Location& player_location,
                            const Location& opponent_location,
                            const NodeId objective_id,
                            const Location& previous_shift_location) {
    is_aborted = false;
    size_t max_depth = 0;
    Evaluator evaluator{objective_id};
    MinimaxRunner runner{evaluator, max_depth};
    MinimaxResult minimax_result{error_player_action, -MinimaxRunner::infinity};
    do {
        ++max_depth;
        runner.setMaxDepth(max_depth);
        auto new_result = runner.runMinimax(graph, player_location, opponent_location, previous_shift_location);
        if (!is_aborted || max_depth == 1) {
            minimax_result = new_result;
        }
    } while (!minimax_result.evaluation.is_terminal && !is_aborted);
    return minimax_result.player_action;
}

void abortComputation() {
    is_aborted = true;
}

} // namespace minimax
} // namespace labyrinth