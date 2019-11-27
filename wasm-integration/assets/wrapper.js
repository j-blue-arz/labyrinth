var err = (typeof console !== "undefined" && console.warn.bind(console)) || null;

const WASM_PAGE_SIZE = 64 * 1024;
const DEFAULT_TOTAL_MEMORY = 64 * 1024 * 1024; // 64 MB
const DEFAULT_TOTAL_STACK = 5 * 1024 * 1024;

class WasmMemory {
    setMemory(memory) {
        console.log("setMemory called");
        this.memory = memory;
        this.updateBuffer();
    }

    updateBuffer() {
        console.log("updateBuffer called");
        let buffer = this.memory.buffer;
        this._heap8 = new Int8Array(buffer);
        this._heapU8 = new Uint8Array(buffer);
        this._heap16 = new Int16Array(buffer);
        this._heap32 = new Int32Array(buffer);
        this._heapF32 = new Float32Array(buffer);
        this._heapF64 = new Float64Array(buffer);
    }

    setValue(ptr, value, type) {
        type = type || "i8";
        if (type.charAt(type.length - 1) === "*") type = "i32"; // pointers are 32-bit
        switch (type) {
            case "i8":
                this._heap8[ptr >> 0] = value;
                break;
            case "i16":
                this._heap16[ptr >> 1] = value;
                break;
            case "i32":
                this._heap32[ptr >> 2] = value;
                break;
            case "float":
                this._heapF32[ptr >> 2] = value;
                break;
            case "double":
                this._heapF64[ptr >> 3] = value;
                break;
            default:
                err("invalid type for setValue: " + type);
        }
    }

    getValue(ptr, type) {
        type = type || "i8";
        if (type.charAt(type.length - 1) === "*") type = "i32"; // pointers are 32-bit
        switch (type) {
            case "i8":
                return this._heap8[ptr >> 0];
            case "i16":
                return this._heap16[ptr >> 1];
            case "i32":
                return this._heap32[ptr >> 2];
            case "float":
                return this._heapF32[ptr >> 2];
            case "double":
                return this._heapF64[ptr >> 3];
            default:
                err("invalid type for getValue: " + type);
        }
        return null;
    }

    sbrk(increment) {
        const oldDynamicTop = this.dynamicTop;
        this.dynamicTop += increment;
        console.log(oldDynamicTop + " + " + increment + " = " + this.dynamicTop);
        return oldDynamicTop;
    }
    
    memcpy_big(dest, src, num) {
        console.log("called memcpy_big with " + dest + ", " + src + ", " + num);
        this._heapU8.set(this._heapU8.subarray(src, src+num), dest);
    }


    setArray(ptr, array, type) {
        type = type || "i8";
        if (type.charAt(type.length - 1) === "*") type = "i32"; // pointers are 32-bit
        switch (type) {
            case "i8":
                this._heap8.set(array, ptr >> 0);
            case "i16":
                this._heap16.set(array, ptr >> 1);
            case "i32":
                this._heap32.set(array, ptr >> 2);
            case "float":
                this._heapF32.set(array, ptr >> 2);
            case "double":
                this._heapF64.set(array, ptr >> 3);
            default:
                err("invalid type for setValue: " + type);
        }
    }
}

class WasmWrapper {
    constructor(wasmInstance, wasmMemory) {
        this.bindings = {};
        this.instance = wasmInstance;
        this.wasmMemory = wasmMemory;
        this._malloc = wasmInstance.exports.malloc;
        this._free = wasmInstance.exports.free;
    }

    _getNativeTypeSize(type) {
        switch (type) {
            case "i8":
                return 1;
            case "i16":
                return 2;
            case "i32":
                return 4;
            case "i64":
                return 8;
            case "float":
                return 4;
            case "double":
                return 8;
            default: {
                if (type[type.length - 1] === "*") {
                    return 4; // A pointer
                } else {
                    return 0;
                }
            }
        }
    }

    _getStructSize(binding) {
        let types = binding.types;
        let totalSize = 0;
        for (let i = 0; i < types.length; i++) {
            let type = types[i];
            if (type.startsWith("struct") && type[type.length - 1] !== "*") {
                let binding = this.bindings[type];
                totalSize += this._getStructSize(binding);
            } else {
                totalSize += this._getNativeTypeSize(types[i]);
            }
        }
        return totalSize;
    }

    _allocateForStruct(structType) {
        let binding = this.bindings[structType];
        let ptr = null;
        if (binding) {
            let totalSize = this._getStructSize(binding);
            ptr = this._malloc(totalSize);
        }
        return ptr;
    }

    _structToObject(ptr, structType) {
        let binding = this.bindings[structType];
        let constructorArgs = [];
        let cur = ptr;
        for (let i = 0; i < binding.types.length; i++) {
            let curType = binding.types[i];
            if (curType.startsWith("struct")) {
                constructorArgs.push(this._structToObject(cur, curType));
                cur += this._getStructSize(this.bindings[curType]);
            } else {
                constructorArgs.push(this.wasmMemory.getValue(cur, curType));
                cur += this._getNativeTypeSize(curType);
            }
        }
        if(binding.jsConstructor) {
            return binding.jsConstructor.apply(null, constructorArgs);
        } else {
            return constructorArgs;
        }
    }

    _objectToCStruct(object, structType) {
        let ptr = this._allocateForStruct(structType);
        if (ptr !== null) {
            let binding = this.bindings[structType];
            this._setStruct(ptr, object, binding);
        }
        return ptr;
    }

    _isStruct(type) {
        return type.startsWith("struct") && type[type.length - 1] !== "*";
    }

    _setStruct(ptr, object, binding) {
        let cur = ptr;
        if(binding.memberGetters && binding.memberGetters.length === binding.types.length) {
            for (let i = 0; i < binding.types.length; i++) {
                let curType = binding.types[i];
                let value = binding.memberGetters[i](object);
                if (this._isStruct(curType)) {
                    let binding = this.bindings[curType];
                    if (binding) {
                        cur = this._setStruct(cur, value, binding);
                    }
                } else {
                    if (curType[curType.length - 1] === "*") {
                        let pointer = this._pointerTypeToCPointer(value, curType);
                        if (pointer) {
                            value = pointer;
                        }
                    }
                    this.wasmMemory.setValue(cur, value, curType);
                    cur += this._getNativeTypeSize(curType);
                }
            }
        }
        return cur;
    }

    _pointerTypeToCPointer(value, pointerType) {
        let pointer = null;
        let type = pointerType.substr(0, pointerType.length - 1);
        if (Array.isArray(value)) {
            pointer = this._arrayToCArray(value, type);
        } else {
            if (type.startsWith("struct")) {
                pointer = this._objectToCStruct(value, type);
            }
        }
        return pointer;
    }

    _arrayToCArray(array, type) {
        let ptr = null;
        if (type.startsWith("struct")) {
            let binding = this.bindings[type];
            if (binding) {
                let structSize = this._getStructSize(binding);
                ptr = this._malloc(array.length * structSize);
                let cur = ptr;
                for (let object of array) {
                    cur = this._setStruct(cur, object, binding);
                }
            }
        } else {
            let nativeSize = this._getNativeTypeSize(type);
            ptr = this._malloc(array.length * nativeSize);
            this.wasmMemory.setArray(ptr, array, type);
        }
        return ptr;
    }

    _callC(ident, returnType, argTypes, args) {
        let params = [];
        let returnPtr = null;
        let argPtrs = [];
        let func = this.instance.exports[ident];

        try {
            if (returnType.startsWith("struct")) {
                returnPtr = this._allocateForStruct(returnType);
                if (returnPtr !== null) {
                    params.push(returnPtr);
                }
            }

            for (let i = 0; i < args.length; i++) {
                let type = argTypes[i];
                let value = args[i];
                if (this._isStruct(type)) {
                    type += "*";
                }
                if (type[type.length - 1] === "*") {
                    let ptr = this._pointerTypeToCPointer(value, type);
                    if (ptr) {
                        argPtrs.push(ptr);
                        value = ptr;
                    }
                }
                params.push(value);
            }

            let result = func.apply(null, params);

            if (returnPtr) {
                result = this._structToObject(returnPtr, returnType);
                this._free(returnPtr);
                returnPtr = null;
            }

            return result;
        } finally {
            if (argPtrs) {
                argPtrs.forEach(argPtr => this._free(argPtr));
            }

            if (returnPtr) {
                this._free(returnPtr);
            }
        }
    }
}

export { WasmMemory, WasmWrapper };
