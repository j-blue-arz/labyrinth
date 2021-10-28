<template>
    <v-game-board
        @pointerdown.native="pointerDown($event)"
        @pointermove.native="pointerMove($event)"
        @pointerup.native="endDrag()"
        @pointercancel.native="pointercancel($event)"
        :interactive-maze-cards="interactiveMazeCards"
        :current-player-color="currentPlayerColor"
        :reachable-cards="reachableCards"
        :required-action="userAction"
        :drag="{ row: dragRow, column: dragColumn, offset: dragOffset }"
        @player-move="onMazeCardClicked"
    ></v-game-board>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";
import { locationsEqual, getShiftLocations, loc } from "@/store/modules/board.js";
import { MOVE_ACTION, SHIFT_ACTION, NO_ACTION } from "@/model/player.js";
import { Vector, bound } from "@/model/2d.js";
import { ShiftLocation } from "@/model/shift.js";

export default {
    name: "draggable-game-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard
    },
    props: {
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
            dragStart: null,
            dragLocation: null,
            dragOffset: 0,
            dragRow: null,
            dragColumn: null
        };
    },
    computed: {
        mazeSize: function() {
            return this.$store.state.board.mazeSize;
        },
        shiftLocations: function() {
            const n = this.mazeSize;
            return getShiftLocations(n).map(location => new ShiftLocation(location, n));
        },
        dragInteractiveLocations: function() {
            let result = new Set();
            for (let shiftLocation of this.shiftLocations) {
                shiftLocation
                    .affectedLocations(this.mazeSize)
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
                    result.add(this.$store.getters["board/mazeCard"](location));
                }
                return result;
            } else {
                return new Set();
            }
        },
        possibleDragDirections: function() {
            let result = [];
            if (this.dragLocation) {
                const disabledShiftLocation = this.$store.state.board.disabledShiftLocation;
                for (let shiftLocation of this.shiftLocations) {
                    if (!locationsEqual(disabledShiftLocation, shiftLocation)) {
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
        startDrag: function(svgPosition) {
            this.resetDrag();
            if (this.userAction === SHIFT_ACTION) {
                let location = this.getLocation(svgPosition);
                let mazeCard = this.$store.getters["board/mazeCard"](location);
                if (mazeCard) {
                    if (this.isDraggable(location)) {
                        this.dragLocation = location;
                        this.dragStart = svgPosition;
                    }
                }
            }
        },
        drag: function(svgPosition) {
            let offset = this.dragStart.to(svgPosition);
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
        endDrag: function() {
            if (Math.abs(this.dragOffset) > this.SHIFT_DRAG_THRESHOLD) {
                this.emitShiftEvent();
            }
            this.resetDrag();
        },
        resetDrag: function() {
            this.dragRow = null;
            this.dragColumn = null;
            this.dragStart = null;
            this.dragLocation = null;
            this.dragOffset = 0;
        },
        pointerDown: function($event) {
            this.startDrag(this.getPointerPosition($event));
        },
        pointerMove: function($event) {
            if (this.dragLocation !== null) {
                this.drag(this.getPointerPosition($event));
            }
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
                    shiftLocation = loc(this.dragRow, this.mazeSize - 1);
                }
            } else if (this.dragColumn) {
                if (this.dragOffset > 0) {
                    shiftLocation = loc(0, this.dragColumn);
                } else {
                    shiftLocation = loc(this.mazeSize - 1, this.dragColumn);
                }
            }
            if (shiftLocation) {
                this.$emit("player-shift", shiftLocation);
            }
        },
        getPointerPosition: function(evt) {
            const svg = evt.currentTarget;
            return this.getSVGPosition(evt.clientX, evt.clientY, svg);
        },
        getSVGPosition: function(clientX, clientY, svg) {
            const CTM = svg.getScreenCTM();
            return new Vector((clientX - CTM.e) / CTM.a, (clientY - CTM.f) / CTM.d);
        },
        getLocation: function(svgPosition) {
            let locationVector = svgPosition.dividedBy(this.$ui.cardSize);
            let column = Math.floor(locationVector.x);
            let row = Math.floor(locationVector.y);
            return loc(row, column);
        },
        onMazeCardClicked: function(mazeCard) {
            this.$emit("player-move", mazeCard);
        }
    },
    created() {
        this.DRAG_BOUND = 100;
        this.SHIFT_DRAG_THRESHOLD = this.$ui.cardSize / 2;
    }
};
</script>

<style lang="scss"></style>
