import WasmGateway from "@/services/wasmGateway.js";
import { NO_ACTION, MOVE_ACTION, SHIFT_ACTION } from "@/model/player";
import { getShiftLocations } from "@/store/modules/board.js";

export default class WasmPlayer {
    constructor(store) {
        this.store = store;
        this.wasmGateway = new WasmGateway();
        this.computedAction = undefined;

        this.store.watch(
            () => {
                return this.store.getters["players/wasmPlayer"]?.nextAction ?? NO_ACTION;
            },
            newAction => {
                console.log(newAction);
                if (newAction === SHIFT_ACTION) {
                    this.onHasToShift();
                } else if (newAction === MOVE_ACTION) {
                    this.onHasToMove();
                } else if (newAction === NO_ACTION) {
                    this.computedAction = null;
                }
            }
        );
    }

    onHasToShift() {
        if (!this.wasmGateway.hasLibexhsearch()) {
            this.wasmGateway.loadLibexhsearch(() => this.performShift());
        } else {
            this.performShift();
        }
    }

    onHasToMove() {
        if (this.computedAction) {
            this.performMove();
        }
    }

    performShift() {
        const wasmPlayerId = this.store.getters["players/wasmPlayerId"];
        const playerCard = this.store.getters["players/mazeCard"](wasmPlayerId);
        const playerLocation = playerCard.location;
        const objectiveId = this.store.state.game.objectiveId;
        const leftoverCard = this.store.getters["board/leftoverMazeCard"];
        const mazeCardList = this.store.getters["board/mazeCardsRowMajorOrder"].concat([
            leftoverCard
        ]);
        const shiftLocations = getShiftLocations(this.store.state.board.mazeSize);
        const disabledShiftLocation = this.store.state.board.disabledShiftLocation;
        const previousShiftLocation = this.store.getters["board/oppositeLocation"](
            disabledShiftLocation
        );
        const instance = {
            playerLocation: playerLocation,
            objectiveId: objectiveId,
            mazeCardList: mazeCardList,
            shiftLocations: shiftLocations,
            previousShiftLocation: previousShiftLocation
        };
        this.computedAction = this.wasmGateway.computeActions(instance);
        let shiftAction = {
            playerId: wasmPlayerId,
            location: this.computedAction.shiftAction.location,
            leftoverRotation: this.computedAction.shiftAction.leftoverRotation
        };
        this.store.dispatch("game/shift", shiftAction);
    }

    performMove() {
        let shiftAction = {
            playerId: this.store.getters["players/wasmPlayerId"],
            targetLocation: this.computedAction.moveLocation
        };
        this.computedAction = undefined;
        this.store.dispatch("game/move", shiftAction);
    }
}
