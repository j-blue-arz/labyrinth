export const MOVE_ACTION = "MOVE";
export const SHIFT_ACTION = "SHIFT";
export const NO_ACTION = "NONE";

export default class Player {
    constructor(id) {
        this._id = id;
        this.mazeCard = null;
        this.colorIndex = 0;
        this.isBot = false;
        this.computationMethod = "";
        this.isUser = false;
        this._turnAction = NO_ACTION; // one of NONE, MOVE, or SHIFT
        this.score = 0;
        this.playerName = "";
    }

    get id() {
        return this._id;
    }

    hasToMove() {
        return this._turnAction === MOVE_ACTION;
    }

    hasToShift() {
        return this._turnAction === SHIFT_ACTION;
    }

    isHisTurn() {
        return this._turnAction !== NO_ACTION;
    }

    getTurnAction() {
        return this._turnAction;
    }

    setTurnAction(newTurnAction) {
        let previousTurnAction = this._turnAction;
        this._turnAction = newTurnAction;
        if (previousTurnAction !== newTurnAction) {
            if (newTurnAction === SHIFT_ACTION) {
                this.onHasToShift();
            } else if (newTurnAction === MOVE_ACTION) {
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
        if (apiPlayer.isBot) {
            this.isBot = true;
            this.computationMethod = apiPlayer.computationMethod;
        }
        this.playerName = apiPlayer.name || "";
    }

    getLabel() {
        if (this.isBot) {
            return Player.computationMethodLabel(this.computationMethod);
        } else if (this.playerName) {
            return this.playerName;
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
