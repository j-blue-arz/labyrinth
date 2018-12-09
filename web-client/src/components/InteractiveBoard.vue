<template>
    <svg :viewBox="`0 0 ${interactionSize} ${interactionSize}`" class="interactive-board">
        <v-game-board
            @maze-card-clicked="onMazeCardClick"
            :board-offset="boardOffset"
            :n="mazeSize"
            :maze-cards="mazeCards"
            :card-size="cardSize"
        ></v-game-board>
        <rect
            v-for="(insertPanel, itemIndex) in insertPanels"
            @click="onInsertPanelClick($event, itemIndex)"
            :key="insertPanel.id"
            :x="xPos(insertPanel) + boardOffset"
            :y="yPos(insertPanel) + boardOffset"
            :height="cardSize"
            :width="cardSize"
            class="interactive-board__insert-location"
        ></rect>
        <v-maze-card
            @click.native="onLeftoverClick"
            v-if="hasStarted"
            :maze-card="leftoverMazeCard"
            :card-size="cardSize"
            class="interactive-board__leftover"
            ref="leftover"
        ></v-maze-card>
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import Game, * as action from "@/model/game.js";
import MazeCard from "@/model/mazecard.js";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard,
        VMazeCard
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
        playerToAct: function() {
            return this.game.nextAction;
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
            if (
                this.playerToAct.playerId === this.playerId &&
                this.playerToAct.action === action.SHIFT_ACTION
            ) {
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
            if (
                this.playerToAct.playerId === this.playerId &&
                this.playerToAct.action === action.MOVE_ACTION
            ) {
                this.$emit("move-piece", mazeCard.location);
            }
        },
        onLeftoverClick: function() {
            if (
                this.playerToAct.playerId === this.playerId &&
                this.playerToAct.action === action.SHIFT_ACTION
            ) {
                this.game.leftoverMazeCard.rotateClockwise();
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
    width: 900px;

    &__insert-location {
        opacity: 0.1;
        cursor: pointer;
    }

    &__leftover {
        top: 100px;
        cursor: pointer;
    }
}
</style>
