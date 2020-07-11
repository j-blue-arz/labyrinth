export default class MazeCard {
    constructor(id, row, column, out_paths, rotation) {
        this.id = id;
        this.location = { row: row, column: column };
        this.out_paths = out_paths;
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
        if (typeof out_paths !== "string")
            throw new Error("Invalid constructor argument for out_paths, should be string.");
        if (!/^[NESW]{2,4}$/.test(out_paths))
            throw new Error(
                "Invalid constructor argument for out_paths, should comply pattern '[NESW]{2,4}'."
            );
        if (
            Number(this.hasNorthOutPath()) +
                Number(this.hasEastOutPath()) +
                Number(this.hasWestOutPath()) +
                Number(this.hasSouthOutPath()) !==
            out_paths.length
        )
            throw new Error(
                "Invalid constructor argument for out_paths, should not include same out_path twice."
            );
    }

    static createFromApi(apiMazeCard) {
        return new this(
            apiMazeCard.id,
            apiMazeCard.location.row,
            apiMazeCard.location.column,
            apiMazeCard.out_paths,
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

    _hasOutPath(out_path) {
        return this.out_paths.indexOf(out_path) != -1;
    }

    hasRotationAwareOutPath(outPath) {
        var unrotatedOutPath = MazeCard.rotatedOutPath(outPath, -this._rotation);
        return this.out_paths.indexOf(unrotatedOutPath) != -1;
    }

    static rotatedOutPath(originalOutPath, rotation) {
        return MazeCard.out_pathsRotation[
            (MazeCard.out_pathsRotation.indexOf(originalOutPath) + rotation / 90 + 4) % 4
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

MazeCard.out_pathsRotation = ["N", "E", "S", "W"];
