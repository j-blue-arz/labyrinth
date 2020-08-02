import Vue from "vue";
import MazeCard from "@/model/mazeCard.js";
import Player from "@/model/player.js";
import Graph from "@/model/mazeAlgorithm.js";
import ValueError from "@/util/exceptions";

export const MOVE_ACTION = "MOVE";
export const SHIFT_ACTION = "SHIFT";
export const NO_ACTION = "NONE";

export function loc(row, column) {
    return { row: row, column: column };
}

export default class Game {
    constructor() {
        this.n = 7;
        this.mazeCards = [];
        this.leftoverMazeCard = {};
        this._players = [];
        this.nextAction = { playerId: 0, action: NO_ACTION };
        this.isLoading = false;
        this.isShifting = false;
        this.disabledShiftLocation = null;
    }

    hasStarted() {
        return !this.isLoading && this.nextAction.action !== NO_ACTION;
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
        if (this.isInside(location)) {
            return this.mazeCards[location.row][location.column];
        } else {
            throw new RangeError();
        }
    }

    setMazeCard(location, mazeCard) {
        if (this.isInside(location)) {
            this.mazeCards[location.row][location.column] = mazeCard;
        } else {
            throw new RangeError();
        }
    }

    shift(location) {
        if (this._locationsEqual(location, this.disabledShiftLocation)) {
            throw new ValueError("Shifting at " + location + " is not allowed.");
        }

        if (!this.isInside(location)) {
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
            this.disabledShiftLocation = this.getOppositeLocation(location);
        } else {
            throw new ValueError();
        }
    }

    getOppositeLocation(borderLocation) {
        let oppositeLocation = null;
        if (borderLocation.row === 0) {
            oppositeLocation = { row: this.n - 1, column: borderLocation.column };
        } else if (borderLocation.row === this.n - 1) {
            oppositeLocation = { row: 0, column: borderLocation.column };
        } else if (borderLocation.column === this.n - 1) {
            oppositeLocation = { row: borderLocation.row, column: 0 };
        } else if (borderLocation.column === 0) {
            oppositeLocation = { row: borderLocation.row, column: this.n - 1 };
        }
        return oppositeLocation;
    }

    _locationsEqual(locA, locB) {
        return locA && locB && locA.row === locB.row && locA.column === locB.column;
    }

    hasPlayer(playerId) {
        for (let player of this._players) {
            if (player.id === playerId) {
                return true;
            }
        }
        return false;
    }

    getPlayer(playerId) {
        for (let player of this._players) {
            if (player.id === playerId) {
                return player;
            }
        }
        throw new ValueError("No player with id " + playerId);
    }

    addPlayer(player) {
        if (!this.hasPlayer(player.id)) {
            this._players.push(player);
        }
    }

    getComputerPlayers() {
        let result = [];
        for (var player of this._players) {
            if (player.isComputer) {
                result.push(player);
            }
        }
        return result;
    }

    getPlayers() {
        return this._players;
    }

    deletePlayerById(playerId) {
        let position = -1;
        for (var index = 0; index < this._players.length; index++) {
            if (this._players[index].id === playerId) {
                position = index;
            }
        }
        if (position >= 0) {
            this._players.splice(position, 1);
        }
    }

    move(playerId, targetLocation) {
        var player = this.getPlayer(playerId);
        var targetMazeCard = this.getMazeCard(targetLocation);
        var sourceMazeCard = player.mazeCard;
        sourceMazeCard.removePlayer(player);
        targetMazeCard.addPlayer(player);
        player.mazeCard = targetMazeCard;
    }

    isMoveValid(playerId, targetLocation) {
        if (this.nextAction.playerId !== playerId) {
            return false;
        }
        if (this.nextAction.action !== MOVE_ACTION) {
            return false;
        }
        let player = this.getPlayer(playerId);
        let sourceLocation = player.mazeCard.location;
        return new Graph(this).isReachable(sourceLocation, targetLocation);
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
        this.isShifting = true;
        var pushedCard = this.leftoverMazeCard;
        this.leftoverMazeCard = this.getMazeCard(locations[this.n - 1]);
        this.leftoverMazeCard.setLeftoverLocation();
        for (let i = this.n - 1; i > 0; i--) {
            this.setMazeCard(locations[i], this.getMazeCard(locations[i - 1]));
            this.getMazeCard(locations[i]).setLocation(locations[i]);
        }
        var first = locations[0];
        pushedCard.setLocation(first);
        Vue.set(this.mazeCards[first.row], first.column, pushedCard);
        this.isShifting = false;
        this._transferPlayers(this.leftoverMazeCard, pushedCard);
    }

    _transferPlayers(sourceMazeCard, targetMazeCard) {
        while (sourceMazeCard.players.length) {
            var player = sourceMazeCard.players.pop();
            player.mazeCard = targetMazeCard;
            targetMazeCard.addPlayer(player);
        }
    }

    createFromApi(apiState) {
        this.isLoading = true;
        var maze = apiState.maze;
        var apiMazeCards = maze.mazeCards;
        this._sortApiMazeCards(apiMazeCards);
        if (this.leftoverMazeCard.id != apiMazeCards[0].id) {
            this.leftoverMazeCard = MazeCard.createFromApi(apiMazeCards[0]);
        }

        this.n = maze.mazeSize;
        this._mazeCardsFromSortedApi(apiMazeCards);
        this._playersFromApi(apiState);

        let objectiveCard = this.mazeCardById(apiState.objectiveMazeCardId);
        objectiveCard.hasObject = true;
        this.setNextAction(apiState.nextAction);

        this.disabledShiftLocation = this._findMissingShiftLocation(apiState.enabledShiftLocations);

        this.isLoading = false;
    }

    _playersFromApi(apiState) {
        let toRemove = new Set(this._players.map(player => player.id));
        apiState.players.sort(function(p1, p2) {
            return p1.id - p2.id;
        });
        for (let index = 0; index < apiState.players.length; index++) {
            let apiPlayer = apiState.players[index];
            let playerCard = this.mazeCardById(apiPlayer.mazeCardId);
            let player;
            if (this.hasPlayer(apiPlayer.id)) {
                player = this.getPlayer(apiPlayer.id);
                player.fillFromApi(apiPlayer);
            } else {
                player = Player.newFromApi(apiPlayer);
            }
            player.mazeCard = playerCard;
            playerCard.addPlayer(player);
            toRemove.delete(player.id);
            if (!this.hasPlayer(player.id)) {
                this.addPlayer(player);
            }
        }
        for (let id of toRemove) {
            this.deletePlayerById(id);
        }
    }

    _findMissingShiftLocation(apiShiftLocations) {
        let enabledShiftLocations = new Set();
        for (let location of apiShiftLocations) {
            enabledShiftLocations.add(this._key(location));
        }
        let allShiftLocations = [];
        for (let position = 1; position < this.n - 1; position += 2) {
            allShiftLocations.push({ row: 0, column: position });
            allShiftLocations.push({ row: position, column: 0 });
            allShiftLocations.push({ row: this.n - 1, column: position });
            allShiftLocations.push({ row: position, column: this.n - 1 });
        }
        for (let location of allShiftLocations) {
            if (!enabledShiftLocations.has(this._key(location))) {
                return location;
            }
        }
        return null;
    }

    _key(location) {
        return location.row * this.n + location.column;
    }

    setNextAction(nextAction) {
        for (let player of this._players) {
            if (nextAction && player.id === nextAction.playerId) {
                player.turnAction = nextAction.action;
            } else {
                player.turnAction = NO_ACTION;
            }
        }

        if (nextAction !== null) {
            this.nextAction = nextAction;
        } else {
            this.nextAction = { playerId: 0, action: NO_ACTION };
        }
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
        this.mazeCards.splice(0, this.mazeCards.length);
        var index = 1;
        for (var row = 0; row < this.n; row++) {
            this.mazeCards.push([]);
            for (var col = 0; col < this.n; col++) {
                this.mazeCards[row].push(MazeCard.createFromApi(sortedApiMazeCards[index]));
                index++;
            }
        }
    }

    isInside(location) {
        return (
            location.row >= 0 &&
            location.row < this.n &&
            location.column >= 0 &&
            location.column < this.n
        );
    }
}
