<template>
    <svg
        :x="$ui.boardOffset - borderWidth"
        :y="$ui.boardOffset - borderWidth"
        :width="boardSize + 2 * borderWidth"
        :height="boardSize + 2 * borderWidth"
        @mousedown="startDrag($event)"
        @mousemove="drag($event)"
        @mouseup="endDrag($event)"
        @mouseleave="endDrag($event)"
    >
        <v-game-board
            :board-size="boardSize"
            :border-width="borderWidth"
            :maze-cards="mazeCards"
            :interactive-maze-cards="interactiveMazeCards"
            :current-player-color="currentPlayerColor"
            :reachable-cards="reachableCards"
            :drag="{ row: dragRow, column: dragColumn, offset: dragOffset }"
            @maze-card-clicked="onMazeCardClicked"
        ></v-game-board>
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";
import { locationsEqual, loc } from "@/model/game.js";

export default {
    name: "draggable-game-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard
    },
    props: {
        game: {
            type: Object,
            required: true
        },
        userHasToShift: {
            type: Boolean,
            required: true
        },
        interactiveMazeCards: {
            required: false,
            default: () => new Set([])
        },
        reachableCards: {
            required: false,
            default: () => new Set([])
        },
        currentPlayerColor: {
            required: false,
            default: null
        }
    },
    data() {
        return {
            mouseStart: null,
            dragLocation: null,
            dragOffset: 0,
            dragRow: null,
            dragColumn: null
        };
    },
    computed: {
        boardSize: function() {
            return this.$ui.cardSize * this.game.n;
        },
        borderWidth: function() {
            return Math.floor(this.$ui.cardSize / 6);
        },
        mazeCards: function() {
            return this.game.mazeCardsAsList();
        },
        shiftableRows: function() {
            let result = new Array(this.game.n - 1).fill(false);
            let shiftLocations = this.game.getShiftLocations();
            for (let location of shiftLocations) {
                if (location.column == 0 || location.column == this.game.n - 1) {
                    result[location.row] = true;
                }
            }
            return result;
        },
        shiftableColumns: function() {
            let result = new Array(this.game.n - 1).fill(false);
            let shiftLocations = this.game.getShiftLocations();
            for (let location of shiftLocations) {
                if (location.row == 0 || location.row == this.game.n - 1) {
                    result[location.column] = true;
                }
            }
            return result;
        },
        canDragRow: function() {
            if (this.dragLocation) {
                return this.shiftableRows[this.dragLocation.row];
            }
            return false;
        },
        canDragColumn: function() {
            if (this.dragLocation) {
                return this.shiftableColumns[this.dragLocation.column];
            }
            return false;
        }
    },
    methods: {
        startDrag: function($event) {
            this.endDrag();
            if (this.userHasToShift) {
                let mousePosition = this.getMousePosition($event);
                let location = this.getLocation(mousePosition);
                let mazeCard = this.getMazeCard(location);
                if (mazeCard) {
                    if (
                        this.shiftableColumns[location.column] ||
                        this.shiftableRows[location.row]
                    ) {
                        this.dragLocation = location;
                        this.mouseStart = mousePosition;
                    }
                }
            }
        },
        drag: function($event) {
            if (this.dragLocation !== null) {
                $event.preventDefault();
                let mousePosition = this.getMousePosition($event);
                let offset = this.offset(this.mouseStart, mousePosition);
                let boundingBox = { xMin: -100, xMax: 100, yMin: -100, yMax: 100 };
                if (this.game.disabledShiftLocation) {
                    const disabled = this.game.disabledShiftLocation;
                    if (this.dragLocation.row === disabled.row) {
                        if (disabled.column === 0) {
                            boundingBox.xMax = 0;
                        } else {
                            boundingBox.xMin = 0;
                        }
                    } else if (this.dragLocation.column == disabled.column) {
                        if (disabled.row === 0) {
                            boundingBox.yMax = 0;
                        } else {
                            boundingBox.yMin = 0;
                        }
                    }
                }
                offset = {
                    x: bound(offset.x, boundingBox.xMin, boundingBox.xMax),
                    y: bound(offset.y, boundingBox.yMin, boundingBox.yMax)
                };
                if (this.canDragRow && this.canDragColumn) {
                    if (Math.abs(offset.x) >= Math.abs(offset.y)) {
                        this.dragHorizontally(offset);
                    } else {
                        this.dragVertically(offset);
                    }
                } else if (this.canDragRow) {
                    this.dragHorizontally(offset);
                } else if (this.canDragColumn) {
                    this.dragVertically(offset);
                }
            }

            function bound(value, min, max) {
                return Math.min(Math.max(value, min), max);
            }
        },
        dragHorizontally: function(offset) {
            this.dragOffset = offset.x;
            this.dragRow = this.dragLocation.row;
            this.dragColumn = null;
        },
        dragVertically: function(offset) {
            this.dragOffset = offset.y;
            this.dragRow = null;
            this.dragColumn = this.dragLocation.column;
        },
        endDrag: function($event) {
            this.dragRow = null;
            this.dragColumn = null;
            this.mouseStart = null;
            this.dragLocation = null;
            this.dragOffset = 0;
        },
        offset: function(from, to) {
            return {
                x: to.x - from.x,
                y: to.y - from.y
            };
        },
        getMousePosition: function(evt) {
            const svg = evt.currentTarget;
            const CTM = svg.getScreenCTM();
            return {
                x: (evt.clientX - CTM.e) / CTM.a,
                y: (evt.clientY - CTM.f) / CTM.d
            };
        },
        getLocation: function(mousePosition) {
            let column = Math.floor((mousePosition.x - this.$ui.boardOffset) / this.$ui.cardSize);
            let row = Math.floor((mousePosition.y - this.$ui.boardOffset) / this.$ui.cardSize);
            return loc(row, column);
        },
        getMazeCard: function(location) {
            let mazeCard = this.mazeCards.find(mazeCard =>
                locationsEqual(mazeCard.location, location)
            );
            return mazeCard;
        },
        onMazeCardClicked: function(mazeCard) {
            this.$emit("maze-card-clicked", mazeCard);
        }
    }
};
</script>

<style lang="scss"></style>
