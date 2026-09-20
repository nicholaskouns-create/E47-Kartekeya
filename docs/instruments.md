# Instrument directory

[Repository home](../README.md) · [Documentation](README.md) · [Open the City](https://nicholaskouns-create.github.io/E47-Kartekeya/)

Start with **[EIDOLON flight](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight)**. Every interface below also has its own direct route.

This directory maps the browser interfaces present in the repository. A route identifies the interface and its source; external-service availability and browser rendering are separate runtime checks.

## Flight and propulsion

| Open | What it contains | Source |
|---|---|---|
| [MANTA](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manta/) | Morphing aircraft and fixed-baseline simulation | [manta/](../website/interfaces/manta/) |
| [MANTA Daylight](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manta-daylight/) | Companion daylight flight view | [manta-daylight/](../website/interfaces/manta-daylight/) |
| [SKYRMION](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/skyrmion/) | WGS84 flight simulator with conventional and experimental models | [skyrmion/](../website/interfaces/skyrmion/) |
| [Syntax Jacob](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/syntax-jacob/) | 3I/ATLAS trajectory and propulsion lab | [syntax-jacob/](../website/interfaces/syntax-jacob/) |
| [UFO Propulsion](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/flight/ufo-propulsion/) | Native propulsion simulation interface | [ufo-propulsion/](../website/interfaces/flight/ufo-propulsion/) |
| [Propulsion Atlas](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/propulsion/) | Directory of propulsion apps and locations | [propulsion/](../website/interfaces/propulsion/) |

## Quantum, spectral, and graphics instruments

| Open | What it contains | Source |
|---|---|---|
| [CITY CORE](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight) | Instrument navigation and EIDOLON entry | [kouns-core/](../website/interfaces/kouns-core/) |
| [THE MATRIX](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/) | Quantum circuit, statevector, and matrix-product-state tools | [matrix/](../website/interfaces/matrix/) |
| [CITY 125](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/city-125/) | 125-state visual debugger | [city-125/](../website/interfaces/city-125/) |
| [THE CUBE](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/cube-platform/) | Modular Cube platform interface | [cube-platform/](../website/interfaces/cube-platform/) |
| [Visualizers](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/visualizers/) | Portal for independent research visualizers | [visualizers/](../website/interfaces/visualizers/) |
| [WebGL Lab](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/webgl/) | Browser graphics instrument | [webgl/](../website/interfaces/webgl/) |

## Flight shells and companion routes

These routes retain the existing linked or embedded applications and receipt bindings.

| Open | What it contains | Source |
|---|---|---|
| [EIDOLON](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/flight/eidolon/) | EIDOLON flight shell | [eidolon/](../website/interfaces/flight/eidolon/) |
| [EIDOLON Flight Lab](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/eidolon-flight-lab/) | Companion shell embedding the EIDOLON route | [eidolon-flight-lab/](../website/interfaces/eidolon-flight-lab/) |
| [Eidolon Harmonic](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/flight/eidolon-harmonic/) | Harmonic flight shell | [eidolon-harmonic/](../website/interfaces/flight/eidolon-harmonic/) |
| [HOVER Assembly](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/flight/hover-assembly/) | Assembly interface shell | [hover-assembly/](../website/interfaces/flight/hover-assembly/) |
| [HOVER Cockpit](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/flight/hover-cockpit/) | Cockpit interface shell | [hover-cockpit/](../website/interfaces/flight/hover-cockpit/) |
| [MAV](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/flight/mav/) | MAV console shell | [mav/](../website/interfaces/flight/mav/) |

## Existing worker interface

| Open | What it contains | Source |
|---|---|---|
| [External Agents](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/external-agents/) | Five-worker integration and status interface | [Browser source](../website/interfaces/external-agents/) · [Worker contract](../city/external-agents/README.md) |

## Code behind the interfaces

[E47 Python core](../src/e47/) · [AETHERIS](../src/aetheris/) · [MANTA Python model](../src/manta/) · [Shared graphics](../web/README.md) · [Shared world engine](../website/interfaces/shared/world-engine/) · [Component manifest](../lab-manifest.json)
