## The game

#### action
A shifting action or a move action.
#### door
A maze card's potential paths to its surrounding cards. 
The door positions are a defining characteristic of a maze card. Together with its rotation, they result in certain out paths.
#### computer player
An artificial player, who plays the game by finding shift actions and move actions according to the rules.
#### game board
The set of all maze cards placed in a two-dimensional matrix of size 7x7
#### leftover maze card
The single maze card which is not situated on the game board, but remains available for a shift.
#### maze card
The cards or tiles the game board consists of. There are different types of maze cards, defined by the layout of their doors. 
Maze cards have a rotation, which cannot be changed once it is placed on the board.
#### move action, moves
Place the player's piece to a maze card connected in the current maze card by pathways. 
#### no-pushback rule
Game rule which prohibits players make a shifting action which reverses the shifting action of the previous player's turn.
#### object, objectives
Items placed on maze cards. The player has to reach them with their playing piece to win the game. The objectives stay on the maze card, even if they are pushed out.
#### out paths
The potential paths of a maze card to its surrounding cards. If and only if two neighboring maze cards have out paths facing the respective other, there is a path between them.
Out paths take the rotation of a maze card into consideration, the doors do not.
#### pathways
The graph built out of all subpaths. Pieces can only move along those pathways.
#### piece
Playing pieces of the players. Always situated on the game board. If the maze card a piece is situated on is pushed out, the piece is placed on the opposing, just inserted maze card.
#### player
A human or computer playing the game.
#### reachable locations of a piece
The locations on the board which are connected by pathways starting from the piece.
#### rotation
Each maze card 
#### shifting action, shift action, shifts
Insert the leftover maze card, push out a maze card on the opposite side. This forms new pathways.
A shift action is defined by the rotation of the inserted leftover maze card and one of the available shift locations.
#### shift location
A location on the border of the game board, which is allowed for shift actions. Not all border locations are available. Typically, every second location on a border is a shift location, starting with the first non-corner.
The direction of the shift is determined to be perpendicular to the border the shift location is situated on. Corners of the board are not allowed to be shift locations.
#### previous shift location
The shift location which was used in the latest shift action of one of the players.
#### disabled shift location
The shift location opposing the previous shift location.
#### path
The connection between a single maze card and its neighbor, if they have a door facing each other.
#### turn
A player's turn consists of a shifting action followed by a move action.

## Search algorithms
There are several search algorithms to find actions for a computer player. Some of them find optimal solutions, some use heuristics to find actions which are 'good enough'.
#### Exhaustive search
Finds a shortest path from the player to the objective, given that there are no other players in the game. A shortests path is a shortest sequence of actions.
#### Minimax
Finds exact solutions for a two player game, assuming that the other player play perfect moves.
#### Alpha-Beta search
An improvement of the Minimax algorithm, introducing a heuristic for board positions. This heuristic allows to considerably prune the search space.