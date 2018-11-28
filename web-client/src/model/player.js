export default class Player {
    constructor(id, mazeCard) {
        this.id = id;
        this.mazeCard = mazeCard;
    }

    static withId(id) {
        return new this(id, null);
    }

    static compareById(player1, player2) {
        return player1.id - player2.id;
    }
}
