import { loc } from "@/stores/board.js";

function shiftLocationDirection(shiftLocation, limit) {
    if (shiftLocation.row === 0) {
        return "S";
    } else if (shiftLocation.row === limit) {
        return "N";
    } else if (shiftLocation.column === 0) {
        return "E";
    } else if (shiftLocation.column === limit) {
        return "W";
    }
}

export class ShiftLocation {
    constructor(location, mazeSize = 7) {
        this._shiftLocation = location;
        this._direction = shiftLocationDirection(location, mazeSize - 1);
    }

    isHorizontal() {
        return this._direction === "E" || this._direction === "W";
    }

    isVertical() {
        return this._direction === "N" || this._direction === "S";
    }

    affects(location) {
        if (this.isHorizontal()) {
            return location.row === this._shiftLocation.row;
        }
        if (this.isVertical()) {
            return location.column === this._shiftLocation.column;
        }
    }

    affectedLocations(mazeSize) {
        if (this.isHorizontal()) {
            const row = this._shiftLocation.row;
            return Array.from({ length: mazeSize }, (_, index) => loc(row, index));
        }
        if (this.isVertical()) {
            const column = this._shiftLocation.column;
            return Array.from({ length: mazeSize }, (_, index) => loc(index, column));
        }
    }

    get shiftLocation() {
        return this._shiftLocation;
    }

    get direction() {
        return this._direction;
    }

    get row() {
        return this._shiftLocation.row;
    }

    get column() {
        return this._shiftLocation.column;
    }
}

export class InsertPanel extends ShiftLocation {
    constructor(id, shiftLocation, mazeSize = 7) {
        super(shiftLocation, mazeSize);
        this.id = id;
        this.enabled = true;
        this.displayLocation = null;
        let row = shiftLocation.row;
        let column = shiftLocation.column;
        let limit = mazeSize - 1;
        if (this._shiftLocation.row === 0) {
            this.displayLocation = { row: -1, column: column };
        } else if (this._shiftLocation.row === limit) {
            this.displayLocation = { row: mazeSize, column: column };
        } else if (this._shiftLocation.column === 0) {
            this.displayLocation = { row: row, column: -1 };
        } else if (this._shiftLocation.column === limit) {
            this.displayLocation = { row: row, column: mazeSize };
        }
    }
}
