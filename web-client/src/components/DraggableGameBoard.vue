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
            :required-action="userAction"
            :drag="{ row: dragRow, column: dragColumn, offset: dragOffset }"
            @player-move="onMazeCardClicked"
        ></v-game-board>
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";
import { locationsEqual, loc, MOVE_ACTION, SHIFT_ACTION, NO_ACTION } from "@/model/game.js";
import { Vector, bound } from "@/model/2d.js";
import { ShiftLocation } from "@/model/shift.js";

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
        userAction: {
            required: false,
            default: NO_ACTION
        },
        reachableCards: {
            required: false,
            default: () => new Set()
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
        shiftLocations: function() {
            let result = [];
            let locations = this.game.getShiftLocations();
            for (let location of locations) {
                result.push(new ShiftLocation(location, this.game.n));
            }
            return result;
        },
        dragInteractiveLocations: function() {
            let result = new Set();
            for (let shiftLocation of this.shiftLocations) {
                shiftLocation
                    .affectedLocations(this.game.n)
                    .forEach(location => result.add(location));
            }
            return result;
        },
        interactiveMazeCards: function() {
            if (this.userAction === MOVE_ACTION) {
                return this.reachableCards;
            } else if (this.userAction === SHIFT_ACTION) {
                let result = new Set();
                for (let location of this.dragInteractiveLocations) {
                    result.add(this.game.getMazeCard(location));
                }
                return result;
            } else {
                return new Set();
            }
        },
        possibleDragDirections: function() {
            let result = [];
            if (this.dragLocation) {
                for (let shiftLocation of this.shiftLocations) {
                    if (!locationsEqual(this.game.disabledShiftLocation, shiftLocation)) {
                        if (shiftLocation.affects(this.dragLocation)) {
                            result.push(shiftLocation.direction);
                        }
                    }
                }
            }
            return result;
        }
    },
    methods: {
        startDrag: function($event) {
            this.endDrag();
            if (this.userAction === SHIFT_ACTION) {
                let mousePosition = this.getMousePosition($event);
                let location = this.getLocation(mousePosition);
                let mazeCard = this.getMazeCard(location);
                if (mazeCard) {
                    if (this.isDraggable(location)) {
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
                for (let direction of ["N", "S", "E", "W"]) {
                    if (!this.possibleDragDirections.includes(direction)) {
                        offset = offset.removeDirectionComponent(direction);
                    }
                }
                if (Math.abs(offset.x) >= Math.abs(offset.y)) {
                    this.dragHorizontally(offset);
                } else {
                    this.dragVertically(offset);
                }
            }
        },
        dragHorizontally: function(offset) {
            this.dragOffset = this.bound(offset.x);
            this.dragRow = this.dragLocation.row;
            this.dragColumn = null;
        },
        dragVertically: function(offset) {
            this.dragOffset = this.bound(offset.y);
            this.dragRow = null;
            this.dragColumn = this.dragLocation.column;
        },
        bound: function(value) {
            return bound(value, -this.DRAG_BOUND, this.DRAG_BOUND);
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
        isDraggable: function(location) {
            for (let shiftLocation of this.shiftLocations) {
                if (shiftLocation.affects(location)) {
                    return true;
                }
            }
            return false;
        },
        emitShiftEvent: function() {
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
                this.$emit("player-shift", shiftLocation);
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
            this.$emit("player-move", mazeCard);
        }
    },
    created() {
        this.BOARD_OFFSET_VECTOR = new Vector(this.$ui.boardOffset, this.$ui.boardOffset);
        this.DRAG_BOUND = 100;
        this.SHIFT_DRAG_THRESHOLD = this.$ui.cardSize / 2;
    }
};
</script>

<style lang="scss"></style>
