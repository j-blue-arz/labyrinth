import WasmGateway from "@/api/wasmGateway.js";

export default class WasmPlayer {
    constructor(playerId, game, emitShiftEvent, emitMoveEvent) {
        this.playerId = playerId;
        this.game = game;
        this.wasmGateway = new WasmGateway();
        this.emitShiftEvent = emitShiftEvent;
        this.emitMoveEvent = emitMoveEvent;
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
            this.emitMoveEvent(this.computedAction.moveLocation);
            this.computedAction = null;
        }
    }

    _performShift() {
        this.computedAction = this.wasmGateway.computeActions(this.game, this.playerId);
        this.emitShiftEvent(this.computedAction.shiftAction);
    }
}
