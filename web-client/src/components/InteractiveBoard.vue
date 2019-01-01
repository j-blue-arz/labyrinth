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
            :board-offset="boardOffset"
            :card-size="cardSize"
            :player-id="playerId"
            :game="game"
        ></v-move-animation>
        <rect
            v-for="(insertPanel, itemIndex) in insertPanels"
            @click="onInsertPanelClick($event, itemIndex)"
            :key="insertPanel.id"
            :x="xPos(insertPanel) + boardOffset"
            :y="yPos(insertPanel) + boardOffset"
            :height="cardSize"
            :width="cardSize"
            class="interactive-board__insert-location"
            :class="{interaction: isMyTurnToShift}"
        ></rect>
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
import VMazeCard from "@/components/VMazeCard.vue";
import VMoveAnimation from "@/components/VMoveAnimation.vue";
import VSvgDefs from "@/components/VSvgDefs.vue";
import Game, * as action from "@/model/game.js";
import MazeCard from "@/model/mazecard.js";
import Graph from "@/model/mazeAlgorithm.js";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard,
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
        playerId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            insertPanels: [
                { id: 0, row: -1, column: 1 },
                { id: 1, row: -1, column: 3 },
                { id: 2, row: -1, column: 5 },
                { id: 3, row: this.game.n, column: 1 },
                { id: 4, row: this.game.n, column: 3 },
                { id: 5, row: this.game.n, column: 5 },
                { id: 6, row: 1, column: -1 },
                { id: 7, row: 3, column: -1 },
                { id: 8, row: 5, column: -1 },
                { id: 9, row: 1, column: this.game.n },
                { id: 10, row: 3, column: this.game.n },
                { id: 11, row: 5, column: this.game.n }
            ]
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
                let player = this.game.getPlayer(this.playerId);
                let pieceLocation = player.mazeCard.location;
                let graph = new Graph(this.game);
                let locations = graph.reachableLocations(pieceLocation);
                return new Set(locations.map(location => this.game.getMazeCard(location)));
            }
        },
        isMyTurnToShift: function() {
            return (
                this.game.nextAction.playerId === this.playerId &&
                this.game.nextAction.action === action.SHIFT_ACTION &&
                !this.game.getPlayer(this.playerId).isComputer
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
        }
    },
    methods: {
        isMyTurnToMove: function() {
            return (
                this.game.nextAction.playerId === this.playerId &&
                this.game.nextAction.action === action.MOVE_ACTION &&
                !this.game.getPlayer(this.playerId).isComputer
            );
        },
        xPos(location) {
            return this.cardSize * location.column;
        },
        yPos(location) {
            return this.cardSize * location.row;
        },
        toInsidePosition(maybeOutside) {
            if (maybeOutside === -1) {
                return 0;
            }
            if (maybeOutside === this.mazeSize) {
                return this.mazeSize - 1;
            }
            return maybeOutside;
        },
        onInsertPanelClick: function(event, itemIndex) {
            if (this.isMyTurnToShift) {
                let insertPanel = this.insertPanels[itemIndex];
                let insertEvent = {
                    location: {
                        row: this.toInsidePosition(insertPanel.row),
                        column: this.toInsidePosition(insertPanel.column)
                    },
                    leftoverRotation: this.leftoverMazeCard.rotation
                };
                this.$emit("insert-card", insertEvent);
            }
        },
        onMazeCardClick: function(mazeCard) {
            if (this.isMyTurnToMove && this.game.isMoveValid(this.playerId, mazeCard.location)) {
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
    &__insert-location {
        transition: all 0.2s;
        &:not(.interaction) {
            fill: black;
            opacity: 0.2;
        }

        &.interaction {
            opacity: 0.3;
            cursor: pointer;
            &:hover {
                fill: blue;
            }
        }
    }
}
</style>
