export default class MazeCard {
    constructor(id, row, column, doors, rotation) {
        this.id = id;
        this.location = { row: row, column: column };
        this.doors = doors;
        this._rotation = rotation;
        this.playerPieces = [];

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

    static createNewRandom(id, row, column) {
        return new this(id, row, column, this.generateRandomDoors(), 0);
    }

    static generateRandomDoors() {
        return MazeCard.validCombinations[
            Math.floor(Math.random() * MazeCard.validCombinations.length)
        ];
    }

    static rotationEquivalentDoor(originalDoor, rotation) {
        return MazeCard.doorsRotation[
            (MazeCard.doorsRotation.indexOf(originalDoor) + rotation / 90 + 4) %
                4
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
        var rotationDoor = MazeCard.rotationEquivalentDoor(
            door,
            -this._rotation
        );
        return this.doors.indexOf(rotationDoor) != -1;
    }

    get rotation() {
        return this._rotation;
    }

    rotateClockwise() {
        this._rotation = (this._rotation + 90) % 360;
    }

    setLocation(row, column) {
        this.location.row = row;
        this.location.column = column;
    }

    setLeftoverLocation() {
        this.setLocation(-1, -1);
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
