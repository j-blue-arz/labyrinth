""" This module defines the ApiException, which can be translated to a HTTP response.
It defines a few exception factories.
It also maps domain exceptions to these pre-defined factories. """

from .domain.exceptions import InvalidStateException, PlayerNotFoundException, \
    InvalidLocationException, InvalidShiftLocationException, MoveUnreachableException, \
    InvalidRotationException, TurnActionViolationException, GameFullException
from .mapper.api import exception_to_dto

GAME_FULL = lambda: ApiException("GAME_FULL", "Number of players has reached game limit.", 400)
INVALID_ACTION = lambda: ApiException("INVALID_ACTION", "The sent action is invalid.", 400)
GAME_NOT_FOUND = lambda: ApiException("GAME_NOT_FOUND", "The game does not exist.", 404)
PLAYER_NOT_IN_GAME = lambda: ApiException("PLAYER_NOT_IN_GAME", "The player does not take part in this game.", 400)
UNKNOWN_ERROR = lambda: ApiException("UNKNOWN_ERROR", "An unknown error has occurred.", 400)

class ApiException(Exception):
    """ Exception which is translated to a HTTP Response """

    def __init__(self, key, message, status_code):
        super().__init__(message)
        self.key = key
        self.message = message
        self.status_code = status_code

    def to_dto(self):
        """ Maps this object to a DTO to be transferred by the API """
        return exception_to_dto(self)

def domain_to_api_exception(domain_exception):
    """ Maps a domain exception instance to an ApiException.

    :param domain_exception: an instance of a subclass of domain.exceptions.LabyrinthDomainException
    """
    if isinstance(domain_exception, InvalidStateException):
        return UNKNOWN_ERROR()
    if isinstance(domain_exception, GameFullException):
        return GAME_FULL()
    if isinstance(domain_exception, PlayerNotFoundException):
        return PLAYER_NOT_IN_GAME()
    if isinstance(domain_exception, (InvalidLocationException,
                                     InvalidShiftLocationException,
                                     InvalidRotationException,
                                     MoveUnreachableException,
                                     TurnActionViolationException)):
        return INVALID_ACTION()
    return UNKNOWN_ERROR()
