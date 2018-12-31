export default class Graph {
    constructor(game) {
        this.game = game;
    }

    isReachable(sourceLocation, targetLocation) {
        let locations = this.reachableLocations(sourceLocation);
        for (var location of locations) {
            if (this._locationsEqual(location, targetLocation)) {
                return true;
            }
        }
        return false;
    }

    _locationsEqual(locationA, locationB) {
        return locationA.row === locationB.row && locationA.column == locationB.column;
    }

    reachableLocations(sourceLocation) {
        let reachedLocations = this._initReached();
        this._setReached(sourceLocation, reachedLocations);
        let nextElements = [sourceLocation];
        var currentLocation;
        while ((currentLocation = nextElements.shift()) !== undefined) {
            this._neighbors(currentLocation).forEach(neighbor => {
                if (!this._hasReached(neighbor, reachedLocations)) {
                    this._setReached(neighbor, reachedLocations);
                    nextElements.push(neighbor);
                }
            });
        }
        return this._reachedToArray(reachedLocations);
    }

    _neighbors(location) {
        let neighbors = [];
        let mazeCard = this.game.getMazeCard(location);
        let outPaths = this._outPaths(mazeCard);
        for (var outPath of outPaths) {
            let locationToTest = {
                row: location.row + outPath[0],
                column: location.column + outPath[1]
            };
            if (this.game.isInside(locationToTest)) {
                let cardToTest = this.game.getMazeCard(locationToTest);
                let mirroredDoor = this._mirror(outPath[2]);
                if (cardToTest.hasRotationEquivalentDoor(mirroredDoor)) {
                    neighbors.push(locationToTest);
                }
            }
        }
        return neighbors;
    }

    _outPaths(mazeCard) {
        let result = [];
        if (mazeCard.hasRotationEquivalentDoor("N")) {
            result.push([-1, 0, "N"]);
        }
        if (mazeCard.hasRotationEquivalentDoor("E")) {
            result.push([0, 1, "E"]);
        }
        if (mazeCard.hasRotationEquivalentDoor("S")) {
            result.push([1, 0, "S"]);
        }
        if (mazeCard.hasRotationEquivalentDoor("W")) {
            result.push([0, -1, "W"]);
        }
        return result;
    }

    _mirror(door) {
        let doors = ["N", "E", "S", "W"];
        let mirroredIndex = (doors.indexOf(door) + 2) % 4;
        return doors[mirroredIndex];
    }

    _initReached() {
        let reached = [];
        for (var row = 0; row < this.game.n; row++) {
            reached.push([]);
            for (var col = 0; col < this.game.n; col++) {
                reached[row].push(false);
            }
        }
        return reached;
    }

    _hasReached(location, reachedLocations) {
        return reachedLocations[location.row][location.column];
    }

    _setReached(location, reachedLocations) {
        reachedLocations[location.row][location.column] = true;
    }

    _reachedToArray(reachedLocations) {
        let reached = [];
        for (var row = 0; row < this.game.n; row++) {
            for (var col = 0; col < this.game.n; col++) {
                if (reachedLocations[row][col]) {
                    reached.push({
                        row: row,
                        column: col
                    });
                }
            }
        }
        return reached;
    }
}
