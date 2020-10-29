export default class Player {
    constructor(id) {
        this.id = id;
        this.mazeCard = null;
        this.colorIndex = 0;
        this.isComputer = false;
        this.computationMethod = "";
        this.isUser = false;
        this._turnAction = "NONE"; // one of NONE, MOVE, or SHIFT
        this.score = 0;
    }

    hasToMove() {
        return this._turnAction == "MOVE";
    }

    hasToShift() {
        return this._turnAction == "SHIFT";
    }

    getTurnAction() {
        return this._turnAction;
    }

    setTurnAction(newTurnAction) {
        let previousTurnAction = this._turnAction;
        this._turnAction = newTurnAction;
        if (previousTurnAction !== newTurnAction) {
            if (newTurnAction === "SHIFT") {
                this.onHasToShift();
            } else if (newTurnAction === "MOVE") {
                this.onHasToMove();
            }
        }
    }

    static withId(id) {
        return new this(id, null);
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
        if (computationMethod === "libexhsearch") {
            return "Exhaustive Search (1P)";
        } else if (computationMethod === "libminimax") {
            return "Minimax (2P)";
        } else if (computationMethod.startsWith("libminimax-")) {
            let suffix = computationMethod.replace("libminimax-", "");
            if (suffix === "distance") {
                return "Minimax (2P) - Distance Heuristic";
            } else if (suffix === "reachable") {
                return "Minimax (2P) - Reachable Heuristic";
            } else {
                return "Minimax (2P) - heuristic: " + suffix;
            }
        } else {
            return computationMethod;
        }
    }

    onHasToShift() {}

    onHasToMove() {}
}
