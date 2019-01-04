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
        <rect
            v-for="insertPanel in insertPanels"
            @click="onInsertPanelClick($event, insertPanel)"
            :key="'panel-' + insertPanel.id"
            :x="xPos(insertPanel.displayLocation) + boardOffset"
            :y="yPos(insertPanel.displayLocation) + boardOffset"
            :height="cardSize"
            :width="cardSize"
            class="insert-location"
            :class="insertPanelClass(insertPanel)"
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
import MazeCard from "@/model/mazeCard.js";
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
    watch: {
        disabledInsertLocation: function() {
            console.log("called");
            this.updateDisabledInsertLocation();
        }
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
        xPos(location) {
            return this.cardSize * location.column;
        },
        yPos(location) {
            return this.cardSize * location.row;
        },
        onInsertPanelClick: function(event, insertPanel) {
            if (this.isMyTurnToShift && insertPanel.enabled) {
                let insertEvent = {
                    location: insertPanel.insertLocation,
                    leftoverRotation: this.leftoverMazeCard.rotation
                };
                this.$emit("insert-card", insertEvent);
            }
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
        },
        locationsEqual(locA, locB) {
            return locA && locB && locA.row === locB.row && locA.column === locB.column;
        },
        updateDisabledInsertLocation: function() {
            let disabledInsertLocation = this.game.disabledInsertLocation;
            for (var insertPanel of this.insertPanels) {
                if (this.locationsEqual(insertPanel.insertLocation, disabledInsertLocation)) {
                    insertPanel.enabled = false;
                } else {
                    insertPanel.enabled = true;
                }
            }
        },
        inside: function(value, min, max) {
            return Math.min(Math.max(value, min), max);
        },
        panelToInsertLocation: function(location) {
            return {
                row: this.inside(location.row, 0, this.mazeSize - 1),
                column: this.inside(location.column, 0, this.mazeSize - 1)
            };
        },
        createInsertPanel: function(id, row, column) {
            let displayLocation = {
                row: row,
                column: column
            };
            return {
                id: id,
                displayLocation: displayLocation,
                insertLocation: this.panelToInsertLocation(displayLocation),
                enabled: true
            };
        },
        insertPanelClass: function(insertPanel) {
            if (insertPanel.enabled) {
                if (this.isMyTurnToShift) {
                    return ["insert-location--enabled", "insert-location--interaction"];
                }
                return "insert-location--enabled";
            } else {
                return "insert-location--disabled";
            }
        }
    },
    created: function() {
        let id = 0;
        for (var position of [1, 3, 5]) {
            this.insertPanels.push(this.createInsertPanel(id++, -1, position));
            this.insertPanels.push(this.createInsertPanel(id++, position, -1));
            this.insertPanels.push(this.createInsertPanel(id++, this.game.n, position));
            this.insertPanels.push(this.createInsertPanel(id++, position, this.game.n));
        }
        this.updateDisabledInsertLocation();
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

.insert-location {
    transition: all 0.2s;
    &:not(&--interaction) {
        fill: black;
        opacity: 0.2;
    }

    &--interaction {
        opacity: 0.3;
        cursor: pointer;
        &:hover {
            fill: blue;
        }
    }
}
</style>
