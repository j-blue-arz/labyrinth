import { defineStore } from "pinia";

import ValueError from "@/util/exceptions.js";

export const stateFactory = () => ({
    mazeSize: 0,
    cardsById: {},
    boardLayout: [],
    leftoverId: null,
    disabledShiftLocation: null,
});

export const useBoardStore = defineStore("board", {
    state: stateFactory,
    getters: {
        notEmpty: (state) => {
            return state.leftoverId !== null && state.mazeSize > 0;
        },
        mazeCardById: (state) => (id) => {
            return state.cardsById[id];
        },
        leftoverMazeCard: (state) => {
            return leftoverMazeCard(state);
        },
        mazeCard: (state) => (location) => {
            return mazeCardAtLocation(state, location);
        },
        isInside: (state) => (location) => {
            return isInside(location, state.mazeSize);
        },
        oppositeLocation: (state) => (location) => {
            return getOppositeLocation(location, state.mazeSize);
        },
        mazeCardsRowMajorOrder(state) {
            return [].concat.apply([], state.boardLayout).map(this.mazeCardById);
        },
        allIds: (state) => {
            return [].concat.apply([state.leftoverId], state.boardLayout);
        },
    },
    actions: {
        update(updateState) {
            this.updateBoard(updateState.maze);
            const n = updateState.maze.mazeSize;
            const enabledShiftLocations = updateState.enabledShiftLocations;
            const disabledShiftLocation = findDisabledShiftLocation(n, enabledShiftLocations);
            this.setDisabledShiftLocation(disabledShiftLocation);
            this.updatePlayers(updateState.players);
        },
        updatePlayers(players) {
            [].concat
                .apply([], this.boardLayout)
                .forEach((id) => this.cardsById[id].playerIds.splice(0));
            for (const player of players) {
                this.cardsById[player.mazeCardId].playerIds.push(player.id);
            }
        },
        movePlayer(move) {
            const sourceCard = this.mazeCardById(move.sourceCardId);
            const playerIndexInSource = sourceCard.playerIds.indexOf(move.playerId);
            this.cardsById[move.sourceCardId].playerIds.splice(playerIndexInSource, 1);
            this.cardsById[move.targetCardId].playerIds.push(move.playerId);
        },
        shift(shiftAction) {
            const location = shiftAction.location;
            if (locationsEqual(location, this.disabledShiftLocation)) {
                throw new ValueError("Shifting at " + location + " is not allowed.");
            }

            const n = this.mazeSize;

            let shiftLocations = generateShiftLocations(location, n);
            if (shiftLocations.length === n) {
                this.setLeftoverRotation(shiftAction.leftoverRotation);
                this.shiftAlongLocations(shiftLocations);
                this.setDisabledShiftLocation(getOppositeLocation(location, n));
                this.transferPlayers({
                    source: this.leftoverMazeCard.id,
                    target: this.mazeCard(location).id,
                });
            } else {
                throw new ValueError();
            }
        },
        rotateLeftoverClockwise() {
            const oldRotation = this.cardsById[this.leftoverId].rotation;
            this.setLeftoverRotation((oldRotation + 90) % 360);
        },
        updateBoard(maze) {
            const newState = {
                mazeSize: 0,
                leftoverId: this.leftoverId,
                cardsById: { ...this.cardsById },
                boardLayout: [],
            };

            const n = maze.mazeSize;
            newState.mazeSize = n;

            const mazeCardArray = maze.mazeCards;
            if (mazeCardArray) {
                if (newState.leftoverId !== mazeCardArray[0].id) {
                    newState.leftoverId = mazeCardArray[0].id;
                    newState.cardsById[newState.leftoverId] = createCardWithoutPlayers(
                        mazeCardArray[0],
                    );
                }

                let index = 1;
                for (let row = 0; row < n; row++) {
                    newState.boardLayout.push([]);
                    for (let col = 0; col < n; col++) {
                        newState.cardsById[mazeCardArray[index].id] = createCardWithoutPlayers(
                            mazeCardArray[index],
                        );
                        newState.boardLayout[row].push(mazeCardArray[index].id);
                        index++;
                    }
                }
            }

            this.$patch(newState);
        },
        setDisabledShiftLocation(shiftLocation) {
            this.disabledShiftLocation = shiftLocation;
        },
        shiftAlongLocations(locations) {
            const n = this.mazeSize;
            const pushedOut = locations[n - 1];
            const inserted = locations[0];
            let layout = this.boardLayout;
            let oldLeftoverId = this.leftoverId;
            this.leftoverId = layout[pushedOut.row][pushedOut.column];
            for (let i = n - 1; i > 0; i--) {
                const from = locations[i - 1];
                const to = locations[i];
                layout[to.row][to.column] = layout[from.row][from.column];
                setLocation(this, idAtLocation(this, to), to);
            }
            setLocation(this, oldLeftoverId, inserted);
            layout[inserted.row][inserted.column] = oldLeftoverId;
            setLocation(this, this.leftoverId, null);
        },
        transferPlayers(transfer) {
            const sourceMazeCard = this.cardsById[transfer.source];
            const targetMazeCard = this.cardsById[transfer.target];
            while (sourceMazeCard.playerIds.length) {
                targetMazeCard.playerIds.push(sourceMazeCard.playerIds.pop());
            }
        },
        setLeftoverRotation(rotation) {
            this.cardsById[this.leftoverId].rotation = rotation;
        },
    },
});

export function mazeCardAtLocation(state, location) {
    if (isInside(location, state.mazeSize)) {
        const id = state.boardLayout[location.row][location.column];
        return state.cardsById[id];
    } else {
        throw new RangeError();
    }
}

function setLocation(state, cardId, location) {
    state.cardsById[cardId] = { ...state.cardsById[cardId], location: location };
}

function idAtLocation(state, location) {
    if (isInside(location, state.mazeSize)) {
        return state.boardLayout[location.row][location.column];
    } else {
        throw new RangeError();
    }
}

export function isInside(location, mazeSize) {
    return (
        location.row >= 0 &&
        location.row < mazeSize &&
        location.column >= 0 &&
        location.column < mazeSize
    );
}

function createCardWithoutPlayers(mazeCard) {
    return { ...mazeCard, playerIds: [] };
}

function generateShiftLocations(location, n) {
    let shiftLocations = [];
    if (location.row === 0) {
        shiftLocations = columnLocations(location.column, n);
    } else if (location.row === n - 1) {
        shiftLocations = columnLocations(location.column, n);
        shiftLocations.reverse();
    } else if (location.column === n - 1) {
        shiftLocations = rowLocations(location.row, n);
        shiftLocations.reverse();
    } else if (location.column === 0) {
        shiftLocations = rowLocations(location.row, n);
    }
    return shiftLocations;
}

function findDisabledShiftLocation(n, apiShiftLocations) {
    let allShiftLocations = getShiftLocations(n);
    for (let location of allShiftLocations) {
        if (!apiShiftLocations.find((apiLocation) => locationsEqual(apiLocation, location))) {
            return location;
        }
    }
    return null;
}

export function locationsEqual(locationA, locationB) {
    return locationA?.row === locationB?.row && locationA?.column == locationB?.column;
}

export function getShiftLocations(n) {
    let allShiftLocations = [];
    for (let position = 1; position < n - 1; position += 2) {
        allShiftLocations.push({ row: 0, column: position });
        allShiftLocations.push({ row: position, column: 0 });
        allShiftLocations.push({ row: n - 1, column: position });
        allShiftLocations.push({ row: position, column: n - 1 });
    }
    return allShiftLocations;
}

function columnLocations(column, n) {
    var locations = [];
    for (let row = 0; row < n; row++) {
        locations.push({ row: row, column: column });
    }
    return locations;
}

function rowLocations(row, n) {
    var locations = [];
    for (let column = 0; column < n; column++) {
        locations.push({ row: row, column: column });
    }
    return locations;
}

function getOppositeLocation(borderLocation, n) {
    let oppositeLocation = null;
    if (borderLocation) {
        if (borderLocation.row === 0) {
            oppositeLocation = { row: n - 1, column: borderLocation.column };
        } else if (borderLocation.row === n - 1) {
            oppositeLocation = { row: 0, column: borderLocation.column };
        } else if (borderLocation.column === n - 1) {
            oppositeLocation = { row: borderLocation.row, column: 0 };
        } else if (borderLocation.column === 0) {
            oppositeLocation = { row: borderLocation.row, column: n - 1 };
        }
    }
    return oppositeLocation;
}

function leftoverMazeCard(state) {
    return state.cardsById[state.leftoverId];
}

export function loc(row, column) {
    return { row: row, column: column };
}
