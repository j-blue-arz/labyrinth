function inside(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function panelToInsertLocation(location, mazeSize) {
    return {
        row: inside(location.row, 0, mazeSize - 1),
        column: inside(location.column, 0, mazeSize - 1)
    };
}

export default class InsertPanel {
    constructor(id, row, column, mazeSize = 7) {
        this.id = id;
        this.displayLocation = { row: row, column: column };
        this.insertLocation = panelToInsertLocation(this.displayLocation, mazeSize);
        this.enabled = true;
    }
}
