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
            :drag="{ mazeCardId: draggedMazeCardId, offset: dragOffset }"
            @maze-card-clicked="onMazeCardClicked"
        ></v-game-board>
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";

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
            draggedMazeCardId: null,
            dragStart: null,
            dragOffset: null
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
        }
    },
    methods: {
        startDrag: function($event) {
            let mousePosition = this.getMousePosition($event);
            let mazeCard = this.getMazeCard(mousePosition);
            if (mazeCard) {
                this.draggedMazeCardId = mazeCard.id;
                this.dragStart = mousePosition;
            }
            this.dragOffset = { x: 0, y: 0 };
        },
        drag: function($event) {
            if (this.draggedMazeCardId !== null) {
                $event.preventDefault();
                let mousePosition = this.getMousePosition($event);
                this.dragOffset = this.offset(this.dragStart, mousePosition);
            }
        },
        endDrag: function($event) {
            this.draggedMazeCardId = null;
            this.dragStart = null;
            this.dragOffset = { x: 0, y: 0 };
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
        getMazeCard: function(mousePosition) {
            let column = Math.floor((mousePosition.x - this.$ui.boardOffset) / this.$ui.cardSize);
            let row = Math.floor((mousePosition.y - this.$ui.boardOffset) / this.$ui.cardSize);
            let mazeCard = this.mazeCards.find(
                mazeCard => mazeCard.location.row == row && mazeCard.location.column == column
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
