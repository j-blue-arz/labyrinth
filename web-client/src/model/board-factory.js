const CORNER = "NE";
const TJUNCT = "NES";
const CROSS = "NESW";
const STRAIGHT = "NS";

export function generateBoard(size) {
    let mazeCards = [];
    for (let row = 0; row < size; row++) {
        mazeCards.push([]);
        for (let column = 0; column < size; column++) {
            mazeCards[row].push(null);
        }
    }

    const a = size - 1;
    mazeCards[0][0] = generateFixedMazeCard(CORNER, 90);
    mazeCards[0][a] = generateFixedMazeCard(CORNER, 180);
    mazeCards[a][a] = generateFixedMazeCard(CORNER, 270);
    mazeCards[a][0] = generateFixedMazeCard(CORNER, 0);

    if (size % 4 == 3) {
        const middle = Math.floor(size / 2);
        mazeCards[middle][middle] = generateFixedMazeCard(CROSS, 0);
    }

    for (let row = 0; row < size; row += 2) {
        for (let column = 0; column < size; column += 2) {
            if (!mazeCards[row][column]) {
                const rotation = rotationOfFixedTJunct(row, column, size);
                mazeCards[row][column] = generateFixedMazeCard(TJUNCT, rotation);
            }
        }
    }

    let free = 1;
    for (let row = 0; row < size; row++) {
        for (let column = 0; column < size; column++) {
            if (!mazeCards[row][column]) {
                free++;
            }
        }
    }

    let freeCards = generateFreeCards(free);
    let leftover = freeCards.pop();
    for (let row = 0; row < size; row++) {
        for (let column = 0; column < size; column++) {
            if (!mazeCards[row][column]) {
                mazeCards[row][column] = freeCards.pop();
            }
        }
    }

    for (let row = 0; row < size; row++) {
        for (let column = 0; column < size; column++) {
            mazeCards[row][column].location = { row: row, column: column };
        }
    }

    mazeCards = [].concat.apply([leftover], mazeCards);
    for (let id = 0; id < mazeCards.length; id++) {
        mazeCards[id].id = id;
    }

    return { mazeSize: size, mazeCards: mazeCards };
}

function rotationOfFixedTJunct(row, column, size) {
    const a = size - 1;
    if (column <= row && row < a - column) return 0;
    if (row < column && column <= a - row) return 90;
    if (a - column < row && row <= column) return 180;
    return 270;
}

function generateFixedMazeCard(outPaths, rotation) {
    return {
        id: 0,
        outPaths: outPaths,
        rotation: rotation,
        location: null
    };
}

function generateFreeMazeCard(outPaths) {
    return {
        id: 0,
        outPaths: outPaths,
        rotation: Math.floor(Math.random() * 4) * 90,
        location: null
    };
}

function generateFreeCards(remaining) {
    let nums = {
        [CORNER]: Math.floor((remaining * 15) / 34),
        [TJUNCT]: Math.floor((remaining * 6) / 34),
        [STRAIGHT]: Math.floor((remaining * 13) / 34),
        [CROSS]: 0
    };

    remaining = remaining - Object.values(nums).reduce((acc, val) => acc + val, 0);

    if (remaining > 0) nums[CORNER] += 1;
    if (remaining > 1) nums[STRAIGHT] += 1;

    let cards = [];
    Object.keys(nums).forEach(outPath => {
        for (let i = 0; i < nums[outPath]; i++) {
            cards.push(generateFreeMazeCard(outPath));
        }
    });

    shuffle(cards);
    return cards;
}

// https://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}
