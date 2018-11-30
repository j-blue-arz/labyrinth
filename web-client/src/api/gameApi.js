import axios from "axios";

export default class GameApi {
    constructor(serverUrl) {
        this.apiPath = serverUrl + "/api";
        this.playerId = "";
        this.fetchSource = axios.CancelToken.source();
    }

    doMove(toLocation) {
        var postMovePath = this.apiPath + "/games/0/move?p_id=" + this.playerId;
        return axios.post(postMovePath, {
            location: toLocation
        });
    }

    doShift(shiftLocation, leftoverRotation) {
        var postShiftPath =
            this.apiPath + "/games/0/shift?p_id=" + this.playerId;
        return axios.post(postShiftPath, {
            location: shiftLocation,
            leftoverRotation: leftoverRotation
        });
    }

    doAddPlayer() {
        var addPlayerPath = this.apiPath + "/games/0/players";
        return axios.post(addPlayerPath);
    }

    fetchState() {
        var getStatePath =
            this.apiPath + "/games/0/state?p_id=" + this.playerId;
        return axios.get(getStatePath, {
            cancelToken: this.fetchSource.token
        });
    }

    cancelAllFetches() {
        this.fetchSource.cancel();
        this.fetchSource = axios.CancelToken.source();
    }
}
