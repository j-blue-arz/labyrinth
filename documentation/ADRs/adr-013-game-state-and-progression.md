# ADR 13: Separation between game state and game progression

## Context
The word 'game' has two meanings. One is the set of all components, layed out on a table in a certain manner, defining the state of the game.
The other is the actual match, describing the progression of the game, with different turns, counting points and a winning player.

These two notions should be separated in the backend model.
Question of wording. Is the board only the field of maze cards, or is it the set of all components, e.g. does it include the leftover maze card?
If the two notions of game are separated, should player be separated as well? One for the piece on the board, the other for the human beeing, the one haveing
and objective, getting points and winning the game?

Another problem: model classes have setters on actually internal fields, because mapper needs to access this state.
Solution1: remove setters, let mapper set private fields directly
Solution2: make private fields public
Solution3: let mapper methods be members of domain classes.

## Decision
Create class GameFactory, containing init_game and all random generation methods.
Keep the current classes, but rename Board to Maze, Game to Board, and create a new class Game containing Board and Turns.
Also rename Player into Piece, but do not separate Player into Player and Piece yet, as the class is rather small right now anyways. Once more responsibilities are added to Piece, it might make more sense to split it up.
The list of Pieces is located in the Board, not in the Game. Game only knows about IDs.
So right now, these two words player and piece are used interchangeably in the code, with the general idea that in the domain of a match the wording should be 'player' and in the domain of the Board, 'piece' should be the preferrd word.

Remove setters for private fields. Ignore warnings in mapper.


## Status
Open

## Consequence
Refactor, revisit this ADR if needed.
Turns has to work with player IDs, not with Piece instances, because Game does not know about Pieces.



