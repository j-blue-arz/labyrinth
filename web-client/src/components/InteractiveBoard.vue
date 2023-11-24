<template>
    <svg :viewBox="viewBox" class="interactive-board">
        <v-svg-defs></v-svg-defs>
        <draggable-game-board
            @player-move="onPlayerMove"
            @player-shift="onPlayerShift"
            :current-player-color="currentPlayerColor"
            :reachable-cards="reachableMazeCards"
            :user-action="userAction"
        ></draggable-game-board>
        <insert-panels v-if="!isTouchDevice" @player-shift="onPlayerShift"></insert-panels>
    </svg>
</template>

<script>
import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import InsertPanels from "@/components/InsertPanels.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import VSvgDefs from "@/components/VSvgDefs.vue";
import Graph from "@/model/Graph.js";
import * as action from "@/model/player.js";

import { useBoardStore } from "@/stores/board.js";
import { useGameStore } from "@/stores/game.js";
import { usePlayersStore } from "@/stores/players.js";
import { mapState, mapStores } from "pinia";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        DraggableGameBoard,
        InsertPanels,
        VMazeCard,
        VSvgDefs,
    },
    data() {
        return {
            leftoverX: 0,
            leftoverY: 0,
            isLandscape: true,
        };
    },
    computed: {
        reachableMazeCards: function () {
            const playerId = this.gameStore.currentPlayer?.id;
            if (playerId !== undefined) {
                return this.computeReachableMazeCards(playerId);
            }
            return new Set();
        },
        currentPlayerColor: function () {
            return this.gameStore.currentPlayer?.pieceIndex;
        },
        isTouchDevice: function () {
            // https://stackoverflow.com/a/4819886/359287
            return (
                "ontouchstart" in window ||
                navigator.maxTouchPoints > 0 ||
                navigator.msMaxTouchPoints > 0
            );
        },
        viewBox: function () {
            const offset = this.isTouchDevice ? -16 : -100;
            const interactionSize = this.$ui.cardSize * this.boardState.mazeSize + 2 * -offset;
            return `${offset} ${offset} ${interactionSize} ${interactionSize}`;
        },
        ...mapState(useBoardStore, {
            boardMazeCardAt: "mazeCard",
            leftoverMazeCardRotation: (store) => store.leftoverMazeCard.rotation,
            boardState: (store) => store,
            mazeSize: "mazeSize",
        }),
        ...mapState(usePlayersStore, {
            userPlayerId: "userPlayerId",
            userAction: (store) => store.userPlayer?.nextAction ?? action.NO_ACTION,
            mazeCardOfPlayer: "mazeCard",
        }),
        ...mapStores(useGameStore),
    },
    methods: {
        computeReachableMazeCards: function (playerId) {
            const playerCard = this.mazeCardOfPlayer(playerId);
            if (playerCard?.location) {
                let pieceLocation = playerCard.location;
                let graph = new Graph(this.boardState);
                let locations = graph.reachableLocations(pieceLocation);
                return new Set(locations.map((location) => this.boardMazeCardAt(location)));
            } else {
                return new Set();
            }
        },
        onPlayerShift: function (shiftLocation) {
            let shiftAction = {
                playerId: this.userPlayerId,
                location: shiftLocation,
                leftoverRotation: this.leftoverMazeCardRotation,
            };
            this.gameStore.shift(shiftAction);
        },
        onPlayerMove: function (mazeCard) {
            if (this.isMoveValid(mazeCard.location)) {
                let moveAction = {
                    playerId: this.userPlayerId,
                    targetLocation: mazeCard.location,
                };
                this.gameStore.move(moveAction);
            }
        },
        isMoveValid: function (targetLocation) {
            if (this.userAction === action.MOVE_ACTION) {
                const sourceLocation = this.mazeCardOfPlayer(this.userPlayerId).location;
                return new Graph(this.boardState).isReachable(sourceLocation, targetLocation);
            }
            return false;
        },
    },
};
</script>

<style lang="scss">
.interactive-board {
    position: absolute;
    width: 100%;
    height: 100%;

    touch-action: none;
}
</style>
