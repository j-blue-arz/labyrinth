import Player from "@/model/player.js";

export default class MazeCard {
    constructor(id, row, column, doors, rotation) {
        this.id = id;
        this.location = { row: row, column: column };
        this.doors = doors;
        this._rotation = rotation;
        this._players = [];
        this.hasObject = false;

        if (!Number.isInteger(id))
            throw new Error(
                "Invalid constructor argument for id, should be integer."
            );
        if (!Number.isInteger(row))
            throw new Error(
                "Invalid constructor argument for row, should be integer."
            );
        if (!Number.isInteger(column))
            throw new Error(
                "Invalid constructor argument for column, should be integer."
            );
        if (!Number.isInteger(rotation / 90))
            throw new Error(
                "Invalid constructor argument for rotation, should be integer divisible by 90."
            );
        if (typeof doors !== "string")
            throw new Error(
                "Invalid constructor argument for doors, should be string."
            );
        if (!/^[NESW]{2,4}$/.test(doors))
            throw new Error(
                "Invalid constructor argument for doors, should comply pattern '[NESW]{2,4}'."
            );
        if (
            Number(this.hasNorthDoor()) +
                Number(this.hasEastDoor()) +
                Number(this.hasWestDoor()) +
                Number(this.hasSouthDoor()) !==
            doors.length
        )
            throw new Error(
                "Invalid constructor argument for doors, should not include same door twice."
            );
    }

    static createFromApi(apiMazeCard) {
        return new this(
            apiMazeCard.id,
            apiMazeCard.location.row,
            apiMazeCard.location.column,
            apiMazeCard.doors,
            apiMazeCard.rotation
        );
    }

    static createNewRandom(id, row, column) {
        return new this(id, row, column, this.generateRandomDoors(), 0);
    }

    static generateRandomDoors() {
        return MazeCard.validCombinations[
            Math.floor(Math.random() * MazeCard.validCombinations.length)
        ];
    }

    hasNorthDoor() {
        return this._hasDoor("N");
    }

    hasEastDoor() {
        return this._hasDoor("E");
    }

    hasSouthDoor() {
        return this._hasDoor("S");
    }

    hasWestDoor() {
        return this._hasDoor("W");
    }

    _hasDoor(door) {
        return this.doors.indexOf(door) != -1;
    }

    hasRotationEquivalentDoor(door) {
        var rotationDoor = MazeCard.rotationEquivalentDoor(
            door,
            -this._rotation
        );
        return this.doors.indexOf(rotationDoor) != -1;
    }

    static rotationEquivalentDoor(originalDoor, rotation) {
        return MazeCard.doorsRotation[
            (MazeCard.doorsRotation.indexOf(originalDoor) + rotation / 90 + 4) %
                4
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
        this._players.sort(Player.compareById);
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

MazeCard.doorsRotation = ["N", "E", "S", "W"];
