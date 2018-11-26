<template>
  <div class="game-container">
    <interactive-board
      @move-piece="onMovePlayerPiece"
      @insert-card="onInsertCard"
      :n="n"
      :maze-cards="mazeCardsList"
      :card-size="cardSize"
      ref="interactive-board"
    />
    <v-maze-card
      @click.native="onLeftoverClick"
      :maze-card="leftoverMazeCard"
      :card-size="cardSize"
      class="game-container__leftover"
      ref="leftover"
    />
  </div>
</template>


<script>
import axios from "axios";
import Vue from "vue";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazecard.js";
// import { setInterval } from "timers";

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
        }
    },
    data() {
        return {
            n: 7,
            cardSize: 100,
            mazeCards: [],
            leftoverMazeCard: {},
            playerId: 0,
            playerPieces: new Map(),
            timer: "",
            api: ""
        };
    },
    computed: {
        mazeCardsList: function() {
            return [].concat.apply([], this.mazeCards);
        }
    },
    methods: {
        onInsertCard: function(location) {
            var shiftLocations = [];
            if (location.row === -1) {
                shiftLocations = this.columnLocations(location.column);
            } else if (location.row === this.n) {
                shiftLocations = this.columnLocations(location.column);
                shiftLocations.reverse();
            } else if (location.column === this.n) {
                shiftLocations = this.rowLocations(location.row);
                shiftLocations.reverse();
            } else if (location.column === -1) {
                shiftLocations = this.rowLocations(location.row);
            }
            this.shiftAlongLocations(shiftLocations);
        },
        columnLocations: function(column) {
            var locations = [];
            for (let row = 0; row < this.n; row++) {
                locations.push({ row: row, column: column });
            }
            return locations;
        },
        rowLocations: function(row) {
            var locations = [];
            for (let column = 0; column < this.n; column++) {
                locations.push({ row: row, column: column });
            }
            return locations;
        },
        onLeftoverClick: function() {
            this.leftoverMazeCard.rotateClockwise();
        },
        onMovePlayerPiece: function(targetLocation) {
            var targetMazeCard = this.getMazeCard(targetLocation);
            var postMovePath = this.api + "/games/0/move?p_id=" + this.playerId;
            axios
                .post(postMovePath, {
                    location: targetMazeCard.location
                })
                .catch(error => {
                    console.error(error.response.data.userMessage);
                });

            var playerPiece = this.playerPieces.get(this.playerId);
            var index = playerPiece.mazeCard.playerPieces.indexOf(playerPiece);
            playerPiece.mazeCard.playerPieces.splice(index, 1);

            targetMazeCard.playerPieces.push(playerPiece);
            playerPiece.mazeCard = targetMazeCard;
        },
        getMazeCard: function(location) {
            return this.mazeCards[location.row][location.column];
        },
        setMazeCard: function(location, mazeCard) {
            this.mazeCards[location.row][location.column] = mazeCard;
        },
        mazeCardById: function(id) {
            for (var row = 0; row < this.n; row++) {
                for (var col = 0; col < this.n; col++) {
                    if (this.mazeCards[row][col].id == id) {
                        return this.mazeCards[row][col];
                    }
                }
            }
        },
        shiftAlongLocations: function(locations) {
            var pushedCard = this.leftoverMazeCard;
            var postShiftPath =
                this.api + "/games/0/shift?p_id=" + this.playerId;
            axios
                .post(postShiftPath, {
                    location: locations[0],
                    leftoverRotation: pushedCard.rotation
                })
                .catch(error => {
                    console.error(error.response.data.userMessage);
                });

            this.leftoverMazeCard = this.getMazeCard(locations[this.n - 1]);
            this.leftoverMazeCard.setLeftoverLocation();
            for (let i = this.n - 1; i > 0; i--) {
                this.setMazeCard(
                    locations[i],
                    this.getMazeCard(locations[i - 1])
                );
                this.getMazeCard(locations[i]).setLocation(locations[i]);
            }
            this.transferPlayerPieces(this.leftoverMazeCard, pushedCard);
            var first = locations[0];
            pushedCard.setLocation(first);
            Vue.set(this.mazeCards[first.row], first.column, pushedCard);
        },
        transferPlayerPieces: function(sourceMazeCard, targetMazeCard) {
            while (sourceMazeCard.playerPieces.length) {
                var piece = sourceMazeCard.playerPieces.pop();
                piece.mazeCard = targetMazeCard;
                targetMazeCard.playerPieces.push(piece);
            }
        },
        compareApiLocations: function(a, b) {
            if (a.row == b.row) {
                return a.column - b.column;
            }
            return a.row - b.row;
        },
        getApiState: function() {
            var getStatePath =
                this.api + "/games/0/state?p_id=" + this.playerId;
            axios
                .get(getStatePath)
                .then(response => this.createFromApiState(response.data))
                .catch(error => {
                    console.error(error.response.data.userMessage);
                });
        },
        createFromApiState: function(apiState) {
            console.log(apiState.mazeCards);
            apiState.mazeCards.forEach(card => {
                if (card.location === null) {
                    card.location = {
                        row: -1,
                        column: -1
                    };
                }
            });
            apiState.mazeCards.sort((card1, card2) =>
                this.compareApiLocations(card1.location, card2.location)
            );
            console.log(apiState.mazeCards);
            this.leftoverMazeCard = MazeCard.createFromApi(
                apiState.mazeCards[0]
            );
            this.mazeCards.splice(0, this.n);
            var index = 1;
            for (var row = 0; row < this.n; row++) {
                this.mazeCards.push([]);
                for (var col = 0; col < this.n; col++) {
                    this.mazeCards[row].push(
                        MazeCard.createFromApi(apiState.mazeCards[index])
                    );
                    index++;
                }
            }
            this.playerPieces.clear();
            apiState.players.forEach(player => {
                var playerMazeCard = this.mazeCardById(player.mazeCardId);
                var playerPiece = {
                    id: player.id,
                    mazeCard: playerMazeCard
                };
                playerMazeCard.playerPieces.push(playerPiece);
                this.playerPieces.set(player.id, playerPiece);
            });
        }
    },
    created: function() {
        this.api = location.protocol + "//" + location.host + "/api";
        var addPlayerPath = this.api + "/games/0/players";
        axios
            .post(addPlayerPath)
            .then(response => (this.playerId = parseInt(response.data)))
            .catch(error => {
                console.error(error.response.data.userMessage);
            });

        this.timer = setInterval(this.getApiState, 800);
        /* var id = 0;
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
                mazeCard: this.getMazeCard(location)
            };
            this.getMazeCard(location).playerPieces.push(playerPiece);
            this.playerPieces.set(i, playerPiece);
        }

        this.leftoverMazeCard = MazeCard.createNewRandom(id, -1, -1); */
    },
    beforeDestroy() {
        clearInterval(this.timer);
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
