# ADR 13: Separation between game state and game progression

## Context
The word 'game' has two meanings. One is the set of all components, layed out on a table in a certain manner, defining the state of the game.
The other is the actual match, describing the progression of the game, with different turns, counting points and a winning player.

These two notions should be separated in the backend model.
There are more questions of wording. Is the board only the field of maze cards, or is it the set of all components, e.g. does it include the leftover maze card?
If the two notions of game are separated, should player be separated as well? One for the piece on the board, the other for the human beeing, the one haveing and objective, getting points and winning the game?

Another problem is that model classes have setters on internal fields, because the mapper has to set these fields when creating the objects from a DTO.
The mapper is the only reason these fields are mutable.
One solution is to remove the setters, and let the mapper set private fields directly. This is possible in python. The mapper then depends on the models internal structures, but this is hard to eliminate, anyways.
Another solution would be to make the private fields public. Then no setters are needed. The dependency problem state above remains. Moreover, there is no longer the distinction between the fields which can be altered and the fields which should not be altered. Another solution would be to let the mapper methods be members of domain classes, but this would introduce responsibilities to these classes.
Yet another solution is to set the private fields in the constructor. Then the mapper can construct the objects, but they remain hidden after construction.

## Decision
Create class GameFactory, containing init_game and all random generation methods.
Keep the current classes, but rename Board to Maze, Game to Board, and create a new class Game containing Board and Turns.
Also rename Player into Piece, but do not separate Player into Player and Piece yet, as the class is rather small right now anyways. Once more responsibilities are added to Piece, it might make more sense to split it up.
The list of Pieces is located in the Board, not in the Game. Game only knows about IDs.
So right now, these two words player and piece are used interchangeably in the code, with the general idea that in the domain of a match the wording should be 'player' and in the domain of the Board, 'piece' should be the preferrd word.

At first, I aimed to let the mapper access private fields directly. I tried to ignore the linter warnings, but my OCD kept nagging on me. Now I moved most of these fields into the constructors.


## Status
Implemented

## Consequence
Refactor, revisit this ADR if needed.
Turns has to work with player IDs, not with Piece instances, because Game does not know about Pieces.





