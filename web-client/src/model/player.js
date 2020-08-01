export default class Player {
    constructor(id, colorIndex) {
        this.id = id;
        this.mazeCard = null;
        this.colorIndex = colorIndex;
        this.isComputer = false;
        this.computationMethod = "";
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
            this.computationMethod = apiPlayer.computationMethod;
        }
    }

    getLabel() {
        if (this.isUser) {
            return "You";
        } else if (this.isComputer) {
            return Player.computationMethodLabel(this.computationMethod);
        }
        return "";
    }

    static computationMethodLabel(computationMethod) {
        if (computationMethod === "exhaustive-search") {
            return "Exhaustive Search";
        } else if (computationMethod === "alpha-beta") {
            return "Alpha-Beta";
        } else if (computationMethod === "minimax") {
            return "Minimax";
        } else if (computationMethod === "random") {
            return "Random actions";
        } else if (computationMethod.startsWith("dynamic-")) {
            return computationMethod.replace("dynamic-", "Library: ");
        } else {
            return computationMethod;
        }
    }
}
