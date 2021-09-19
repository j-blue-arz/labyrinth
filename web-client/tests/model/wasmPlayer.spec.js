import WasmPlayer from "@/model/wasmPlayer.js";
import WasmGateway from "@/services/wasmGateway.js";

const mockHasLibexhsearch = jest.fn().mockReturnValue(true);
const mockLoadLibexhsearch = jest.fn();
const mockComputeActions = jest.fn();

const spyPerformShift = jest.fn();
const spyPerformMove = jest.fn();

jest.mock("@/services/wasmGateway.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            hasLibexhsearch: mockHasLibexhsearch,
            loadLibexhsearch: mockLoadLibexhsearch,
            computeActions: mockComputeActions
        };
    });
});

beforeAll(() => {
    WasmGateway.mockClear();
    mockHasLibexhsearch.mockClear();
    mockLoadLibexhsearch.mockClear();
    mockComputeActions.mockClear();
    spyPerformShift.mockClear();
    spyPerformMove.mockClear();
});

const givenWasmGatewayReturns = function(shiftLocation, leftoverRotation, moveLocation) {
    let computedActions = {
        shiftAction: {
            location: shiftLocation,
            leftoverRotation: leftoverRotation
        },
        moveLocation: moveLocation
    };
    mockComputeActions.mockReturnValue(computedActions);
};

const givenShiftHasAlreadyBeenPerformed = function(player) {
    player.setTurnAction("SHIFT");
    mockComputeActions.mockClear();
    spyPerformShift.mockClear();
    spyPerformMove.mockClear();
};

describe("WasmPlayer", () => {
    it("when it is his turn to shift", () => {
        let game = "game";
        let playerId = 1;
        let player = new WasmPlayer(playerId, game, spyPerformShift, spyPerformMove);
        givenWasmGatewayReturns(loc(0, 1), 90, loc(3, 3));

        player.setTurnAction("SHIFT");

        expect(mockComputeActions).toHaveBeenCalledWith(game, playerId);
        let shiftAction = {
            playerId: playerId,
            location: loc(0, 1),
            leftoverRotation: 90
        };
        expect(spyPerformShift).toHaveBeenCalledWith(shiftAction);
        expect(spyPerformMove).not.toHaveBeenCalled();
    });

    it("when it is his turn to move", () => {
        let game = "game";
        let playerId = 1;
        let player = new WasmPlayer(playerId, game, spyPerformShift, spyPerformMove);
        givenWasmGatewayReturns(loc(0, 1), 90, loc(3, 3));
        givenShiftHasAlreadyBeenPerformed(player);

        player.setTurnAction("MOVE");

        expect(mockComputeActions).not.toHaveBeenCalled();
        let moveAction = {
            playerId: playerId,
            targetLocation: loc(3, 3)
        };
        expect(spyPerformMove).toHaveBeenCalledWith(moveAction);
        expect(spyPerformShift).not.toHaveBeenCalled();
    });
});

const loc = function(row, column) {
    return { row: row, column: column };
};
