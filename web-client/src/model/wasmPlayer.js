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

    onHasToShift() {
        if (!this.wasmGateway.libexhsearch) {
            this.wasmGateway.loadLibexhsearch(this._performShift);
        } else {
            this._performShift();
        }
    }

    onHasToMove() {
        if (this.computedAction) {
            let moveEvent = {
                playerId: this.playerId,
                targetLocation: this.computedAction.moveLocation
            };
            this.performMove(moveEvent);
            this.computedAction = null;
        }
    }

    _performShift() {
        this.computedAction = this.wasmGateway.computeActions(this.game, this.playerId);
        let shiftEvent = {
            playerId: this.playerId,
            location: this.computedAction.shiftAction.location,
            leftoverRotation: this.computedAction.shiftAction.leftoverRotation
        };
        this.performShift(shiftEvent);
    }
}
