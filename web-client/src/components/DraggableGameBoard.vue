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
import { Vector, BoundingBox, HALF_PLANES } from "@/model/2d.js";

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
        },
        dragBoundingBox: function() {
            let boundingBox = this.DRAG_BOUNDING_BOX;
            if (this.game.disabledShiftLocation) {
                const disabled = this.game.disabledShiftLocation;
                if (this.dragLocation.row === disabled.row) {
                    if (disabled.column === 0) {
                        boundingBox = boundingBox.intersect(HALF_PLANES.left);
                    } else {
                        boundingBox = boundingBox.intersect(HALF_PLANES.right);
                    }
                } else if (this.dragLocation.column == disabled.column) {
                    if (disabled.row === 0) {
                        boundingBox = boundingBox.intersect(HALF_PLANES.upper);
                    } else {
                        boundingBox = boundingBox.intersect(HALF_PLANES.lower);
                    }
                }
            }
            return boundingBox;
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
                let offset = this.mouseStart.to(mousePosition);
                offset = this.dragBoundingBox.bound(offset);
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
            if (Math.abs(this.dragOffset) > this.SHIFT_DRAG_THRESHOLD) {
                this.emitShiftEvent();
            }
            this.dragRow = null;
            this.dragColumn = null;
            this.mouseStart = null;
            this.dragLocation = null;
            this.dragOffset = 0;
        },
        emitShiftEvent() {
            let shiftLocation = null;
            if (this.dragRow) {
                if (this.dragOffset > 0) {
                    shiftLocation = loc(this.dragRow, 0);
                } else {
                    shiftLocation = loc(this.dragRow, this.game.n - 1);
                }
            } else if (this.dragColumn) {
                if (this.dragOffset > 0) {
                    shiftLocation = loc(0, this.dragColumn);
                } else {
                    shiftLocation = loc(this.game.n - 1, this.dragColumn);
                }
            }
            if (shiftLocation) {
                this.$emit("insert-panel-clicked", shiftLocation);
            }
        },
        getMousePosition: function(evt) {
            const svg = evt.currentTarget;
            const CTM = svg.getScreenCTM();
            return new Vector((evt.clientX - CTM.e) / CTM.a, (evt.clientY - CTM.f) / CTM.d);
        },
        getLocation: function(mousePosition) {
            let locationVector = mousePosition
                .minus(this.BOARD_OFFSET_VECTOR)
                .dividedBy(this.$ui.cardSize);
            let column = Math.floor(locationVector.x);
            let row = Math.floor(locationVector.y);
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
    },
    created() {
        this.BOARD_OFFSET_VECTOR = new Vector(this.$ui.boardOffset, this.$ui.boardOffset);
        this.DRAG_BOUNDING_BOX = new BoundingBox(new Vector(-100, -100), new Vector(100, 100));
        this.SHIFT_DRAG_THRESHOLD = this.$ui.cardSize / 2;
    }
};
</script>

<style lang="scss"></style>
