<template>
    <div>{{ playerType }}</div>
</template>

<script>
import { Game, SHIFT_ACTION, MOVE_ACTION, NO_ACTION } from "@/model/game.js";
import WasmPlayer from "@/model/wasmPlayer.js";

export default {
    name: "wasm-player",
    props: {
        game: {
            type: Game,
            required: true
        },
        playerId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            computedAction: null,
            wasmPlayer: null
        };
    },
    watch: {
        playerType: function(newType, oldType) {
            if (oldType !== "wasm" && newType === "wasm") {
                this.wasmPlayer = new WasmPlayer(
                    this.playerId,
                    this.game,
                    shiftAction => this.$emit("perform-shift", shiftAction),
                    moveAction => this.$emit("move-piece", moveAction)
                );
            }
        },
        playerTurnAction: function(newAction, oldAction) {
            if (oldAction !== SHIFT_ACTION && newAction === SHIFT_ACTION) {
                this.wasmPlayer.onHasToShift();
            } else if (oldAction !== MOVE_ACTION && newAction === MOVE_ACTION) {
                this.wasmPlayer.onHasToMove();
            }
        }
    },
    computed: {
        playerType: function() {
            if (this.game.hasStarted()) {
                let player = this.game.getPlayer(this.playerId);
                if (player) {
                    return player.computationMethod;
                }
            }
            return "";
        },
        playerTurnAction: function() {
            if (this.game.hasStarted()) {
                let player = this.game.getPlayer(this.playerId);
                if (player) {
                    return player.turnAction;
                }
            }
            return NO_ACTION;
        }
    }
};
</script>

<style></style>
