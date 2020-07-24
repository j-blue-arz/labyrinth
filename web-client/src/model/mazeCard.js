export default class MazeCard {
    constructor(id, row, column, outPaths, rotation) {
        this.id = id;
        this.location = { row: row, column: column };
        this.outPaths = outPaths;
        this._rotation = rotation;
        this._players = [];
        this.hasObject = false;

        if (!Number.isInteger(id))
            throw new Error("Invalid constructor argument for id, should be integer.");
        if (!Number.isInteger(row))
            throw new Error("Invalid constructor argument for row, should be integer.");
        if (!Number.isInteger(column))
            throw new Error("Invalid constructor argument for column, should be integer.");
        if (!Number.isInteger(rotation / 90))
            throw new Error(
                "Invalid constructor argument for rotation, should be integer divisible by 90."
            );
        if (typeof outPaths !== "string")
            throw new Error("Invalid constructor argument for outPaths, should be string.");
        if (!/^[NESW]{2,4}$/.test(outPaths))
            throw new Error(
                "Invalid constructor argument for outPaths, should comply pattern '[NESW]{2,4}'."
            );
        if (
            Number(this.hasNorthOutPath()) +
                Number(this.hasEastOutPath()) +
                Number(this.hasWestOutPath()) +
                Number(this.hasSouthOutPath()) !==
            outPaths.length
        )
            throw new Error(
                "Invalid constructor argument for outPaths, should not include same outPath twice."
            );
    }

    static createFromApi(apiMazeCard) {
        return new this(
            apiMazeCard.id,
            apiMazeCard.location.row,
            apiMazeCard.location.column,
            apiMazeCard.outPaths,
            apiMazeCard.rotation
        );
    }

    static createNewRandom(id, row, column) {
        return new this(id, row, column, this.generateRandomOutPaths(), 0);
    }

    static generateRandomOutPaths() {
        return MazeCard.validCombinations[
            Math.floor(Math.random() * MazeCard.validCombinations.length)
        ];
    }

    hasNorthOutPath() {
        return this._hasOutPath("N");
    }

    hasEastOutPath() {
        return this._hasOutPath("E");
    }

    hasSouthOutPath() {
        return this._hasOutPath("S");
    }

    hasWestOutPath() {
        return this._hasOutPath("W");
    }

    _hasOutPath(outPath) {
        return this.outPaths.indexOf(outPath) != -1;
    }

    hasRotationAwareOutPath(outPath) {
        var unrotatedOutPath = MazeCard.rotatedOutPath(outPath, -this._rotation);
        return this.outPaths.indexOf(unrotatedOutPath) != -1;
    }

    static rotatedOutPath(originalOutPath, rotation) {
        return MazeCard.outPathsRotation[
            (MazeCard.outPathsRotation.indexOf(originalOutPath) + rotation / 90 + 4) % 4
        ];
    }

    get rotation() {
        return this._rotation;
    }

    set rotation(value) {
        this._rotation = value;
    }

    get players() {
        return this._players;
    }

    addPlayer(player) {
        this._players.push(player);
        this._players.sort(function(p1, p2) {
            return p1.id - p2.id;
        });
    }

    removePlayer(player) {
        var index = this._players.indexOf(player);
        if (index >= 0) {
            this._players.splice(index, 1);
        }
    }

    rotateClockwise() {
        this._rotation = (this._rotation + 90) % 360;
    }

    setLocation(location) {
        this.location.row = location.row;
        this.location.column = location.column;
    }

    setLeftoverLocation() {
        this.location.row = -1;
        this.location.column = -1;
    }

    isLeftoverLocation() {
        return this.location.row === -1 || this.location.column === -1;
    }
}

MazeCard.validCombinations = [
    "NESW",
    "NES",
    "NEW",
    "NSW",
    "ESW",
    "NE",
    "NS",
    "NW",
    "ES",
    "EW",
    "SW"
];

MazeCard.outPathsRotation = ["N", "E", "S", "W"];
