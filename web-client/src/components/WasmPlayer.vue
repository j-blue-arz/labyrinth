<template>
    <div>{{ playerType }}</div>
</template>

<script>
import { Game, loc, SHIFT_ACTION, MOVE_ACTION, NO_ACTION } from "@/model/game.js";

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
            libexhsearch: null,
            isLoading: false,
            computedAction: null,
            publicPath: process.env.BASE_URL
        };
    },
    watch: {
        playerType: function(newType, oldType) {
            if (oldType !== "wasm" && newType === "wasm") {
                if (!this.libexhsearch) {
                    this.loadLibexhsearch(() => {
                        if (this.playerTurnAction === SHIFT_ACTION) {
                            this.computeActions();
                        }
                    });
                } else {
                    if (this.playerTurnAction === SHIFT_ACTION) {
                        this.computeActions();
                    }
                }
            }
        },
        playerTurnAction: function(newAction, oldAction) {
            if (this.libexhsearch) {
                if (oldAction !== SHIFT_ACTION && newAction === SHIFT_ACTION) {
                    this.computeActions();
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
                    return player.type;
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
        computeActions: function() {
            this.computedAction = null;
            let player = this.game.getPlayer(this.playerId);
            let objectiveId = -1;
            let vectorNodes = new this.libexhsearch.vectorOfNode();
            let mazeCardList = this.game.mazeCardsAsList().concat([this.game.leftoverMazeCard]);
            for (let mazeCard of mazeCardList) {
                vectorNodes.push_back(this.createNode(mazeCard));
                if (mazeCard.hasObject) {
                    objectiveId = mazeCard.id;
                }
            }

            let mazeGraph = new this.libexhsearch.MazeGraph(vectorNodes);
            let border = this.game.n - 1;
            for (var position = 1; position < border; position += 2) {
                mazeGraph.addShiftLocation(loc(0, position));
                mazeGraph.addShiftLocation(loc(position, 0));
                mazeGraph.addShiftLocation(loc(position, border));
                mazeGraph.addShiftLocation(loc(border, position));
            }

            let previousShiftLocation = loc(-1, -1);
            if (this.game.disabledShiftLocation) {
                previousShiftLocation = this.game.getOppositeLocation(
                    this.game.disabledShiftLocation
                );
            }

            let action = this.libexhsearch.findBestAction(
                mazeGraph,
                player.mazeCard.location,
                objectiveId,
                previousShiftLocation
            );

            this.computedAction = {
                shiftAction: {
                    location: loc(action.shift.location.row, action.shift.location.column),
                    leftoverRotation: action.shift.rotation
                },
                moveLocation: loc(action.move_location.row, action.move_location.column)
            };

            mazeGraph.delete();
            for (let i = 0; i < vectorNodes.size(); ++i) {
                vectorNodes.get(i).delete();
            }
            vectorNodes.delete();

            this.$emit("perform-shift", this.computedAction.shiftAction);
        },
        createNode: function(mazeCard) {
            let id = mazeCard.id;
            let outPathBitmask = 0;
            if (mazeCard.hasNorthOutPath()) {
                outPathBitmask += 1;
            }
            if (mazeCard.hasEastOutPath()) {
                outPathBitmask += 2;
            }
            if (mazeCard.hasSouthOutPath()) {
                outPathBitmask += 4;
            }
            if (mazeCard.hasWestOutPath()) {
                outPathBitmask += 8;
            }
            let rotation = mazeCard.rotation;
            return new this.libexhsearch.Node(id, outPathBitmask, rotation);
        },
        player: function() {
            return (
                this.game.nextAction.playerId === this.playerId &&
                this.game.nextAction.action === SHIFT_ACTION &&
                !this.game.getPlayer(this.userPlayerId).isComputer
            );
        },
        loadLibexhsearch: function(callback) {
            if (!this.isLoading) {
                this.isLoading = true;
                this.loadRuntime()
                    .then(loadWasm => {
                        loadWasm().then(libexhsearch => {
                            this.libexhsearch = libexhsearch;
                            this.isLoading = false;
                            callback();
                        });
                    })
                    .catch(reason => {
                        console.error("failed to load runtime: " + reason);
                        this.isLoading = false;
                    })
                    .then(() => {
                        this.isLoading = false;
                    });
            }
        },
        loadRuntime: function() {
            return new Promise((resolve, reject) => {
                const url =
                    location.protocol +
                    "//" +
                    location.host +
                    this.publicPath +
                    "wasm/libexhsearch.js";
                const script = document.createElement("script");
                script.type = "text/javascript";
                script.async = true;
                script.addEventListener("load", () => {
                    resolve(window["libexhsearch"]);
                });
                script.addEventListener("error", () => {
                    reject(new Error(`Error loading ${url}`));
                });
                script.src = url;
                document.body.appendChild(script);
            });
        }
    }
};
</script>

<style></style>
