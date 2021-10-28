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
import * as action from "@/model/player.js";
import Graph from "@/model/Graph.js";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        DraggableGameBoard,
        InsertPanels,
        VMazeCard,
        VSvgDefs
    },
    data() {
        return {
            leftoverX: 0,
            leftoverY: 0,
            isLandscape: true
        };
    },
    computed: {
        userPlayerId: function() {
            return this.$store.getters["players/userPlayerId"];
        },
        reachableMazeCards: function() {
            const playerId = this.$store.getters["game/currentPlayer"]?.id;
            if (playerId) {
                return this.computeReachableMazeCards(playerId);
            }
            return new Set();
        },
        currentPlayerColor: function() {
            return this.$store.getters["game/currentPlayer"]?.pieceIndex;
        },
        userAction: function() {
            return this.$store.getters["players/userPlayer"]?.nextAction ?? action.NO_ACTION;
        },
        isTouchDevice: function() {
            // https://stackoverflow.com/a/4819886/359287
            return (
                "ontouchstart" in window ||
                navigator.maxTouchPoints > 0 ||
                navigator.msMaxTouchPoints > 0
            );
        },
        viewBox: function() {
            const offset = this.isTouchDevice ? -16 : -100;
            const interactionSize =
                this.$ui.cardSize * this.$store.state.board.mazeSize + 2 * -offset;
            return `${offset} ${offset} ${interactionSize} ${interactionSize}`;
        }
    },
    methods: {
        computeReachableMazeCards: function(playerId) {
            const playerCard = this.$store.getters["players/mazeCard"](playerId);
            if (playerCard?.location) {
                let pieceLocation = playerCard.location;
                let graph = new Graph(this.$store.state.board);
                let locations = graph.reachableLocations(pieceLocation);
                return new Set(
                    locations.map(location => this.$store.getters["board/mazeCard"](location))
                );
            } else {
                return new Set();
            }
        },
        onPlayerShift: function(shiftLocation) {
            let shiftAction = {
                playerId: this.userPlayerId,
                location: shiftLocation,
                leftoverRotation: this.$store.getters["board/leftoverMazeCard"].rotation
            };
            this.$store.dispatch("game/shift", shiftAction);
        },
        onPlayerMove: function(mazeCard) {
            if (this.isMoveValid(mazeCard.location)) {
                let moveAction = {
                    playerId: this.userPlayerId,
                    targetLocation: mazeCard.location
                };
                this.$store.dispatch("game/move", moveAction);
            }
        },
        isMoveValid: function(targetLocation) {
            const sourceLocation = this.$store.getters["players/mazeCard"](this.userPlayerId)
                .location;
            return (
                this.userAction === action.MOVE_ACTION &&
                new Graph(this.$store.state.board).isReachable(sourceLocation, targetLocation)
            );
        }
    }
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
