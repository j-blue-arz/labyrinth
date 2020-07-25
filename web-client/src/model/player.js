export default class Player {
    constructor(id, colorIndex) {
        this.id = id;
        this.mazeCard = null;
        this.colorIndex = colorIndex;
        this.isComputer = false;
        this.type = "";
        this.isUser = false;
        this.turnAction = "NONE"; // one of NONE, MOVE, or SHIFT
        this.score = 0;
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

    static newFromApi(apiPlayer) {
        let player = new this(apiPlayer.id);
        player.fillFromApi(apiPlayer);
        return player;
    }

    fillFromApi(apiPlayer) {
        this.score = apiPlayer.score;
        this.colorIndex = apiPlayer.pieceIndex;
        if (apiPlayer.isComputerPlayer) {
            this.isComputer = true;
            this.type = apiPlayer.algorithm;
            this.isUser = false;
        }
    }

    computationMethodLabel() {
        if (this.type === "exhaustive-search") {
            return "Exhaustive Search";
        } else if (this.type === "alpha-beta") {
            return "Alpha-Beta";
        } else if (this.type === "minimax") {
            return "Minimax";
        } else {
            return this.type;
        }
    }
}
