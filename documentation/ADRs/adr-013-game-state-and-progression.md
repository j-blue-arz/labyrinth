# ADR 13: Separation betwee game state and game progression

## Context
The word 'game' has two meanings. One is the set of all components, layed out on a table in a certain manner, defining the state of the game.
The other is the actual match, describing the progression of the game, with different turns, counting points and a winning player.

These two notions should be separated in the model.

Another problem: model classes have setters on actually internal fields, because mapper needs to access this state.
Solution1: remove setters, let mapper set private fields directly
Solution2: make private fields public
Solution3: let mapper methods be members of domain classes.

## Decision
init_game and all random generation methods into a GameFactory.
Old. Game: Players, Turns, Leftover, Board; Board: MazeCards
New: Game: Board, Turns, Players; Board: Maze, Pieces, Leftover; Maze: MazeCards; Pieces: id, MazeCard, Objective
Basically keep the current classes, but rename Player to Piece, Board to Maze, Game to Board, and create a new class Game containing Board and Turns.
Separate Game into Board, containing MazeCards, Pieces, Leftover, and Game, containing Board, Turns, Players. Move and Shift logic implemented in GameBoard, Check if it is easily possible to distinguish betwee Players (id, objective) and Pieces (current location).

## Status
Open

## Consequence
Refactor, revisit this ADR if needed.



