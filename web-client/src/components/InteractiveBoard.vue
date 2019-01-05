<template>
    <svg :viewBox="`0 0 ${interactionSize} ${interactionSize}`" class="interactive-board">
        <v-svg-defs></v-svg-defs>
        <v-game-board
            @maze-card-clicked="onMazeCardClick"
            :board-offset="boardOffset"
            :n="mazeSize"
            :maze-cards="mazeCards"
            :card-size="cardSize"
            :interactive-maze-cards="interactiveMazeCards"
        ></v-game-board>
        <v-move-animation
            v-for="player in players"
            :key="'player-' + player.id"
            :board-offset="boardOffset"
            :card-size="cardSize"
            :player="player"
            :maze-card-id="player.mazeCard.id"
            :game="game"
        ></v-move-animation>
        <insert-panels
            @insert-panel-clicked="onInsertPanelClick"
            :disabledInsertLocation="disabledInsertLocation"
            :interaction="isMyTurnToShift"
            :cardSize="cardSize"
            />
        <v-maze-card
            @click.native="onLeftoverClick"
            v-if="hasStarted"
            :maze-card="leftoverMazeCard"
            :card-size="cardSize"
            class="interactive-board__leftover"
            ref="leftover"
            :class="{interaction: isMyTurnToShift}"
            overflow="visible"
        ></v-maze-card>
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";
import InsertPanels from "@/components/InsertPanels.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import VMoveAnimation from "@/components/VMoveAnimation.vue";
import VSvgDefs from "@/components/VSvgDefs.vue";
import Game, * as action from "@/model/game.js";
import MazeCard from "@/model/mazeCard.js";
import Graph from "@/model/mazeAlgorithm.js";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard,
        InsertPanels,
        VMazeCard,
        VMoveAnimation,
        VSvgDefs
    },
    props: {
        game: {
            type: Game,
            required: true
        },
        cardSize: {
            type: Number,
            required: true
        },
        userPlayerId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            insertPanels: []
        };
    },
    computed: {
        mazeSize: function() {
            return this.game.n;
        },
        interactiveMazeCards: function() {
            if (!this.isMyTurnToMove() || this.game.isLoading) {
                return new Set([]);
            } else {
                let player = this.game.getPlayer(this.userPlayerId);
                let pieceLocation = player.mazeCard.location;
                let graph = new Graph(this.game);
                let locations = graph.reachableLocations(pieceLocation);
                return new Set(locations.map(location => this.game.getMazeCard(location)));
            }
        },
        isMyTurnToShift: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.SHIFT_ACTION &&
                !this.game.getPlayer(this.userPlayerId).isComputer
            );
        },
        interactionSize: function() {
            return this.cardSize * (this.mazeSize + 2);
        },
        boardOffset: function() {
            return this.cardSize;
        },
        mazeCards: function() {
            return this.game.mazeCardsAsList();
        },
        hasStarted: function() {
            return this.game.leftoverMazeCard instanceof MazeCard;
        },
        leftoverMazeCard: function() {
            return this.game.leftoverMazeCard;
        },
        players: function() {
            return this.game.getPlayers();
        },
        disabledInsertLocation: function() {
            return this.game.disabledInsertLocation;
        }
    },
    methods: {
        isMyTurnToMove: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.MOVE_ACTION &&
                !this.game.getPlayer(this.userPlayerId).isComputer
            );
        },
        onInsertPanelClick: function(insertLocation) {
            let insertEvent = {
                location: insertLocation,
                leftoverRotation: this.leftoverMazeCard.rotation
            };
            this.$emit("insert-card", insertEvent);
        },
        onMazeCardClick: function(mazeCard) {
            if (
                this.isMyTurnToMove &&
                this.game.isMoveValid(this.userPlayerId, mazeCard.location)
            ) {
                this.$emit("move-piece", mazeCard.location);
            }
        },
        onLeftoverClick: function() {
            if (this.isMyTurnToShift) {
                this.leftoverMazeCard.rotateClockwise();
            }
        }
    }
};
</script>

<style lang="scss">
.interactive-board {
    top: 0;
    left: 0;
    max-height: 100%;
    max-width: 100%;
    height: 100%;
}
</style>
