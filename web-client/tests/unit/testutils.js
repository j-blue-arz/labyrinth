export function assertConsistentLocation(game, location) {
    expect(game.getMazeCard(location).location).toEqual(location);
}

export function loc(row, column) {
    return { row: row, column: column };
}
