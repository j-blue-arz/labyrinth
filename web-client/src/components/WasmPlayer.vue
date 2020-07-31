<template>
    <div>{{ playerType }}</div>
</template>

<script>
import { Game, SHIFT_ACTION, MOVE_ACTION, NO_ACTION } from "@/model/game.js";
import WasmGateway from "@/api/wasmGateway.js";

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
            wasmGateway: new WasmGateway()
        };
    },
    watch: {
        playerType: function(newType, oldType) {
            if (oldType !== "wasm" && newType === "wasm") {
                if (!this.wasmGateway.libexhsearch) {
                    this.wasmGateway.loadLibexhsearch(() => {
                        if (this.playerTurnAction === SHIFT_ACTION) {
                            this.computedAction = this.wasmGateway.computeActions(
                                this.game,
                                this.playerId
                            );
                            this.$emit("perform-shift", this.computedAction.shiftAction);
                        }
                    });
                } else {
                    if (this.playerTurnAction === SHIFT_ACTION) {
                        this.computedAction = this.wasmGateway.computeActions(
                            this.game,
                            this.playerId
                        );
                        this.$emit("perform-shift", this.computedAction.shiftAction);
                    }
                }
            }
        },
        playerTurnAction: function(newAction, oldAction) {
            if (this.wasmGateway.libexhsearch) {
                if (oldAction !== SHIFT_ACTION && newAction === SHIFT_ACTION) {
                    this.computedAction = this.wasmGateway.computeActions(this.game, this.playerId);
                    this.$emit("perform-shift", this.computedAction.shiftAction);
                } else if (
                    oldAction !== MOVE_ACTION &&
                    newAction === MOVE_ACTION &&
                    this.computedAction
                ) {
                    this.$emit("move-piece", this.computedAction.moveLocation);
                    this.computedAction = null;
                }
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
    },
    methods: {
        player: function() {
            return (
                this.game.nextAction.playerId === this.playerId &&
                this.game.nextAction.action === SHIFT_ACTION &&
                !this.game.getPlayer(this.userPlayerId).isComputer
            );
        }
    }
};
</script>

<style></style>
