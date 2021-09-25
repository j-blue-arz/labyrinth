import { state, mutations } from "@/store/modules/players.js";

describe("mutations", () => {
    describe("update", () => {
        beforeEach(() => {
            apiPlayers = [];
            givenApiPlayer({
                id: 42,
                mazeCardId: 16,
                pieceIndex: 0,
                isBot: true,
                computationMethod: "random"
            });
            givenApiPlayer({
                id: 17,
                pieceIndex: 1,
                mazeCardId: 15,
                score: 12,
                name: "Fred"
            });
        });

        it("sets correct number of players for empty game", () => {
            givenNoPlayersInState();

            whenSetPlayersFromApi();

            thenPlayerExists(42);
            thenPlayerExists(17);
        });

        it("fills bot from api", () => {
            givenNoPlayersInState();

            whenSetPlayersFromApi();

            const botPlayer = playerWithId(42);
            expect(botPlayer.id).toBe(42);
            expect(botPlayer.mazeCard).toBe(16);
            expect(botPlayer.pieceIndex).toBe(0);
            expect(botPlayer.isBot).toBe(true);
            expect(botPlayer.computationMethod).toBe("random");
            expect(botPlayer.name).toBe("");
        });

        it("fills human player from api", () => {
            givenNoPlayersInState();

            whenSetPlayersFromApi();

            const player = playerWithId(17);
            expect(player.id).toBe(17);
            expect(player.mazeCard).toBe(15);
            expect(player.pieceIndex).toBe(1);
            expect(player.score).toBe(12);
            expect(player.isBot).toBe(false);
            expect(player.name).toBe("Fred");
        });

        it("keeps value of isUser for existing user player", () => {
            givenPlayerInState({ id: 2, isUser: true });
            givenApiPlayer({
                id: 2,
                pieceIndex: 1,
                mazeCardId: 15
            });

            whenSetPlayersFromApi();

            expect(playerWithId(2).isUser).toBe(true);
        });

        it("keeps value of isUser for existing non-user player", () => {
            givenPlayerInState({ id: 2, isUser: false });
            givenApiPlayer({
                id: 2,
                pieceIndex: 1,
                mazeCardId: 15
            });

            whenSetPlayersFromApi();

            expect(playerWithId(2).isUser).toBe(false);
        });

        it("sets isUser to false for new players", () => {
            givenNoPlayersInState();

            whenSetPlayersFromApi();

            expect(playerWithId(17).isUser).toBe(false);
        });

        it("removes player if not present in api", () => {
            givenPlayerInState({ id: 2 });

            whenSetPlayersFromApi();

            thenPlayerDoesNotExist(2);
        });
    });
});

const { update } = mutations;

let players;
let apiPlayers = [];

const givenNoPlayersInState = function() {
    players = state();
};

const givenPlayerInState = function(player) {
    const playerId = player.id;
    players = { byId: { [playerId]: player }, allIds: [playerId] };
};

const givenApiPlayer = function(apiPlayer) {
    apiPlayers.push(apiPlayer);
};

const whenSetPlayersFromApi = function() {
    update(players, apiPlayers);
};

const thenPlayerExists = function(id) {
    expect(players.byId).toHaveProperty("" + id);
    expect(players.allIds).toContain(id);
};

const thenPlayerDoesNotExist = function(id) {
    expect(players.byId).not.toHaveProperty("" + id);
    expect(players.allIds).not.toContain(id);
};

const playerWithId = function(id) {
    return players.byId[id];
};
