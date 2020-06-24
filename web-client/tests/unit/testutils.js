import VMazeCard from "@/components/VMazeCard.vue";
import VGameBoard from "@/components/VGameBoard.vue";

export function assertConsistentLocation(game, location) {
    expect(game.getMazeCard(location).location).toEqual(location);
}

export function extractIdMatrix(gameContainer) {
    var vMazeCards = gameContainer
        .find({ ref: "interactive-board" })
        .find(VGameBoard)
        .findAll(VMazeCard);
    var htmlCards = [];
    for (let i = 0; i < vMazeCards.length; i++) {
        var card = vMazeCards.at(i);
        if (!card.classes("leftover")) {
            var x = Number.parseInt(card.props("xPos"));
            var y = Number.parseInt(card.props("yPos"));
            var id = Number.parseInt(card.element.getAttribute("id"));
            htmlCards.push({
                x: x,
                y: y,
                id: id
            });
        }
    }
    htmlCards.sort(function(a, b) {
        if (a.y > b.y) {
            return 1;
        }
        if (a.y < b.y) {
            return -1;
        }
        if (a.x > b.x) {
            return 1;
        }
        if (a.x < b.x) {
            return -1;
        }
        return 0;
    });
    var ids = [];
    var i = 0;
    for (var row = 0; row < 7; row++) {
        ids.push([]);
        for (var col = 0; col < 7; col++) {
            ids[row].push(htmlCards[i++].id);
        }
    }
    return ids;
}

export function copyObjectStructure(obj) {
    return JSON.parse(JSON.stringify(obj));
}
