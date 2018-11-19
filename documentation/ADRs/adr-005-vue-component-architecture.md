# ADR 3: How to structure the Vue.js components?

## Context

Vue allows for structuring the application into components. Following components identified: 
* the game container, managing game state, communicating with webservice, pushing data to sub-components for display, also containing the leftover card
* the game board, displaying the maze cards
* a maze card, displaying a maze card
* the game interatction, managing interaction with the board, emitting events

How to structure these?
Board and interaction are difficult to separate, synchronization of sizes would be difficult. Interaction html element contains board, this is possible in vue with slots. However, this technique creates a dynamic which is not required and makes the structure harder to understand. Better: hard-defined composition. Then the interaction component has to contain the board. The problem here is that the container only includes the interaction.

## Decision
I will implement the board contained in the interaction, and the interaction contained in the container.

## Status
Accepted

## Consequences
Find names for each component. Name of interaction has to make clear that it contains the game board.

