export const state = () => ({
    mazeSize: 0,
    cardsById: {},
    boardLayout: [],
    leftoverId: null,
    disabledShiftLocation: null
});

const getters = {};

const actions = {};

export const mutations = {
    update(state, apiState) {
        const n = apiState.maze.mazeSize;
        state.mazeSize = n;
        const apiMazeCards = apiState.maze.mazeCards;
        state.leftoverId = apiMazeCards[0].id;
        state.cardsById[state.leftoverId] = apiMazeCards[0];
        var index = 1;
        for (var row = 0; row < n; row++) {
            state.boardLayout.push([]);
            for (var col = 0; col < n; col++) {
                state.boardLayout[row].push(apiMazeCards[index].id);
                state.cardsById[apiMazeCards[index].id] = apiMazeCards[index];
                index++;
            }
        }
        const enabledShiftLocations = apiState.enabledShiftLocations;
        state.disabledShiftLocation = findDisabledShiftLocation(n, enabledShiftLocations);
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

const findDisabledShiftLocation = function(n, apiShiftLocations) {
    let allShiftLocations = getShiftLocations(n);
    for (let location of allShiftLocations) {
        if (!apiShiftLocations.find(apiLocation => locationEqual(apiLocation, location))) {
            return location;
        }
    }
    return null;
};

const locationEqual = function(locationA, locationB) {
    return locationA.row === locationB.row && locationA.column == locationB.column;
};

const getShiftLocations = function(n) {
    let allShiftLocations = [];
    for (let position = 1; position < n - 1; position += 2) {
        allShiftLocations.push({ row: 0, column: position });
        allShiftLocations.push({ row: position, column: 0 });
        allShiftLocations.push({ row: n - 1, column: position });
        allShiftLocations.push({ row: position, column: n - 1 });
    }
    return allShiftLocations;
};
