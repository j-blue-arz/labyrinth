export default class CountdownTimer {
    constructor(startSeconds) {
        this._timer = 0;
        this._remainingSeconds = 0;
        this._startSeconds = startSeconds;
    }

    get remaining() {
        return this._remainingSeconds;
    }

    get startSeconds() {
        return this._startSeconds;
    }

    isRunning() {
        return this._timer !== 0;
    }

    restartCountdown() {
        this.stopCountdown();
        this._remainingSeconds = this._startSeconds;
        this._timer = setInterval(() => this._countDown(), 1000);
    }

    stopCountdown() {
        if (this._timer !== 0) {
            clearInterval(this._timer);
            this._timer = 0;
        }
    }

    _countDown() {
        this._remainingSeconds--;
        if (this._remainingSeconds <= 0) {
            this.stopCountdown();
            this._remainingSeconds = 0;
        }
    }
}
