import WasmGateway from "@/api/wasmGateway.js";
import Player from "@/model/player.js";

export default class WasmPlayer extends Player {
    constructor(id, game, performShift, performMove) {
        super(id);
        this.game = game;
        this.wasmGateway = new WasmGateway();
        this.performShift = performShift;
        this.performMove = performMove;
    }

    fillFromPlayer(player) {
        this.mazeCard = player.mazeCard;
        this.colorIndex = player.colorIndex;
        this._turnAction = player._turnAction;
        this.score = player.score;
    }

    onHasToShift() {
        if (!this.wasmGateway.hasLibexhsearch()) {
            this.wasmGateway.loadLibexhsearch(() => this._performShift());
        } else {
            this._performShift();
        }
    }

    onHasToMove() {
        if (this.computedAction) {
            let moveAction = {
                playerId: this.id,
                targetLocation: this.computedAction.moveLocation
            };
            this.performMove(moveAction);
            this.computedAction = null;
        }
    }

    _performShift() {
        this.computedAction = this.wasmGateway.computeActions(this.game, this.id);
        let shiftAction = {
            playerId: this.id,
            location: this.computedAction.shiftAction.location,
            leftoverRotation: this.computedAction.shiftAction.leftoverRotation
        };
        this.performShift(shiftAction);
    }

    getLabel() {
        return "WASM: Exhaustive Search";
    }
}
