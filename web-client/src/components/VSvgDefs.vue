<template>
    <defs>
        <filter
            id="drop-shadow"
            x="-50%"
            y="-50%"
            width="200%"
            height="200%"
            filterUnits="userSpaceOnUse"
        >
            <feGaussianBlur result="shadowBlur" in="SourceAlpha" stdDeviation="5" />
            <feOffset result="shadow" in="shadowBlur" dx="6" dy="6" />
            <feFlood flood-color="#000000" />
            <feComposite in2="shadow" operator="in" />
            <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
        <filter id="plasticity" x="0" y="0" width="150%" height="150%" filterUnits="userSpaceOnUse">
            <feGaussianBlur result="blur" in="SourceAlpha" stdDeviation="3" />
            <feSpecularLighting
                surfaceScale="2"
                specularConstant="0.6"
                specularExponent="7"
                lighting-color="white"
                in="blur"
                result="light"
            >
                <fePointLight x="-400" y="-400" z="200" />
            </feSpecularLighting>
            <feComposite operator="in" in="light" in2="SourceAlpha" result="insideLight" />
            <feGaussianBlur result="shadowBlur" in="SourceAlpha" stdDeviation="5" />
            <feOffset result="shadow" in="shadowBlur" dx="6" dy="6" />
            <feMerge>
                <feMergeNode in="SourceGraphic" />
                <feMergeNode in="shadow" />
                <feMergeNode in="insideLight" />
            </feMerge>
        </filter>
    </defs>
</template>
