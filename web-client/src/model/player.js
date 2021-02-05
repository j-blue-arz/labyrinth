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
    }

    getLabel() {
        if (this.isUser) {
            return "You";
        } else if (this.isBot) {
            return Player.computationMethodLabel(this.computationMethod);
        }
        return "";
    }

    static computationMethodLabel(computationMethod) {
        if (computationMethod === "libexhsearch") {
            return "Exhaustive Search\u00A0(1P)";
        } else if (computationMethod === "libminimax") {
            return "Minimax\u00A0(2P)";
        } else if (computationMethod.startsWith("libminimax-")) {
            let suffix = computationMethod.replace("libminimax-", "");
            if (suffix === "distance") {
                return "Minimax\u00A0(2P) - Distance\u00A0Heuristic";
            } else if (suffix === "reachable") {
                return "Minimax\u00A0(2P) - Reachable\u00A0Heuristic";
            } else {
                return "Minimax\u00A0(2P) - heuristic: " + suffix;
            }
        } else {
            return computationMethod;
        }
    }

    onHasToShift() {}

    onHasToMove() {}
}
