<template>
    <defs>
        <filter id="plasticity" x="0" y="0" width="150%" height="150%" filterUnits="userSpaceOnUse">
            <feGaussianBlur result="blur" in="SourceAlpha" stdDeviation="2"/>
            <feSpecularLighting
                surfaceScale="2"
                specularConstant="0.7"
                specularExponent="3"
                lighting-color="white"
                in="blur"
                result="light"
            >
                <fePointLight x="-400" y="-400" z="500"/>
            </feSpecularLighting>
            <feComposite operator="in" in="light" in2="SourceAlpha" result="insideLight"/>
            <feGaussianBlur result="shadowBlur" in="SourceAlpha" stdDeviation="5"/>
            <feOffset result="shadow" in="shadowBlur" dx="6" dy="6"/>
            <feMerge>
                <feMergeNode in="SourceGraphic"/>
                <feMergeNode in="shadow"/>
                <feMergeNode in="insideLight"/>
            </feMerge>
        </filter>
    </defs>
</template>
