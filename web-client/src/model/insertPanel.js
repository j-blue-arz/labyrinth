function inside(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function panelToShiftLocation(location, mazeSize) {
    return {
        row: inside(location.row, 0, mazeSize - 1),
        column: inside(location.column, 0, mazeSize - 1)
    };
}

function panelToDirection(location, mazeSize) {
    let limit = mazeSize - 1;
    if (location.row === 0) {
        return "S";
    } else if (location.row === limit) {
        return "N";
    } else if (location.column === 0) {
        return "E";
    } else if (location.column === limit) {
        return "W";
    }
    return "";
}

export default class InsertPanel {
    constructor(id, row, column, mazeSize = 7) {
        this.id = id;
        this.displayLocation = { row: row, column: column };
        this.shiftLocation = panelToShiftLocation(this.displayLocation, mazeSize);
        this.enabled = true;
        this.direction = panelToDirection(this.shiftLocation, mazeSize);
    }
}
