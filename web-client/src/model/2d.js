export class Vector {
    constructor(x, y) {
        this._x = x;
        this._y = y;
    }

    minus(vector) {
        return new Vector(this._x - vector.x, this._y - vector.y);
    }

    to(vector) {
        return new Vector(vector.x - this._x, vector.y - this._y);
    }

    dividedBy(scalar) {
        return new Vector(this._x / scalar, this._y / scalar);
    }

    get x() {
        return this._x;
    }

    get y() {
        return this._y;
    }
}

export class BoundingBox {
    constructor(bottomLeft, topRight) {
        this._xMin = bottomLeft.x;
        this._yMin = bottomLeft.y;
        this._xMax = topRight.x;
        this._yMax = topRight.y;
    }

    bound(vector) {
        return new Vector(
            this._bound(vector.x, this._xMin, this._xMax),
            this._bound(vector.y, this._yMin, this._yMax)
        );
    }

    intersect(other) {
        const bottomLeft = new Vector(
            Math.max(this.xMin, other.xMin),
            Math.max(this.yMin, other.yMin)
        );
        const topRight = new Vector(
            Math.min(this.xMax, other.xMax),
            Math.min(this.yMax, other.yMax)
        );
        return new BoundingBox(bottomLeft, topRight);
    }

    _bound(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    get xMin() {
        return this._xMin;
    }

    get xMax() {
        return this._xMax;
    }

    get yMin() {
        return this._yMin;
    }

    get yMax() {
        return this._yMax;
    }
}

export const HALF_PLANES = {
    left: new BoundingBox(
        new Vector(Number.NEGATIVE_INFINITY, Number.NEGATIVE_INFINITY),
        new Vector(0, Number.POSITIVE_INFINITY)
    ),
    right: new BoundingBox(
        new Vector(0, Number.NEGATIVE_INFINITY),
        new Vector(Number.POSITIVE_INFINITY, Number.POSITIVE_INFINITY)
    ),
    upper: new BoundingBox(
        new Vector(Number.NEGATIVE_INFINITY, 0),
        new Vector(Number.POSITIVE_INFINITY, Number.POSITIVE_INFINITY)
    ),
    lower: new BoundingBox(
        new Vector(Number.NEGATIVE_INFINITY, Number.NEGATIVE_INFINITY),
        new Vector(Number.POSITIVE_INFINITY, 0)
    )
};
