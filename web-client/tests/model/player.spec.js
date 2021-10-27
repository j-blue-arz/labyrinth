import { getLabel } from "@/model/player.js";

describe("getLabel", () => {
    it("returns player name for non-bot players", () => {
        const player = { id: 7, isWasm: false, isUser: false, name: "felix" };

        const label = getLabel(player);

        expect(label).toEqual("felix");
    });

    it("returns human-readable description for bots", () => {
        const player = { id: 7, isBot: true, computationMethod: "libexhsearch" };

        const label = getLabel(player);

        expect(label).toEqual("Exhaustive Search (1P)");
    });
});
