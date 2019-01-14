<template>
    <svg :viewBox="`0 0 ${interactionWidth} ${interactionHeight}`" class="interactive-board">
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
        ></insert-panels>
        <leftover-maze-card
            :x="leftoverX"
            :y="leftoverY"
            :card-size="cardSize"
            :maze-card="leftoverMazeCard"
            :interaction="isMyTurnToShift"
        ></leftover-maze-card>
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import InsertPanels from "@/components/InsertPanels.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import VMoveAnimation from "@/components/VMoveAnimation.vue";
import VSvgDefs from "@/components/VSvgDefs.vue";
import Game, * as action from "@/model/game.js";
import Graph from "@/model/mazeAlgorithm.js";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard,
        InsertPanels,
        VMazeCard,
        VMoveAnimation,
        VSvgDefs,
        LeftoverMazeCard
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
            insertPanels: [],
            interactionWidth: 900,
            interactionHeight: 900,
            leftoverX: 0,
            leftoverY: 0
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
        boardOffset: function() {
            return this.cardSize;
        },
        mazeCards: function() {
            return this.game.mazeCardsAsList();
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
        landscape: function() {
            return window.innerWidth > window.innerHeight;
        },
        interactiveBoardSize: function() {
            return this.cardSize * (this.mazeSize + 2);
        },
        leftoverSize: function() {
            return this.cardSize;
        },
        leftoverOffset: function() {
            return this.cardSize * 0.5;
        },
        handleResize: function() {
            if (this.landscape()) {
                this.interactionWidth = this.interactiveBoardSize() + this.leftoverSize();
                this.interactionHeight = this.interactiveBoardSize();
                this.leftoverX = this.interactiveBoardSize() - this.leftoverOffset();
                this.leftoverY = this.leftoverOffset();
            } else {
                this.interactionWidth = this.interactiveBoardSize();
                this.interactionHeight = this.interactiveBoardSize() + this.leftoverSize();
                this.leftoverX = this.leftoverOffset();
                this.leftoverY = this.interactiveBoardSize() - this.leftoverOffset();
            }
        }
    },
    created() {
        window.addEventListener("resize", this.handleResize);
        this.handleResize();
    },
    destroyed() {
        window.removeEventListener("resize", this.handleResize);
    }
};
</script>

<style lang="scss">
</style>
