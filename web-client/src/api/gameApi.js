import axios from "axios";

export default class GameApi {
    constructor(serverUrl) {
        this.apiPath = serverUrl + "/api";
        this.playerId = "";
    }

    doMove(toLocation, errorCallback) {
        var postMovePath = this.apiPath + "/games/0/move?p_id=" + this.playerId;
        axios
            .post(postMovePath, {
                location: toLocation
            })
            .catch(error => errorCallback(error));
    }

    doShift(shiftLocation, leftoverRotation, errorCallback) {
        var postShiftPath =
            this.apiPath + "/games/0/shift?p_id=" + this.playerId;
        axios
            .post(postShiftPath, {
                location: shiftLocation,
                leftoverRotation: leftoverRotation
            })
            .catch(error => errorCallback(error));
    }

    doAddPlayer(callback, errorCallback) {
        var addPlayerPath = this.apiPath + "/games/0/players";
        axios
            .post(addPlayerPath)
            .then(response => callback(response.data))
            .catch(error => errorCallback(error));
    }

    fetchState(callback, errorCallback) {
        var getStatePath =
            this.apiPath + "/games/0/state?p_id=" + this.playerId;
        axios
            .get(getStatePath)
            .then(response => callback(response.data))
            .catch(error => errorCallback(error));
    }
}
