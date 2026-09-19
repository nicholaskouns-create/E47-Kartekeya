export const SKYRMION_WORLD_RUNTIME=Object.freeze({
 schema:"SKYRMION-WORLD-RUNTIME-2.0",
 runtime:"SKYRMION-RUNTIME-2.0",
 pipeline:["World Engine","6DOF Physics","Vehicle Registry","Propulsion Registry","E47 Runtime","GPU Renderer","Mission/Replays","Proof + Telemetry"],
 maplibreVersion:"6.10.0",mapStyle:"https://demotiles.maplibre.org/globe.json",terrainTiles:"https://demotiles.maplibre.org/terrain-tiles/tiles.json",
 defaultSpawn:{lng:-115.1398,lat:36.1699,altitudeM:3600},fixedStepHz:120,
 vehicles:{conventional:["F-16","SR-71","X-15"],experimentalSimulation:["EIDOLON","MANTA","SKYRMION","SYNTAX JACOB"]},
 graphics:{preferred:"webgpu",fallback:["webgl2","webgl1"],adaptiveDpr:true,terrainLod:true},
 e47:{carrierDimension:125,kernelDimension:47,omegaC:47/125,epsilon:1/99144},
 evidenceBoundary:"Conventional aircraft use aerodynamic 6DOF models. EIDOLON, MANTA, SKYRMION and Syntax Jacob are explicitly separated experimental simulation adapters; no experimental propulsion claim is implied by runtime behavior."
});
