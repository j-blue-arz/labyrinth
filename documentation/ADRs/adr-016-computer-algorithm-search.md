# ADR 16: Search algorithm architecture

## Context
The algorithms which determine move and shift actions will be search algorithms (e.g. BFS) on a game tree. This ADR discusses the architecture of these algorithms. I limit the discussion to the case where a single player tries to find the minimum number of moves to reach the objective.
The multiple player case will be handled in another ADR.

Several components can be identified. A game tree is a tree where the nodes are board states, and edges are actions the player can perform.
Each node can be assigned a value. In the simple case, this value is either 1, if the piece has reached the objective, or 0 otherwise.
Another option is to define a heuristic for the states where the objective was not reached. 
Whether a heuristic is necessary or not depends on the seach depth, or more specifically, if the search depth suffices to reach the objective.
One question is whether the move and shift actions should be considered separately. The only case where this makes a difference is when a heuristic is employed, because then the board state without the move action could already be given a value.

Another question is how to represent a tree node. A tree node can be defined by the initial board state and a list of player actions.
One option is to extend the already implemented graph class to take the list of actions into account. The graph's methods such as `reachable_locations` or `_neighbors` would have to be generalized for a dynamically changing graph.
Easier to implement is to clone the board and perform the actual actions if needed. Caching this state introduces a space / time - tradeoff.
## Decision
I will implement a `GameTree`, with `TreeNode`s. The first implementation will clone the board and perform the actions, without caching the result.
I will not implement a heuristic for this first algorithm. Heuristics will be introduced in later variants of the search algorithms.
I will then evaluate the required depth of the search for the 7 times 7 board. If the search does not finish in two seconds, I will try to engineer the search with the two other approaches, caching the state or even implementing a dynamic graph.

## Status
Ready to be implemented.

## Consequence
Implement, evaluate.
Update the decision when I know more.






