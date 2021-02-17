<template>
    <svg :viewBox="`0 0 ${interactionSize} ${interactionSize}`" class="interactive-board">
        <v-svg-defs></v-svg-defs>
        <draggable-game-board
            @player-move="onPlayerMove"
            @player-shift="onPlayerShift"
            :game="game"
            :current-player-color="currentPlayerColor"
            :reachable-cards="reachableMazeCards"
            :user-action="userAction"
        ></draggable-game-board>
        <v-move-animation
            v-for="player in players"
            :key="'player-' + player.id"
            :player="player"
            :maze-card-id="player.mazeCard.id"
            :game="game"
        ></v-move-animation>
        <insert-panels
            @player-shift="onPlayerShift"
            :interaction="isMyTurnToShift"
            :game="game"
        ></insert-panels>
    </svg>
</template>

<script>
import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import InsertPanels from "@/components/InsertPanels.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import VMoveAnimation from "@/components/VMoveAnimation.vue";
import VSvgDefs from "@/components/VSvgDefs.vue";
import * as action from "@/model/player.js";
import Graph from "@/model/mazeAlgorithm.js";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        DraggableGameBoard,
        InsertPanels,
        VMazeCard,
        VMoveAnimation,
        VSvgDefs
    },
    props: {
        controller: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            leftoverX: 0,
            leftoverY: 0,
            isLandscape: true
        };
    },
    computed: {
        game: function() {
            return this.controller.game;
        },
        mazeSize: function() {
            return this.game.n;
        },
        userPlayerId: function() {
            return this.controller.playerManager.getUserPlayerId();
        },
        reachableMazeCards: function() {
            let player = this.game.getPlayer(this.game.nextAction.playerId);
            if (player) {
                return this.computeReachableMazeCards(player);
            }
            return new Set();
        },
        currentPlayerColor: function() {
            let player = this.game.getPlayer(this.game.nextAction.playerId);
            if (player) {
                return player.colorIndex;
            }
            return null;
        },
        isMyTurnToShift: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.SHIFT_ACTION
            );
        },
        players: function() {
            return this.game.getPlayers();
        },
        userAction: function() {
            let player = this.game.getPlayer(this.userPlayerId);
            if (player) {
                return player.getTurnAction();
            }
            return action.NO_ACTION;
        },
        interactionSize: function() {
            return this.$ui.cardSize * (this.mazeSize + 2);
        }
    },
    methods: {
        isMyTurnToMove: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.MOVE_ACTION
            );
        },
        computeReachableMazeCards: function(player) {
            if (!player.mazeCard.isLeftoverLocation()) {
                let pieceLocation = player.mazeCard.location;
                let graph = new Graph(this.game);
                let locations = graph.reachableLocations(pieceLocation);
                return new Set(locations.map(location => this.game.getMazeCard(location)));
            } else {
                return new Set();
            }
        },
        onPlayerShift: function(shiftLocation) {
            let shiftAction = {
                playerId: this.userPlayerId,
                location: shiftLocation,
                leftoverRotation: this.game.leftoverMazeCard.rotation
            };
            this.controller.performShift(shiftAction);
        },
        onPlayerMove: function(mazeCard) {
            if (
                this.isMyTurnToMove() &&
                this.game.isMoveValid(this.userPlayerId, mazeCard.location)
            ) {
                let moveAction = {
                    playerId: this.userPlayerId,
                    targetLocation: mazeCard.location
                };
                this.controller.performMove(moveAction);
            }
        }
    }
};
</script>

<style lang="scss">
.interactive-board {
    position: absolute;
    width: 100%;
    height: 100%;
}
</style>
