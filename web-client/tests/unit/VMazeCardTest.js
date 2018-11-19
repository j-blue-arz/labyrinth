import { mount } from "@vue/test-utils";
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazecard.js";

const wrapperFactory = (
    props = {
        mazeCard: new MazeCard(0, 0, 0, "NSEW", 0),
        cardSize: 100
    }
) => {
    return mount(VMazeCard, {
        propsData: { ...props }
    });
};

describe("VMazeCard", () => {
    it("contains an svg-element", () => {
        const wrapper = wrapperFactory();
        expect(wrapper.contains("svg")).toBe(true);
    });

    it("has width of 100 when cardSize is 100", () => {
        const wrapper = wrapperFactory();
        expect(wrapper.element.getAttribute("width")).toBe("100");
    });

    it("has height of 200 when cardSize is 200", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "NSEW", 0),
            cardSize: 200
        });
        expect(wrapper.element.getAttribute("height")).toBe("200");
    });

    it("includes north door when MazeCard has a north door", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "NW", 0),
            cardSize: 100
        });
        expect(wrapper.find({ ref: "northDoor" }).exists()).toBeTruthy();
    });

    it("does not include north door when MazeCard object does not have a north door", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "EW", 0),
            cardSize: 100
        });
        expect(wrapper.find({ ref: "northDoor" }).exists()).toBeFalsy();
    });

    it("does not render players when the MazeCard object does not contain pieces", () => {
        const wrapper = wrapperFactory({
            mazeCard: new MazeCard(0, 0, 0, "EW", 0),
            cardSize: 100
        });
        expect(wrapper.findAll("player-piece").length).toBe(0);
    })

    it("renders a single player", () => {
        var mazeCard = new MazeCard(0, 0, 0, "EW", 0);
        mazeCard.playerPieces.push({
            id: 0
        })
        const wrapper = wrapperFactory({
            mazeCard: mazeCard,
            cardSize: 100,
        });
        expect(wrapper.findAll(".player-piece").length).toBe(1);
    });

    it("renders two players without overlap", () => {
        var mazeCard = new MazeCard(0, 0, 0, "EW", 0);
        mazeCard.playerPieces.push({
            id: 0
        });
        mazeCard.playerPieces.push({
            id: 1
        });
        const wrapper = wrapperFactory({
            mazeCard: mazeCard,
            cardSize: 50,
        });
        var playerPieces = wrapper.findAll(".player-piece");
        expect(playerPieces.length).toBe(2);
        var cx0 = Number.parseFloat(playerPieces.at(0).element.getAttribute("cx"));
        var cy0 = Number.parseFloat(playerPieces.at(0).element.getAttribute("cy"));
        var cx1 = Number.parseFloat(playerPieces.at(1).element.getAttribute("cx"));
        var cy1 = Number.parseFloat(playerPieces.at(1).element.getAttribute("cy"));
        var r0 = Number.parseFloat(playerPieces.at(0).element.getAttribute("r"));
        var r1 = Number.parseFloat(playerPieces.at(1).element.getAttribute("r"));
        var distance = Math.sqrt(Math.pow((cx0 - cx1), 2) + Math.pow((cy0 - cy1), 2));
        var radiusSums = r0 + r1;
        expect(distance).toBeGreaterThan(radiusSums);
    });
});
