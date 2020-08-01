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
            :current-player-color="currentPlayerColor"
            :reachable-cards="reachableMazeCards"
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
            :disabledShiftLocation="disabledShiftLocation"
            :interaction="isMyTurnToShift"
            :card-size="cardSize"
            :n="mazeSize"
        ></insert-panels>
        <leftover-maze-card
            v-if="game.hasStarted()"
            :x="leftoverX"
            :y="leftoverY"
            :card-size="cardSize"
            :is-landscape="!isLandscape"
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
            leftoverY: 0,
            cardSize: 100,
            isLandscape: true
        };
    },
    watch: {
        mazeSize: function() {
            this.handleResize();
        }
    },
    computed: {
        mazeSize: function() {
            return this.game.n;
        },
        interactiveMazeCards: function() {
            if (!this.isMyTurnToMove() || !this.game.hasStarted()) {
                return new Set([]);
            } else {
                let player = this.game.getPlayer(this.userPlayerId);
                return this.computeReachableMazeCards(player);
            }
        },
        reachableMazeCards: function() {
            if (!this.game.hasStarted()) {
                return new Set([]);
            } else {
                let player = this.game.getPlayer(this.game.nextAction.playerId);
                return this.computeReachableMazeCards(player);
            }
        },
        currentPlayerColor: function() {
            if (this.game.hasStarted()) {
                return this.game.getPlayer(this.game.nextAction.playerId).colorIndex;
            } else {
                return null;
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
        disabledShiftLocation: function() {
            return this.game.disabledShiftLocation;
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
        computeReachableMazeCards: function(player) {
            if (!player.mazeCard.isLeftoverLocation()) {
                let pieceLocation = player.mazeCard.location;
                let graph = new Graph(this.game);
                let locations = graph.reachableLocations(pieceLocation);
                return new Set(locations.map(location => this.game.getMazeCard(location)));
            } else {
                return new Set([]);
            }
        },
        onInsertPanelClick: function(shiftLocation) {
            let shiftEvent = {
                playerId: this.userPlayerId,
                location: shiftLocation,
                leftoverRotation: this.leftoverMazeCard.rotation
            };
            this.$emit("perform-shift", shiftEvent);
        },
        onMazeCardClick: function(mazeCard) {
            if (
                this.isMyTurnToMove &&
                this.game.isMoveValid(this.userPlayerId, mazeCard.location)
            ) {
                let moveEvent = {
                    playerId: this.userPlayerId,
                    targetLocation: mazeCard.location
                }
                this.$emit("move-piece", moveEvent);
            }
        },
        interactiveBoardSize: function() {
            return this.cardSize * (this.mazeSize + 2);
        },
        leftoverSize: function() {
            return this.cardSize;
        },
        handleResize: function() {
            if (window.innerWidth > window.innerHeight) {
                this.interactionWidth = this.interactiveBoardSize() + this.leftoverSize() - 45;
                this.interactionHeight = this.interactiveBoardSize();
                this.leftoverX = this.interactiveBoardSize() - 60;
                this.leftoverY = 50;
                this.isLandscape = true;
            } else {
                this.interactionWidth = this.interactiveBoardSize();
                this.interactionHeight = this.interactiveBoardSize() + this.leftoverSize() - 45;
                this.leftoverX = 50;
                this.leftoverY = this.interactiveBoardSize() - 60;
                this.isLandscape = false;
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

<style lang="scss"></style>
