# ADR 3: Model for the board state for the MVP

## Context
This ADR covers the representation of the board state for the MVP. This state includes the maze cards on the board, the leftover maze card, the positions of all players, and
the positions of the player's current objects. Distinguishable is the game state. The game state has to cover all other possible objects on the board or anything related to the progression of the game.
More precisely, the state does not yet include the player to move next, the sequence of past actions, and the objectives each player has already attained.
The game state is not matter of this ADR and has to be discussed in the future.

There are several requirements to a model for the board state. 
The board has to be drawn on the UI. This includes the maze cards, the position of each player and the objective.
In the client, only the objective of the player who uses this client should be visible and available. 
All objects on the board, i.e. the objectives and the pieces, have to move with the shifted maze cards, respecting the rules of the game.
Validation is another requirement, be it on the client or on the server. For validation, it should be possible to build a graph to represent the maze. 
Animation on the client should be possible as well. The leftover maze cards has to be rotatable, and the maze cards on the board have to be shifted. These animations
are especially important when not done by the player using the client.
Redundancies should be reduced, as these increase representation size unnecessarily. 
Encoding the same information in two or more ways also raise potential questions, as how should inconsistencies be handled?

For drawing, the positions of the maze cards and the objects have to be known.
For each maze card, the position can be specified as a coordinate, with row and column. A different solution is to determine the position by the index of the maze card object in a list (or 2d array).
The objects either have a coordinate, or a reference to the maze card, or both.
Maze cards can also include a list of objects which are positioned on the maze card. Without this list, all objects have to be iterated over to find the ones which have to be moved with the card.
To define a maze card, it is sufficient to specify its doors, i.e. its potential connections to surrounding maze cards. Including an additional identifier makes it easier
to determine which maze cards were shifted by another player. Without this identfier, special logic is necessary.

Another question which arises is to what extend the state model on the server, in the client, and in the interface differ from one another. As there are different requirements for these three models, they
might as well be different. In this case, mappers are required to transform between different representations. Representations on the server and in the client can make use of references between objects, 
but the interface has to transfer these references as IDs and foreign keys.

## Decision
The representations on the client, the interface, and the server, will differ. Explicit representations are to be preferred to implicit ones.
*On the client*, Maze cards will have a unique identifier and a current position. This position will have a special value for the leftover maze card.
They will also contain information about their initial doors and their current rotation. 
The maze cards will contain references to their current objects.
Objects will have a reference to the maze card they are situated on, but no additional location.
The game state will consist of a list of pieces, the current objective of the player, an 2-d array of maze cards and an additional leftover maze card.

*The server* will have a slightly easier representation, but for the entire game state, not only one players view.
It will store the objectives of all players. Maze cards do not have information about their position, nor about their objects.

The model of *the web interface* will not include references from maze cards to objects. References from objects to maze cards will be present in form of IDs. The maze cards will be transmitted in a list, without
any guarantee about the order. The type of a maze card will be coded in a string over the alphabet {N, E, S, W} of length between two and three. A maze card also transmits its current rotation as a multiple of 90.

## Status
Accepted

## Consequences
The consistency of the back-and-forth reference between objects positioned on maze cards has to be asserted on the client.
The actual doors of maze cards have to be computed by combining the initial doors with the current rotation.
This allows for an implicit graph representation.
Mappers have to be implemented transforming between the representations client representation.