import Vue from "vue";
import MazeCard from "@/model/mazecard.js";
import Player from "@/model/player.js";
import ValueError from "@/util/exceptions";

export const MOVE_ACTION = "MOVE";
export const SHIFT_ACTION = "SHIFT";

export default class Game {
    constructor() {
        this.n = 7;
        this.mazeCards = [];
        this.leftoverMazeCard = {};
        this._players = new Map();
        this.nextAction = { playerId: 0, action: "NONE" };
    }

    mazeCardsAsList() {
        return [].concat.apply([], this.mazeCards);
    }

    mazeCardById(id) {
        for (var row = 0; row < this.mazeCards.length; row++) {
            for (var col = 0; col < this.mazeCards[row].length; col++) {
                if (this.mazeCards[row][col].id == id) {
                    return this.mazeCards[row][col];
                }
            }
        }
        if (this.leftoverMazeCard.id == id) {
            return this.leftoverMazeCard;
        }
        return null;
    }

    getMazeCard(location) {
        if (this._isInside(location)) {
            return this.mazeCards[location.row][location.column];
        } else {
            throw new RangeError();
        }
    }

    setMazeCard(location, mazeCard) {
        if (this._isInside(location)) {
            this.mazeCards[location.row][location.column] = mazeCard;
        } else {
            throw new RangeError();
        }
    }

    shift(location) {
        if (!this._isInside(location)) {
            throw new RangeError();
        }
        var shiftLocations = [];
        if (location.row === 0) {
            shiftLocations = this._columnLocations(location.column);
        } else if (location.row === this.n - 1) {
            shiftLocations = this._columnLocations(location.column);
            shiftLocations.reverse();
        } else if (location.column === this.n - 1) {
            shiftLocations = this._rowLocations(location.row);
            shiftLocations.reverse();
        } else if (location.column === 0) {
            shiftLocations = this._rowLocations(location.row);
        }
        if (shiftLocations.length === this.n) {
            this._shiftAlongLocations(shiftLocations);
        } else {
            throw new ValueError();
        }
    }

    getPlayer(playerId) {
        let player = this._players.get(playerId);
        if (!player) {
            throw new ValueError();
        }
        return player;
    }

    addPlayer(player) {
        this._players.set(player.id, player);
    }

    getComputerPlayers() {
        let result = [];
        for (var player of this._players.values()) {
            if (player.isComputer) {
                result.push(player);
            }
        }
        return result;
    }

    move(playerId, targetLocation) {
        var player = this.getPlayer(playerId);
        var targetMazeCard = this.getMazeCard(targetLocation);
        var sourceMazeCard = player.mazeCard;
        sourceMazeCard.removePlayer(player);
        targetMazeCard.addPlayer(player);
        player.mazeCard = targetMazeCard;
    }

    _columnLocations(column) {
        var locations = [];
        for (let row = 0; row < this.n; row++) {
            locations.push({ row: row, column: column });
        }
        return locations;
    }

    _rowLocations(row) {
        var locations = [];
        for (let column = 0; column < this.n; column++) {
            locations.push({ row: row, column: column });
        }
        return locations;
    }

    _shiftAlongLocations(locations) {
        var pushedCard = this.leftoverMazeCard;
        this.leftoverMazeCard = this.getMazeCard(locations[this.n - 1]);
        this.leftoverMazeCard.setLeftoverLocation();
        for (let i = this.n - 1; i > 0; i--) {
            this.setMazeCard(locations[i], this.getMazeCard(locations[i - 1]));
            this.getMazeCard(locations[i]).setLocation(locations[i]);
        }
        this._transferPlayers(this.leftoverMazeCard, pushedCard);
        var first = locations[0];
        pushedCard.setLocation(first);
        Vue.set(this.mazeCards[first.row], first.column, pushedCard);
    }

    _transferPlayers(sourceMazeCard, targetMazeCard) {
        while (sourceMazeCard.players.length) {
            var player = sourceMazeCard.players.pop();
            player.mazeCard = targetMazeCard;
            targetMazeCard.addPlayer(player);
        }
    }

    createFromApi(apiState, userId = 0) {
        var apiMazeCards = apiState.mazeCards;
        this._sortApiMazeCards(apiMazeCards);
        if (this.leftoverMazeCard.id != apiMazeCards[0].id) {
            this.leftoverMazeCard = MazeCard.createFromApi(apiMazeCards[0]);
        }

        this._mazeCardsFromSortedApi(apiMazeCards);
        let remainingColors = [3, 2, 1, 0];
        let toRemove = new Set(this._players.keys());
        apiState.players.sort(function(p1, p2) {
            return p1.id - p2.id;
        });
        for (let index = 0; index < apiState.players.length; index++) {
            let apiPlayer = apiState.players[index];
            let playerCard = this.mazeCardById(apiPlayer.mazeCardId);
            let player = this._players.get(apiPlayer.id);
            if (!player) {
                player = new Player(apiPlayer.id, remainingColors.pop());
                if (userId === player.id) {
                    player.isUser = true;
                }
            } else {
                player.colorIndex = remainingColors.pop();
            }
            player.mazeCard = playerCard;
            if (apiPlayer.isComputerPlayer) {
                player.isComputer = true;
                player.algorithm = apiPlayer.algorithm;
            }
            player.turnAction = "NONE";
            playerCard.addPlayer(player);
            this.addPlayer(player);
            toRemove.delete(player.id);
        }

        for (let id of toRemove) {
            this._players.delete(id);
        }

        let objectiveCard = this.mazeCardById(apiState.objectiveMazeCardId);
        objectiveCard.hasObject = true;

        if (apiState.nextAction) {
            this.setNextAction(
                apiState.nextAction.playerId,
                apiState.nextAction.action
            );
        }
    }

    setNextAction(playerId, action) {
        this.nextAction.playerId = playerId;
        this.nextAction.action = action;
        this.getPlayer(playerId).turnAction = action;
    }

    _sortApiMazeCards(apiMazeCards) {
        apiMazeCards.forEach(card => {
            if (card.location === null) {
                card.location = {
                    row: -1,
                    column: -1
                };
            }
        });
        apiMazeCards.sort((card1, card2) =>
            this._compareApiLocations(card1.location, card2.location)
        );
    }

    _compareApiLocations(location1, location2) {
        if (location1.row == location2.row) {
            return location1.column - location2.column;
        }
        return location1.row - location2.row;
    }

    _mazeCardsFromSortedApi(sortedApiMazeCards) {
        this.mazeCards.splice(0, this.n);
        var index = 1;
        for (var row = 0; row < this.n; row++) {
            this.mazeCards.push([]);
            for (var col = 0; col < this.n; col++) {
                this.mazeCards[row].push(
                    MazeCard.createFromApi(sortedApiMazeCards[index])
                );
                index++;
            }
        }
    }

    _isInside(location) {
        return (
            location.row >= 0 &&
            location.row < this.n &&
            location.column >= 0 &&
            location.column < this.n
        );
    }
}
