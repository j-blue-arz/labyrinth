# ADR 1: How much logic in the client?

## Context
In classic MVC architecture, the view part of a software architecture is said to be dumb. No logic should take place in the view. The view only displays the model,
and forwards any user interaction to the controller.
In client-server architectures the view is either the client in a browser or a standalone executable communication with the server.
Modern web applications, however, place more and more logic in the client. The question arises, how much logic should be implemented in the client of Labyrinth?

Input validation of player moves in the client require a graph representation of the board, and a breadth-first search.
The results of this search make it possible to animate the move of the player's piece.
Server could also return the path, but this results in a more complex web interface.

In a client-server architecture with multiple clients connecting to a single server, the server should always be the single source of truth. 
That is, even if the validation on the client succeeds, if the server rejects an action by a client, the client should concur.

## Decision
My highest goal is to keep the interface between client and server as clean and simple as possible.
I will prefer a low number of methods transmitting more information over lots of unrelated small methods.
Validation will be performed on both sides. The client will know all rules of the game, and I will implement logic in the client to respect those rules.
More specifically, the client will validate the if move actions are valid and will not allow shifting glued-on maze cards. The client is not expected to deduce which
shifting action is prohibited by the no-pushback rule, so the server will include this information in its state response.

The server will perform validation, as well, because he should be open to other, less trustworthy clients playing the game.
However, the server's main responsibility is to manage game state and inform clients.

## Status
Accepted

## Consequences
It must be possible to infer the maze graph from the maze state. 
The object representations of a maze card has information about its connections to (potentially) surrounding cards, but also about its orientation.
This way, the client has an implicit graph representation of the board.

The client will be informed about everything related to his current state, i.e. the board, all player positions, all object positions and his personal objective.
Client can do everything related to this state, e.g. validating input with respect to the board.
The client will not validate input with respect to the overall game state.
Hence, the client has no logic tracking the no-pushback rule.