export function hasPropertyWithType(obj, prop, type) {
    return obj.hasOwnProperty(prop) && typeof obj[prop] === type;
}

export function hasPropertyWithFunction(obj, prop, funct) {
    return obj.hasOwnProperty(prop) && typeof obj[prop][funct] === "function";
}
