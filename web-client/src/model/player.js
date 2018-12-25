export default class Player {
    constructor(id, colorIndex) {
        this.id = id;
        this.mazeCard = null;
        this.colorIndex = colorIndex;
        this.isComputer = false;
        this.algorithm = "";
        this.isUser = false;
        this.turnAction = "NONE"; // one of NONE, MOVE, or SHIFT
    }

    hasToMove() {
        return this.turnAction == "MOVE";
    }

    hasToShift() {
        return this.turnAction == "SHIFT";
    }

    static withId(id) {
        return new this(id, null);
    }

    static compareById(player1, player2) {
        return player1.id - player2.id;
    }
}
