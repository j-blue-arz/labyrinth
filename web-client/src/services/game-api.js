import axios from "axios";

const API_PATH = "api";
const POLL_INTERVAL_MS = 850;

let pollingTimer = 0;

export default {
    _fetchSource: axios.CancelToken.source(),
    stateObserver: () => {},
    errorHandler: () => {},
    _isPolling: false,

    // this will not start polling until the next request has finished.
    activatePolling() {
        this._isPolling = true;
    },

    stopPolling() {
        this._isPolling = false;
        this._suspendPolling();
    },

    resumePolling() {
        if (this._isPolling) {
            this._suspendPolling();
            if (pollingTimer === 0) {
                this._poll();
            }
        }
    },

    _suspendPolling() {
        if (pollingTimer !== 0) {
            clearTimeout(pollingTimer);
            pollingTimer = 0;
            this._cancelAllFetches();
        }
    },

    _poll() {
        this.fetchState();
        pollingTimer = setTimeout(() => this._poll(), POLL_INTERVAL_MS);
    },

    _handleError(error) {
        if (!this._errorWasThrownByCancel(error)) {
            this.errorHandler(error);
        }
    },

    resetHandlers() {
        this.stateObserver = () => {};
        this.errorHandler = () => {};
    },

    doMove(playerId, toLocation) {
        const postMovePath = API_PATH + "/games/0/move?p_id=" + playerId;
        this._suspendPolling();
        axios
            .post(postMovePath, {
                location: toLocation,
            })
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    doShift(playerId, shiftLocation, leftoverRotation, callback) {
        const postShiftPath = API_PATH + "/games/0/shift?p_id=" + playerId;
        this._suspendPolling();
        axios
            .post(postShiftPath, {
                location: shiftLocation,
                leftoverRotation: leftoverRotation,
            })
            .then((apiResponse) => callback(apiResponse.data))
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    doAddPlayer(callback) {
        const addPlayerPath = API_PATH + "/games/0/players";
        this._suspendPolling();
        axios
            .post(addPlayerPath)
            .then((apiResponse) => callback(apiResponse.data))
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    doAddBot(computeMethod) {
        const addPlayerPath = API_PATH + "/games/0/players";
        this._suspendPolling();
        axios
            .post(addPlayerPath, {
                isBot: true,
                computationMethod: computeMethod,
            })
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    removePlayer(playerId) {
        const deletePlayerPath = API_PATH + "/games/0/players/" + playerId;
        this._suspendPolling();
        axios
            .delete(deletePlayerPath)
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    changePlayerName(playerId, name) {
        const changePlayerNamePath = API_PATH + "/games/0/players/" + playerId + "/name";
        this._suspendPolling();
        axios
            .put(changePlayerNamePath, {
                name: name,
            })
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    changeGame(size) {
        const putGamePath = API_PATH + "/games/0";
        this._suspendPolling();
        axios
            .put(putGamePath, {
                mazeSize: size,
            })
            .catch((error) => this._handleError(error))
            .then(() => this.resumePolling());
    },

    fetchState() {
        var getStatePath = API_PATH + "/games/0/state";
        axios
            .get(getStatePath, {
                cancelToken: this._fetchSource.token,
            })
            .then((response) => this.stateObserver(response.data))
            .catch((error) => this._handleError(error));
    },

    fetchComputationMethods(callback) {
        let getComputationMethodsPath = API_PATH + "/computation-methods";
        axios
            .get(getComputationMethodsPath)
            .then((apiResponse) => callback(apiResponse.data))
            .catch((error) => this._handleError(error));
    },

    CANCEL_MESSAGE: "fetchState cancelled by user.",

    _cancelAllFetches() {
        this._fetchSource.cancel(this.CANCEL_MESSAGE);
        this._fetchSource = axios.CancelToken.source();
    },

    _errorWasThrownByCancel(error) {
        return error.toString().includes(this.CANCEL_MESSAGE);
    },
};
