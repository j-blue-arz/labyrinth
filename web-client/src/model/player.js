export default class Player {
    constructor(id, colorIndex) {
        this.id = id;
        this.mazeCard = null;
        this.colorIndex = colorIndex;
        this.isComputer = false;
        this.algorithm = "";
        this.isUser = false;
        this.turnAction = "NONE"; // one of NONE, MOVE, or SHIFT
        this.score = 0;
    }

    hasToMove() {
        return this.turnAction == "MOVE";
    }

    hasToShift() {
        return this.turnAction == "SHIFT";
    }

    static withId(id) {
        return new this(id, null);
    }

    static newFromApi(apiPlayer, colorIndex) {
        let player = new this(apiPlayer.id, colorIndex);
        player.fillFromApi(apiPlayer, colorIndex);
        return player;
    }

    fillFromApi(apiPlayer) {
        this.score = apiPlayer.score;
        if (apiPlayer.isComputerPlayer) {
            this.isComputer = true;
            this.algorithm = apiPlayer.algorithm;
        }
    }
}
