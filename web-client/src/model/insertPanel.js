export default class InsertPanel {
    constructor(id, shiftLocation, mazeSize = 7) {
        this.id = id;
        this.shiftLocation = shiftLocation;
        this.enabled = true;
        this.displayLocation = null;
        this.direction = null;
        let limit = mazeSize - 1;
        let row = shiftLocation.row;
        let column = shiftLocation.column;
        if (this.shiftLocation.row === 0) {
            this.direction = "S";
            this.displayLocation = { row: -1, column: column };
        } else if (this.shiftLocation.row === limit) {
            this.direction = "N";
            this.displayLocation = { row: mazeSize, column: column };
        } else if (this.shiftLocation.column === 0) {
            this.direction = "E";
            this.displayLocation = { row: row, column: -1 };
        } else if (this.shiftLocation.column === limit) {
            this.direction = "W";
            this.displayLocation = { row: row, column: mazeSize };
        }
    }
}
