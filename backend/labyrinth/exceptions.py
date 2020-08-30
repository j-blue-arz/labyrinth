""" This module defines the ApiException, which can be translated to a HTTP response.
It defines a few exception factories.
It also maps domain exceptions to these pre-defined factories. """

from labyrinth.model.exceptions import InvalidStateException, PlayerNotFoundException, \
    InvalidLocationException, InvalidShiftLocationException, MoveUnreachableException, \
    InvalidRotationException, TurnActionViolationException, GameFullException, InvalidSizeException, \
    InvalidComputeMethodException, GameNotFoundException
from labyrinth.mapper.api import exception_to_dto


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


GAME_NOT_FOUND_API_EXCEPTION = ApiException("GAME_NOT_FOUND", "The game does not exist.", 404)


def domain_to_api_exception(domain_exception):
    """ Maps a domain exception instance to an ApiException.

    :param domain_exception: an instance of a subclass of model.exceptions.LabyrinthDomainException
    """
    if isinstance(domain_exception, InvalidStateException):
        return ApiException("UNKNOWN_ERROR", "An unknown error has occurred.", 500)
    if isinstance(domain_exception, GameFullException):
        return ApiException("GAME_FULL", "Number of players has reached game limit.", 400)
    if isinstance(domain_exception, PlayerNotFoundException):
        return ApiException("PLAYER_NOT_IN_GAME", "The player does not take part in this game.", 400)
    if isinstance(domain_exception, (InvalidShiftLocationException,
                                     MoveUnreachableException,
                                     TurnActionViolationException)):
        return ApiException("INVALID_ACTION", "The sent action is invalid.", 400)
    if isinstance(domain_exception, (InvalidSizeException,
                                     InvalidRotationException,
                                     InvalidLocationException)):
        return ApiException("INVALID_ARGUMENTS", "The combination of arguments in this request is not supported.", 400)
    if isinstance(domain_exception, InvalidComputeMethodException):
        return ApiException("INVALID_ARGUMENTS",
                            str(domain_exception),
                            400)
    if isinstance(domain_exception, GameNotFoundException):
        return GAME_NOT_FOUND_API_EXCEPTION
    return ApiException("UNKNOWN_ERROR", "An unknown error has occurred.", 500)
