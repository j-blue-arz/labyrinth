export const NO_ACTION = "NONE";
export const MOVE_ACTION = "MOVE";
export const SHIFT_ACTION = "SHIFT";

export default class Player {
    constructor(id, mazeCard, playerIndex) {
        this.id = id;
        this.mazeCard = mazeCard;
        this.playerIndex = playerIndex;
        this.nextAction = NO_ACTION;
    }

    static withId(id) {
        return new this(id, null);
    }

    static compareById(player1, player2) {
        return player1.id - player2.id;
    }
}
