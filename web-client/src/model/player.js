export default class Player {
    constructor(id, mazeCard, playerIndex) {
        this.id = id;
        this.mazeCard = mazeCard;
        this.playerIndex = playerIndex;
        this.isComputer = false;
        this.algorithm = "";
    }

    static withId(id) {
        return new this(id, null);
    }

    static compareById(player1, player2) {
        return player1.id - player2.id;
    }
}
