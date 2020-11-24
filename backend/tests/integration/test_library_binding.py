""" This module tests the integration of all available libraries.

It loads all libraries in the /lib project subfolder (.so when running on linux, .dll when on windows).
It does not test the libraries for quality, but only for correctness. For example, for the exhaustive search
library, it will not check if the returned actions are optimal. Instead, it checks that the returned actions are valid
shifts and moves.
"""
from datetime import timedelta
import time
import threading

from labyrinth.model.external_library import ExternalLibraryBinding
from labyrinth.model.reachable import Graph
from labyrinth.model.game import BoardLocation
from tests.unit.factories import param_tuple_to_param_dict, create_board_and_pieces


def test_3by3_single_player_with_direct_path(library_path):
    test_setup = (MAZE_3BY3, "NE", [(0, 0)], (0, 2))
    previous_shift_location = BoardLocation(0, 1)
    board, piece = _create_board(test_setup)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action = library_binding.find_optimal_action()

    _assert_valid_action(action, board, previous_shift_location, piece)


def test_3by3_single_player_no_direct_path_without_previous_shift(library_path):
    test_setup = (MAZE_3BY3, "NE", [(0, 0)], (2, 2))
    previous_shift_location = None
    board, piece = _create_board(test_setup)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action = library_binding.find_optimal_action()

    _assert_valid_action(action, board, previous_shift_location, piece)


def test_3by3_single_player_with_objective_on_leftover(library_path):
    test_setup = (MAZE_3BY3, "NE", [(0, 0)], "leftover")
    previous_shift_location = BoardLocation(1, 2)
    board, piece = _create_board(test_setup)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action = library_binding.find_optimal_action()

    _assert_valid_action(action, board, previous_shift_location, piece)


def test_3by3_single_player_no_fresh_board(library_path):
    """ Creates a board and makes two shifts, so that the maze card ids
    are no longer regularly distributed row-first
    """
    test_setup = (MAZE_3BY3, "NS", [(0, 0)], (0, 2))
    previous_shift_location = BoardLocation(1, 2)
    board, piece = _create_board(test_setup)
    board.shift(BoardLocation(1, 2), 0)
    board.shift(BoardLocation(2, 1), 0)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action = library_binding.find_optimal_action()

    _assert_valid_action(action, board, previous_shift_location, piece)


def test_3by3_multiple_bindings_same_library(library_path):
    """ Binds three times to the same library """
    test_setup = (MAZE_3BY3, "NS", [(0, 0)], (0, 2))
    previous_shift_location = None

    boards = []
    for _ in range(3):
        board, piece = _create_board(test_setup)
        boards.append(board)

    bindings = [ExternalLibraryBinding(library_path, board, board.pieces[0],
                                       previous_shift_location=previous_shift_location) for board in boards]

    actions = [library_binding.find_optimal_action() for library_binding in bindings]

    for i in range(3):
        _assert_valid_action(actions[i], boards[i], previous_shift_location, boards[i].pieces[0])


def test_3by3_single_player_with_direct_path_concurrent(library_path):
    test_setup = (MAZE_3BY3, "NE", [(0, 0)], (0, 2))
    previous_shift_location = BoardLocation(0, 1)
    board, piece = _create_board(test_setup)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)

    search_ended_event = threading.Event()
    concurrent_library_binding = ConcurrentExternalLibraryBinding(library_binding, search_ended_event)
    concurrent_library_binding.start()
    search_ended_event.wait()
    if concurrent_library_binding.action:
        _assert_valid_action(concurrent_library_binding.action, board, previous_shift_location, piece)
    else:
        assert concurrent_library_binding.action is None


def test_3by3_single_player_no_pushback_rule(library_path):
    """ Performs two library calls: the first without previous shift,
    the second with a previous shift invalidating the shift result of the first call.
    """
    test_setup = (MAZE_3BY3, "NS", [(0, 0)], (0, 2))
    previous_shift_location = None
    board, piece = _create_board(test_setup)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action_1 = library_binding.find_optimal_action()
    _assert_valid_action(action_1, board, previous_shift_location, piece)

    shift_location_1 = action_1[0][0]
    board, piece = _create_board(test_setup)
    previous_shift_location = board.opposing_border_location(shift_location_1)
    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action_2 = library_binding.find_optimal_action()
    _assert_valid_action(action_2, board, previous_shift_location, piece)
    shift_location_2 = action_2[0][0]
    assert shift_location_2 != shift_location_1


def test_second_player_to_play__performs_valid_action(library_path):
    test_setup = (MAZE_3BY3, "NS", [(0, 0), (2, 2)], (2, 1))
    previous_shift_location = None
    board, _ = _create_board(test_setup)
    piece = board.pieces[1]

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)
    action = library_binding.find_optimal_action()

    _assert_valid_action(action, board, previous_shift_location, piece)
    _assert_reaches_objective(action, board, piece)


def test_abort_search__with_long_running_instance__returns_quickly(library_path):
    """ Performs a library call on a long running instance, and aborts after a short time.
    The time between the abort and the return should not exceed 100ms.
    To measure this time, the ExternalLibraryBinding is wrapped in a Thread which signals an Event
    once the computation has finished.
    """
    test_setup = (LONG_RUNNING_EXHSEARCH_INSTANCE, "NE", [(7, 6)], (3, 2))
    previous_shift_location = None
    board, piece = _create_board(test_setup)

    library_binding = ExternalLibraryBinding(library_path, board, piece,
                                             previous_shift_location=previous_shift_location)

    search_ended_event = threading.Event()
    concurrent_library_binding = ConcurrentExternalLibraryBinding(library_binding, search_ended_event)
    concurrent_library_binding.start()
    time.sleep(timedelta(milliseconds=10).total_seconds())
    assert not search_ended_event.is_set()
    start = time.time()
    library_binding.abort_search()
    search_ended_event.wait()
    stop = time.time()
    assert (stop - start) < 0.1
    if concurrent_library_binding.action:
        _assert_valid_action(concurrent_library_binding.action, board, previous_shift_location, piece)
    else:
        assert concurrent_library_binding.action is None


class ConcurrentExternalLibraryBinding(threading.Thread):
    def __init__(self, external_binding, search_ended_event):
        threading.Thread.__init__(self)
        self._external_binding = external_binding
        self._search_ended_event = search_ended_event
        self.action = None

    def run(self):
        self.action = self._external_binding.find_optimal_action()
        self._search_ended_event.set()


def _assert_valid_action(action, board, previous_shift_location, piece):
    shift, move_location = action
    shift_location, shift_rotation = shift
    assert shift_location in board.shift_locations
    if previous_shift_location:
        opposing_shift_location = board.opposing_border_location(previous_shift_location)
        assert shift_location != opposing_shift_location
    assert shift_rotation in [0, 90, 180, 270]
    board.shift(shift_location, shift_rotation)
    piece_location = board.maze.maze_card_location(piece.maze_card)
    assert Graph(board.maze).is_reachable(piece_location, move_location)


def _assert_reaches_objective(action, board, piece):
    shift, move_location = action
    shift_location, shift_rotation = shift
    board.shift(shift_location, shift_rotation)
    reached = board.move(piece, move_location)
    assert reached


def _create_board(test_setup):
    param_dict = param_tuple_to_param_dict(*test_setup)
    board = create_board_and_pieces(**param_dict)
    piece = board.pieces[0]
    return board, piece


MAZE_3BY3 = """
###|#.#|#.#|
#..|...|..#|
#.#|#.#|###|
------------
#.#|#.#|###|
#..|..#|...|
#.#|###|###|
------------
#.#|###|#.#|
#..|#..|..#|
###|#.#|###|
-----------*
"""

# equal to exhsearch_s9_d4_num9.json
LONG_RUNNING_EXHSEARCH_INSTANCE = """
###|#.#|###|#.#|###|###|###|#.#|###|
#..|#..|...|#.#|...|...|...|#..|..#|
#.#|###|#.#|#.#|#.#|###|#.#|###|#.#|
-----------------------------------|
###|#.#|#.#|###|###|#.#|###|###|#.#|
...|#.#|#.#|..#|#..|#..|..#|...|#..|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|###|#.#|
-----------------------------------|
#.#|###|#.#|###|###|#.#|###|###|#.#|
#..|...|#..|..#|...|#..|...|#..|..#|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|#.#|#.#|
-----------------------------------|
#.#|#.#|###|###|#.#|###|###|###|###|
..#|#..|...|#..|#.#|...|...|...|#..|
###|###|###|#.#|#.#|###|###|#.#|#.#|
-----------------------------------|
#.#|###|#.#|###|#.#|###|#.#|#.#|#.#|
#..|...|#..|#..|...|..#|..#|...|..#|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|###|#.#|
-----------------------------------|
###|###|###|###|###|###|#.#|###|###|
#..|...|..#|..#|...|#..|#..|...|...|
#.#|###|#.#|#.#|###|#.#|###|###|###|
-----------------------------------|
#.#|###|#.#|#.#|#.#|#.#|#.#|#.#|#.#|
#..|..#|...|..#|...|..#|..#|#.#|..#|
#.#|#.#|###|###|###|#.#|#.#|#.#|#.#|
-----------------------------------|
###|###|#.#|#.#|#.#|###|#.#|###|#.#|
..#|...|#.#|..#|#.#|...|..#|...|#..|
#.#|###|#.#|#.#|#.#|###|###|###|###|
-----------------------------------|
#.#|###|#.#|###|#.#|#.#|#.#|#.#|#.#|
#..|...|...|..#|...|..#|...|#.#|..#|
###|###|###|#.#|###|###|###|#.#|###|
-----------------------------------*
"""
