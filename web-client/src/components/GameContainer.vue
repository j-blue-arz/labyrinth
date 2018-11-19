<template>
    <div class="game-container">
        <interactive-board
            @move-piece="onMovePlayerPiece"
            @insert-card="onInsertCard"
            :n="n"
            :maze-cards="mazeCardsList"
            :card-size="cardSize"
            ref="interactive-board" />
        <v-maze-card
            @click.native="onLeftoverClick"
            :maze-card="leftoverMazeCard"
            :card-size="cardSize"
            class="game-container__leftover"
            ref="leftover" />
    </div>
</template>


<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import Vue from "vue";
import MazeCard from "@/model/mazecard.js";

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        VMazeCard
    },
    props: {
        initialPlayerLocations: {
            type: Array,
            required: false,
            default: () => []
        },
        playerId: {
            type: Number,
            required: false,
            default: 0
        }
    },
    data() {
        return {
            n: 7,
            cardSize: 100,
            mazeCards: [],
            leftoverMazeCard: {},
            playerPieces: []
        };
    },
    computed: {
        mazeCardsList: function() {
            return [].concat.apply([], this.mazeCards);
        }
    },
    methods: {
        onInsertCard: function(location) {
            if (location.row === -1) {
                this.shiftSouth(location.column);
            } else if (location.row === this.n) {
                this.shiftNorth(location.column);
            } else if (location.column === this.n) {
                this.shiftWest(location.row);
            } else if (location.column === -1) {
                this.shiftEast(location.row);
            }
        },
        onLeftoverClick: function() {
            this.leftoverMazeCard.rotateClockwise();
        },
        onMovePlayerPiece: function(targetLocation) {
            var playerPiece = this.playerPieces[this.playerId];
            var index = playerPiece.mazeCard.playerPieces.indexOf(playerPiece);
            playerPiece.mazeCard.playerPieces.splice(index, 1);

            var targetMazeCard = this.mazeCardAtLocation(targetLocation);
            targetMazeCard.playerPieces.push(playerPiece);
            playerPiece.mazeCard = targetMazeCard;
        },
        mazeCardAtLocation(location) {
            return this.mazeCards[location.row][location.column];
        },
        shiftSouth: function(column) {
            var tmp = this.leftoverMazeCard;
            this.leftoverMazeCard = this.mazeCards[this.n - 1][column];
            this.leftoverMazeCard.setLeftoverLocation();
            for (var row = this.n - 1; row > 0; row--) {
                this.mazeCards[row][column] = this.mazeCards[row - 1][column];
                this.mazeCards[row][column].location.row = row;
            }
            this.transferPlayerPieces(this.leftoverMazeCard, tmp);
            tmp.setLocation(0, column);
            Vue.set(this.mazeCards[0], column, tmp);
        },
        shiftNorth: function(column) {
            var tmp = this.leftoverMazeCard;
            this.leftoverMazeCard = this.mazeCards[0][column];
            this.leftoverMazeCard.setLeftoverLocation();
            for (var row = 0; row < this.n - 1; row++) {
                this.mazeCards[row][column] = this.mazeCards[row + 1][column];
                this.mazeCards[row][column].location.row = row;
            }
            this.transferPlayerPieces(this.leftoverMazeCard, tmp);
            tmp.setLocation(this.n - 1, column);
            Vue.set(this.mazeCards[this.n - 1], column, tmp);
        },
        shiftWest: function(row) {
            var tmp = this.leftoverMazeCard;
            this.leftoverMazeCard = this.mazeCards[row][0];
            this.leftoverMazeCard.setLeftoverLocation();
            for (var column = 0; column < this.n - 1; column++) {
                this.mazeCards[row][column] = this.mazeCards[row][column + 1];
                this.mazeCards[row][column].location.column = column;
            }
            this.transferPlayerPieces(this.leftoverMazeCard, tmp);
            tmp.setLocation(row, this.n - 1);
            Vue.set(this.mazeCards[row], this.n - 1, tmp);
        },
        shiftEast: function(row) {
            var tmp = this.leftoverMazeCard;
            this.leftoverMazeCard = this.mazeCards[row][this.n - 1];
            this.leftoverMazeCard.setLeftoverLocation();
            for (var column = this.n - 1; column > 0; column--) {
                this.mazeCards[row][column] = this.mazeCards[row][column - 1];
                this.mazeCards[row][column].location.column = column;
            }
            this.transferPlayerPieces(this.leftoverMazeCard, tmp);
            tmp.setLocation(row, 0);
            Vue.set(this.mazeCards[row], 0, tmp);
        },
        transferPlayerPieces: function(sourceMazeCard, targetMazeCard) {
            while (sourceMazeCard.playerPieces.length) {
                var piece = sourceMazeCard.playerPieces.pop();
                piece.mazeCard = targetMazeCard;
                targetMazeCard.playerPieces.push(piece);
            }
        }
    },
    created: function() {
        var id = 0;
        for (var row = 0; row < this.n; row++) {
            this.mazeCards.push([]);
            for (var col = 0; col < this.n; col++) {
                this.mazeCards[row].push(
                    MazeCard.createNewRandom(id, row, col)
                );
                id++;
            }
        }

        var initialPlayerLocations = this.initialPlayerLocations;
        if (initialPlayerLocations.length === 0) {
            initialPlayerLocations.push({
                row: Math.floor(Math.random() * this.n),
                column: Math.floor(Math.random() * this.n)
            });
        }

        for (var i = 0; i < this.initialPlayerLocations.length; i++) {
            var location = this.initialPlayerLocations[i];
            var playerPiece = {
                id: i,
                mazeCard: this.mazeCardAtLocation(location)
            };
            this.mazeCardAtLocation(location).playerPieces.push(playerPiece);
            this.playerPieces.push(playerPiece);
        }

        this.leftoverMazeCard = MazeCard.createNewRandom(id, -1, -1);
    }
};
</script>

<style lang="scss">
.game-container {
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    flex-flow: row wrap;

    &__leftover {
        top: 100px;
        cursor: pointer;
    }
}
</style>
