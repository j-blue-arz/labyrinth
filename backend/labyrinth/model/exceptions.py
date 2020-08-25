""" This module defines domain exceptions.
"""

__all__ = ["InvalidStateException",
           "PlayerNotFoundException",
           "InvalidLocationException",
           "InvalidShiftLocationException",
           "InvalidRotationException",
           "MoveUnreachableException",
           "TurnActionViolationException",
           "GameFullException",
           "InvalidSizeException",
           "InvalidComputeMethodException",
           "GameNotFoundException"]


class LabyrinthDomainException(Exception):
    """ A base class for all domain exceptions of the labyrinth domain model """
    pass


class InvalidStateException(LabyrinthDomainException):
    """ If the game realizes it is in an invalid state from which it cannot recover,
    and it is unable to determine how it got there
    """
    pass


class GameFullException(LabyrinthDomainException):
    """ If a player is added to game without empty places """
    pass


class PlayerNotFoundException(LabyrinthDomainException, ValueError):
    """ If an action is made for a player who is not part of the game """
    pass


class InvalidLocationException(LabyrinthDomainException):
    """ If a location parameter is invalid, e.g. outside of the board """
    pass


class RuleViolationException(LabyrinthDomainException):
    """ If a rule of the game was violated """
    pass


class InvalidShiftLocationException(InvalidLocationException, RuleViolationException):
    """ The shift location is not possible, either due to the fixed cards, or
    due to the no-pushback rule """
    pass


class MoveUnreachableException(InvalidLocationException, RuleViolationException):
    """ If there is no path to the requested location """
    pass


class TurnActionViolationException(RuleViolationException):
    """ If an action was requested for a player, but it is not his turn to player,
    or he has to perform another action """
    pass


class InvalidRotationException(LabyrinthDomainException, ValueError):
    """ If a given rotation parameter is not divisible by 90 """
    pass


class InvalidSizeException(LabyrinthDomainException, ValueError):
    """ If a requested maze size is not admissible """
    pass


class InvalidComputeMethodException(LabyrinthDomainException):
    """ If a requested compute method could not be found """
    pass


class GameNotFoundException(LabyrinthDomainException):
    """ If a game could not be found in the game repository """
    pass
