import axios from "axios";

export default {
    fetchSource: axios.CancelToken.source(),
    apiPath: "api",

    doMove(playerId, toLocation) {
        var postMovePath = this.apiPath + "/games/0/move?p_id=" + playerId;
        return axios.post(postMovePath, {
            location: toLocation
        });
    },

    doShift(playerId, shiftLocation, leftoverRotation) {
        var postShiftPath = this.apiPath + "/games/0/shift?p_id=" + playerId;
        return axios.post(postShiftPath, {
            location: shiftLocation,
            leftoverRotation: leftoverRotation
        });
    },

    doAddPlayer() {
        let addPlayerPath = this.apiPath + "/games/0/players";
        return axios.post(addPlayerPath);
    },

    doAddBot(computeMethod) {
        let addPlayerPath = this.apiPath + "/games/0/players";
        return axios.post(addPlayerPath, {
            isBot: true,
            computationMethod: computeMethod
        });
    },

    removePlayer(playerId) {
        let deletePlayerPath = this.apiPath + "/games/0/players/" + playerId;
        return axios.delete(deletePlayerPath);
    },

    changePlayerName(playerId, name) {
        const changePlayerNamePath = this.apiPath + "/games/0/players/" + playerId + "/name";
        return axios.put(changePlayerNamePath, {
            name: name
        });
    },

    changeGame(size) {
        let putGamePath = this.apiPath + "/games/0";
        return axios.put(putGamePath, {
            mazeSize: size
        });
    },

    fetchState() {
        var getStatePath = this.apiPath + "/games/0/state";
        return axios.get(getStatePath, {
            cancelToken: this.fetchSource.token
        });
    },

    fetchComputationMethods() {
        let getComputationMethodsPath = this.apiPath + "/computation-methods";
        return axios.get(getComputationMethodsPath);
    },

    CANCEL_MESSAGE: "fetchState cancelled by user.",

    cancelAllFetches() {
        this.fetchSource.cancel(this.CANCEL_MESSAGE);
        this.fetchSource = axios.CancelToken.source();
    },

    errorWasThrownByCancel(error) {
        return error.toString().includes(this.CANCEL_MESSAGE);
    }
};
