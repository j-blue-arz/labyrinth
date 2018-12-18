import MazeCard from "@/model/mazecard.js";

var hasValidState = function(mazeCard) {
    return (
        Number(mazeCard.hasNorthDoor()) +
            Number(mazeCard.hasEastDoor()) +
            Number(mazeCard.hasWestDoor()) +
            Number(mazeCard.hasSouthDoor()) >=
            2 &&
        mazeCard.rotation % 90 === 0 &&
        Number.isInteger(mazeCard.location.row) &&
        Number.isInteger(mazeCard.location.column) &&
        Number.isInteger(mazeCard.id)
    );
};

describe("MazeCard", () => {
    describe("constructor", () => {
        it("throws exception when id is not numeric", () => {
            expect(() => new MazeCard("a", 0, 0, "NS", 0)).toThrowError(Error);
        });

        it("throws exception when row is not integer", () => {
            expect(() => new MazeCard(2, 1.7, 0, "NS", 0)).toThrowError(Error);
        });

        it("throws exception when column is not integer", () => {
            expect(() => new MazeCard(4, 1, [], "NS", 0)).toThrowError(Error);
        });

        it("throws exception when doors is not string", () => {
            expect(() => new MazeCard(4, 1, 4, ["N", "E"], 0)).toThrowError(
                Error
            );
        });

        it("throws exception when doors has same door twice", () => {
            expect(() => new MazeCard(4, 1, 4, "NNE", 0)).toThrowError(Error);
        });

        it("throws exception when doors has less than two doors", () => {
            expect(() => new MazeCard(4, 1, 4, "N", 0)).toThrowError(Error);
        });

        it("does not throw for valid parameters", () => {
            expect(() => new MazeCard(4, 1, 4, "NE", 90)).not.toThrow();
        });

        it("returns valid mazeCard for valid parameters", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NE", 90);
            expect(hasValidState(mazeCard)).toBe(true);
        });
    });

    describe("rotation", () => {
        it("is set with value from constructor", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NE", 180);
            expect(mazeCard.rotation).toBe(180);
            expect(hasValidState(mazeCard)).toBe(true);
        });

        it("is increased by 90 when rotated clockwise", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NE", 90);
            mazeCard.rotateClockwise();
            expect(mazeCard.rotation).toBe(180);
            expect(hasValidState(mazeCard)).toBe(true);
        });

        it("is set to 0 when rotated clockwise, starting from 270", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NE", 270);
            mazeCard.rotateClockwise();
            expect(mazeCard.rotation).toBe(0);
            expect(hasValidState(mazeCard)).toBe(true);
        });
    });

    describe("doors", () => {
        it("are set from constructor", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NE", 0);
            expect(mazeCard.hasNorthDoor()).toBe(true);
            expect(mazeCard.hasEastDoor()).toBe(true);
            expect(mazeCard.hasSouthDoor()).toBe(false);
            expect(mazeCard.hasWestDoor()).toBe(false);
        });

        it("do not respect rotation", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NS", 270);
            expect(mazeCard.hasNorthDoor()).toBe(true);
            expect(mazeCard.hasEastDoor()).toBe(false);
            expect(mazeCard.hasSouthDoor()).toBe(true);
            expect(mazeCard.hasWestDoor()).toBe(false);
        });

        it("are not rotated when rotateClockwise() is called", () => {
            var mazeCard = new MazeCard(4, 1, 4, "NE", 0);
            mazeCard.rotateClockwise();
            expect(mazeCard.hasNorthDoor()).toBe(true);
            expect(mazeCard.hasEastDoor()).toBe(true);
            expect(mazeCard.hasSouthDoor()).toBe(false);
            expect(mazeCard.hasWestDoor()).toBe(false);
        });
    });
});
