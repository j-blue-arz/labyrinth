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
            :interaction="isMyTurnToShift"
            :card-size="cardSize"
            :game="game"
        ></insert-panels>
        <leftover-maze-card
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
import * as action from "@/model/game.js";
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
        controller: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
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
        game: function() {
            return this.controller.getGame();
        },
        mazeSize: function() {
            return this.game.n;
        },
        userPlayerId: function() {
            return this.controller.getPlayerManager().getUserPlayer();
        },
        interactiveMazeCards: function() {
            if (this.isMyTurnToMove()) {
                let player = this.game.getPlayer(this.userPlayerId);
                if (player) {
                    return this.computeReachableMazeCards(player);
                }
            }
            return new Set([]);
        },
        reachableMazeCards: function() {
            let player = this.game.getPlayer(this.game.nextAction.playerId);
            if (player) {
                return this.computeReachableMazeCards(player);
            }
            return new Set([]);
        },
        currentPlayerColor: function() {
            let player = this.game.getPlayer(this.game.nextAction.playerId);
            if (player) {
                return player.colorIndex;
            }
            return null;
        },
        isMyTurnToShift: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.SHIFT_ACTION
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
        }
    },
    methods: {
        isMyTurnToMove: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.MOVE_ACTION
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
            let shiftAction = {
                playerId: this.userPlayerId,
                location: shiftLocation,
                leftoverRotation: this.leftoverMazeCard.rotation
            };
            this.controller.performShift(shiftAction);
        },
        onMazeCardClick: function(mazeCard) {
            if (
                this.isMyTurnToMove &&
                this.game.isMoveValid(this.userPlayerId, mazeCard.location)
            ) {
                let moveAction = {
                    playerId: this.userPlayerId,
                    targetLocation: mazeCard.location
                };
                this.controller.performMove(moveAction);
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
