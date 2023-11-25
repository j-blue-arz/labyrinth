import generateBoard from "@/model/board-factory.js";
import { beforeEach, describe, expect, it } from "vitest";

describe("generateBoard(7)", () => {
    beforeEach(() => {
        board = generateBoard(7);
        size = 7;
    });

    it("returns object with fields mazeSize and mazeCards", () => {
        expect(board).toEqual(
            expect.objectContaining({ mazeSize: expect.any(Number), mazeCards: expect.any(Array) }),
        );
    });

    it("returns mazeSize 7", () => {
        expect(board.mazeSize).toEqual(7);
    });

    it("returns 50 maze cards", () => {
        expect(board.mazeCards.length).toEqual(50);

        board.mazeCards.forEach((mazeCard) =>
            expect(mazeCard).toEqual(
                expect.objectContaining({
                    id: expect.any(Number),
                    outPaths: expect.stringMatching("^[NESW]{2,4}$"),
                    rotation: expect.anything(),
                    // location omitted, because null is difficult to match
                }),
            ),
        );
    });

    it("returns unique maze card ids", () => {
        var ids = new Set(board.mazeCards.map((mazeCard) => mazeCard.id));
        expect(ids.size).toEqual(50);
    });

    it("generates valid outPaths", () => {
        board.mazeCards.forEach((mazeCard) => {
            expect(mazeCard.outPaths).toEqual(expect.stringMatching("^[NESW]{2,4}$"));
            expect(count("N", mazeCard.outPaths)).toBeLessThanOrEqual(1);
            expect(count("E", mazeCard.outPaths)).toBeLessThanOrEqual(1);
            expect(count("S", mazeCard.outPaths)).toBeLessThanOrEqual(1);
            expect(count("W", mazeCard.outPaths)).toBeLessThanOrEqual(1);
        });
    });

    it("generates valid rotations", () => {
        board.mazeCards.forEach((mazeCard) => {
            expect([0, 90, 180, 270]).toContain(mazeCard.rotation);
        });
    });

    it("places leftover first", () => {
        expect(board.mazeCards[0].location).toBeNull();
    });

    it("returns maze cards in row-wise order", () => {
        let index = 1;
        for (let row = 0; row < 7; row++) {
            for (let column = 0; column < 7; column++) {
                expect(board.mazeCards[index].location).toEqual(
                    expect.objectContaining({ row: row, column: column }),
                );
                index++;
            }
        }
    });

    it("places corners at the four corners", () => {
        expect(mazeCardAt(0, 0).outPaths).toEqual("NE");
        expect(mazeCardAt(0, 0).rotation).toEqual(90);

        expect(mazeCardAt(0, 6).outPaths).toEqual("NE");
        expect(mazeCardAt(0, 6).rotation).toEqual(180);

        expect(mazeCardAt(6, 6).outPaths).toEqual("NE");
        expect(mazeCardAt(6, 6).rotation).toEqual(270);

        expect(mazeCardAt(6, 0).outPaths).toEqual("NE");
        expect(mazeCardAt(6, 0).rotation).toEqual(0);
    });

    it("places t-junctions at non-corner even borders, facing inward", () => {
        expect(mazeCardAt(0, 2).outPaths).toEqual("NES");
        expect(mazeCardAt(0, 2).rotation).toEqual(90);

        expect(mazeCardAt(2, 6).outPaths).toEqual("NES");
        expect(mazeCardAt(2, 6).rotation).toEqual(180);

        expect(mazeCardAt(6, 2).outPaths).toEqual("NES");
        expect(mazeCardAt(6, 2).rotation).toEqual(270);

        expect(mazeCardAt(2, 0).outPaths).toEqual("NES");
        expect(mazeCardAt(2, 0).rotation).toEqual(0);
    });

    it("places t-junctions at non-border even locations, facing inward", () => {
        expect(mazeCardAt(2, 2).outPaths).toEqual("NES");
        expect([0, 90]).toContain(mazeCardAt(2, 2).rotation);

        expect(mazeCardAt(2, 4).outPaths).toEqual("NES");
        expect([90, 180]).toContain(mazeCardAt(2, 4).rotation);

        expect(mazeCardAt(4, 4).outPaths).toEqual("NES");
        expect([180, 270]).toContain(mazeCardAt(4, 4).rotation);

        expect(mazeCardAt(4, 2).outPaths).toEqual("NES");
        expect([0, 270]).toContain(mazeCardAt(4, 2).rotation);
    });

    it("does not place a cross anywhere", () => {
        board.mazeCards.forEach((mazeCard) => expect(mazeCard.outPaths).not.toEqual("NESW"));
    });
});

describe("generateBoard(9)", () => {
    beforeEach(() => {
        board = generateBoard(9);
        size = 9;
    });

    it("places cross in the middle of the board", () => {
        expect(mazeCardAt(4, 4).outPaths).toEqual("NESW");
    });
});

let size;

function mazeCardAt(row, column) {
    return board.mazeCards[row * size + column + 1];
}

function count(c, str) {
    return str.split(c).length - 1;
}

let board;
