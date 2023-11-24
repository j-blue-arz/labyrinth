import WasmGateway from "@/services/wasmGateway.js";
import { NO_ACTION, MOVE_ACTION, SHIFT_ACTION } from "@/model/player";
import { useBoardStore, getShiftLocations } from "@/stores/board.js";
import { usePlayersStore } from "@/stores/players.js";
import { useGameStore } from "@/stores/game.js";

import { watch } from 'vue'

export default class WasmPlayer {
    constructor() {
        this.wasmGateway = new WasmGateway();
        this.computedAction = undefined;
        const playersStore = usePlayersStore()

        watch(
            () => playersStore.wasmPlayer?.nextAction ?? NO_ACTION,
            (newAction) => {
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
        const boardStore = useBoardStore();
        const playersStore = usePlayersStore();
        const gameStore = useGameStore();
        const wasmPlayerId = playersStore.wasmPlayerId;
        const playerCard = playersStore.mazeCard(wasmPlayerId);
        const playerLocation = playerCard.location;
        const objectiveId = gameStore.objectiveId;
        const leftoverCard = boardStore.leftoverMazeCard;
        const mazeCardList = boardStore.mazeCardsRowMajorOrder.concat([
            leftoverCard,
        ]);
        const shiftLocations = getShiftLocations(boardStore.mazeSize);
        const disabledShiftLocation = boardStore.disabledShiftLocation;
        const previousShiftLocation =
            boardStore.oppositeLocation(disabledShiftLocation);
        const instance = {
            playerLocation: playerLocation,
            objectiveId: objectiveId,
            mazeCardList: mazeCardList,
            shiftLocations: shiftLocations,
            previousShiftLocation: previousShiftLocation,
        };
        this.computedAction = this.wasmGateway.computeActions(instance);
        let shiftAction = {
            playerId: wasmPlayerId,
            location: this.computedAction.shiftAction.location,
            leftoverRotation: this.computedAction.shiftAction.leftoverRotation,
        };
        gameStore.shift(shiftAction);
    }

    performMove() {
        const gameStore = useGameStore();
        const playersStore = usePlayersStore();
        let moveAction = {
            playerId: playersStore.wasmPlayerId,
            targetLocation: this.computedAction.moveLocation,
        };
        this.computedAction = undefined;
        gameStore.move(moveAction);
    }
}
