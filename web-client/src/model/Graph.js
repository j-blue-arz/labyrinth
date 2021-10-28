import { locationsEqual, mazeCardAtLocation, isInside } from "@/store/modules/board.js";

const outPathsRotation = ["N", "E", "S", "W"];

export default class Graph {
    constructor(board) {
        this.board = board;
        this._reachedLocations = [];
        for (var row = 0; row < this.board.mazeSize; row++) {
            this._reachedLocations.push([]);
            for (var col = 0; col < this.board.mazeSize; col++) {
                this._reachedLocations[row].push(false);
            }
        }
    }

    path(sourceLocation, targetLocation) {
        this._setReached(sourceLocation, { parent: sourceLocation });
        let nextElements = [sourceLocation];
        var currentLocation;
        while ((currentLocation = nextElements.shift()) !== undefined) {
            if (locationsEqual(currentLocation, targetLocation)) {
                return this._reachedToPath(currentLocation);
            }
            this._neighborLocations(currentLocation).forEach(neighbor => {
                if (!this._getReached(neighbor)) {
                    this._setReached(neighbor, { parent: currentLocation });
                    nextElements.push(neighbor);
                }
            });
        }
        return [];
    }

    isReachable(sourceLocation, targetLocation) {
        let locations = this.reachableLocations(sourceLocation);
        for (var location of locations) {
            if (locationsEqual(location, targetLocation)) {
                return true;
            }
        }
        return false;
    }

    reachableLocations(sourceLocation) {
        this._setReached(sourceLocation, true);
        let nextElements = [sourceLocation];
        let currentLocation;
        while ((currentLocation = nextElements.shift()) !== undefined) {
            this._neighborLocations(currentLocation).forEach(neighbor => {
                if (!this._getReached(neighbor)) {
                    this._setReached(neighbor, true);
                    nextElements.push(neighbor);
                }
            });
        }
        return this._reachedToArray();
    }

    _neighborLocations(location) {
        let neighbors = [];
        let mazeCard = mazeCardAtLocation(this.board, location);
        let outPaths = this._outPaths(mazeCard);
        for (var outPath of outPaths) {
            let locationToTest = {
                row: location.row + outPath[0],
                column: location.column + outPath[1]
            };
            if (isInside(locationToTest, this.board.mazeSize)) {
                let cardToTest = mazeCardAtLocation(this.board, locationToTest);
                let mirroredOutPath = this._mirror(outPath[2]);
                if (this._hasRotationAwareOutPath(cardToTest, mirroredOutPath)) {
                    neighbors.push(locationToTest);
                }
            }
        }
        return neighbors;
    }

    _outPaths(mazeCard) {
        let result = [];
        if (this._hasRotationAwareOutPath(mazeCard, "N")) {
            result.push([-1, 0, "N"]);
        }
        if (this._hasRotationAwareOutPath(mazeCard, "E")) {
            result.push([0, 1, "E"]);
        }
        if (this._hasRotationAwareOutPath(mazeCard, "S")) {
            result.push([1, 0, "S"]);
        }
        if (this._hasRotationAwareOutPath(mazeCard, "W")) {
            result.push([0, -1, "W"]);
        }
        return result;
    }

    _mirror(outPath) {
        let outPaths = ["N", "E", "S", "W"];
        let mirroredIndex = (outPaths.indexOf(outPath) + 2) % 4;
        return outPaths[mirroredIndex];
    }

    _initReached() {
        let reached = [];
        for (var row = 0; row < this.board.mazeSize; row++) {
            reached.push([]);
            for (var col = 0; col < this.board.mazeSize; col++) {
                reached[row].push(false);
            }
        }
        return reached;
    }

    _getReached(location) {
        return this._reachedLocations[location.row][location.column];
    }

    _setReached(location, value) {
        this._reachedLocations[location.row][location.column] = value;
    }

    _reachedToArray() {
        let reached = [];
        for (var row = 0; row < this.board.mazeSize; row++) {
            for (var col = 0; col < this.board.mazeSize; col++) {
                if (this._reachedLocations[row][col]) {
                    reached.push({
                        row: row,
                        column: col
                    });
                }
            }
        }
        return reached;
    }

    _reachedToPath(location) {
        let path = [location];
        let current = location;
        while (!locationsEqual(this._getReached(current).parent, current)) {
            current = this._getReached(current).parent;
            path.push(current);
        }
        return path.reverse();
    }

    _hasRotationAwareOutPath(mazeCard, outPath) {
        const unrotatedOutPath = this._rotatedOutPath(outPath, -mazeCard.rotation);
        return mazeCard.outPaths.indexOf(unrotatedOutPath) != -1;
    }

    _rotatedOutPath(originalOutPath, rotation) {
        return outPathsRotation[
            (outPathsRotation.indexOf(originalOutPath) + rotation / 90 + 4) % 4
        ];
    }
}
