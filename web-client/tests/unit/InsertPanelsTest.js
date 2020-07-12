import { mount } from "@vue/test-utils";
import InsertPanels from "@/components/InsertPanels.vue";

const factory = function(interaction, disabledShiftLocation = null) {
    return mount(InsertPanels, {
        propsData: {
            interaction: interaction,
            disabledShiftLocation: disabledShiftLocation
        }
    });
};

describe("InsertPanels", () => {
    it("sets interaction class on insert panels if interaction is required", () => {
        let insertPanels = factory(true);
        let insertPanelsHtml = insertPanels.findAll(".insert-panel");
        expect(insertPanelsHtml.is(".insert-panel--interaction")).toBe(true);
    });

    it("does not set interaction class on insert panels if move is required", () => {
        let insertPanels = factory(false);
        let insertPanelsHtml = insertPanels.findAll(".insert-panel");
        let insertPanelsWithInteraction = insertPanelsHtml.filter(panel =>
            panel.classes(".insert-panel--interaction")
        );
        expect(insertPanelsWithInteraction.length).toBe(0);
    });

    it("enables all insert panels but the one which is disabled in props: disabledShiftLocation", () => {
        let insertPanels = factory(true, { row: 0, column: 1 });
        let insertPanelsHtml = insertPanels.findAll(".insert-panel--disabled");
        expect(insertPanelsHtml.length).toBe(1);
        let xPos = Number.parseInt(insertPanelsHtml.at(0).attributes("x"));
        let yPos = Number.parseInt(insertPanelsHtml.at(0).attributes("y"));
        expect(xPos).toBe(2 * 100);
        expect(yPos).toBe(0 * 100);
    });
});
