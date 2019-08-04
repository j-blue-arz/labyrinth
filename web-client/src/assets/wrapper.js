function getHeapArray(type) {
    type = type || "i8";
    if (type.charAt(type.length - 1) === "*") type = "i32"; // pointers are 32-bit
    switch (type) {
        case "i1":
            return HEAP8;
        case "i8":
            return HEAP8;
        case "i16":
            return HEAP16;
        case "i32":
            return HEAP32;
        case "float":
            return HEAPF32;
        case "double":
            return HEAPF64;
        default:
            abort("invalid type for setValue: " + type);
    }
}

function getStructSize(types) {
    let totalSize = 0;
    for (let i = 0; i < types.length; i++) {
        let type = types[i];
        if(type.startsWith("struct") && (type[type.length-1] !== '*')) {
            let binding = bindings[type];
            totalSize += getStructSize(binding.types);
        } else {
            totalSize += getNativeTypeSize(types[i]);
        }
        
    }
    return totalSize;
}

function allocateForStruct(structType) {
    let binding = bindings[structType];
    let ptr = null;
    if (binding) {
        let totalSize = getStructSize(binding.types);
        ptr = _malloc(totalSize);
    }
    return ptr;
}

function structToObject(ptr, structType) {
    let binding = bindings[structType];
    let constructorArgs = [];
    let cur = ptr;
    for (let i = 0; i < binding.types.length; i++) {
        let curType = binding.types[i];
        if(curType.startsWith("struct")) {
            constructorArgs.push(structToObject(cur, curType))
            cur += getStructSize(bindings[curType].types);
        } else {
            constructorArgs.push(getValue(cur, curType));
            cur += getNativeTypeSize(curType);
        }
    }
    let result = binding.jsConstructor.apply(null, constructorArgs);
    return result;
}

function objectToCStruct(object, structType) {
    let ptr = allocateForStruct(structType);
    if (ptr !== null) {
        let binding = bindings[structType];
        setStruct(ptr, object, binding);
    }
    return ptr;
}

function isStruct(type) {
    return type.startsWith("struct") && (type[type.length-1] !== '*');
}

function setStruct(ptr, object, binding) {
    let cur = ptr;
    for (let i = 0; i < binding.types.length; i++) {
        let curType = binding.types[i];
        let value = binding.memberGetters[i](object);
        if(isStruct(curType)) {
            let binding = bindings[curType];
            if(binding) {
                cur = setStruct(cur, value, binding)
            }
        } else {
            if (curType[curType.length-1] === '*') {
                let pointer = pointerTypeToCPointer(value, curType);
                if(pointer) {
                    value = pointer;
                }
            }
            setValue(cur, value, curType);
            cur += getNativeTypeSize(curType);
        }
    }
    return cur;
}

function pointerTypeToCPointer(value, pointerType) {
    let pointer = null;
    let type = pointerType.substr(0, pointerType.length-1);
    if(Array.isArray(value)) {
        pointer = arrayToCArray(value, type)
    } else {
        if(type.startsWith("struct")) {
            pointer = objectToCStruct(value, type);
        }
    }
    return pointer;
}

function arrayToCArray(array, type) {
    let ptr = null;
    if(type.startsWith("struct")) {
        let binding = bindings[type];
        if (binding) {
            let structSize = getStructSize(binding.types);
            ptr = _malloc(array.length * structSize);
            let cur = ptr;
            for(object of array) {
                cur = setStruct(cur, object, binding);
            }
        }
    } else {
        let nativeSize = getNativeTypeSize(type);
        ptr = _malloc(array.length * nativeSize);
        let correctedAddress = (ptr / nativeSize) | 0;
        getHeapArray(type).set(array, correctedAddress);
    }
    return ptr;
}

function callC(ident, returnType, argTypes, args) {
    let params = [];
    let returnPtr = null;
    let argPtrs = [];
    let func = getCFunc(ident);

    try {
        if (returnType.startsWith("struct")) {
            returnPtr = allocateForStruct(returnType);
            if (returnPtr !== null) {
                params.push(returnPtr);
            }
        }

        for (var i = 0; i < args.length; i++) {
            let type = argTypes[i];
            let value = args[i];
            if(isStruct(type)) {
                type += "*";
            }
            if (type[type.length-1] === '*') {
                let ptr = pointerTypeToCPointer(value, type);
                if (ptr) {
                    argPtrs.push(ptr);
                    value = ptr;
                }
                
            }
            params.push(value);
        }

        let result = func.apply(null, params);

        if (returnPtr) {
            result = structToObject(returnPtr, returnType);
            Module._free(returnPtr);
            returnPtr = null;
        }

        return result;
    } finally {
        if (argPtrs) {
            argPtrs.forEach(argPtr => Module._free(argPtr));
        }

        if (returnPtr) {
            Module._free(returnPtr);
        }
    }
}
