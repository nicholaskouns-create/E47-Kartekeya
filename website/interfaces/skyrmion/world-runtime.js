export const SKYRMION_WORLD_RUNTIME={
  schema:"SKYRMION-WORLD-RUNTIME-1.0",
  maplibreVersion:"6.10.0",
  mapStyle:"https://demotiles.maplibre.org/globe.json",
  terrainTiles:"https://demotiles.maplibre.org/terrain-tiles/tiles.json",
  defaultSpawn:{lng:-115.1398,lat:36.1699,altitudeM:3600},
  domains:["flight","scalar","wave","matrix","cube","e47","aetheris"],
  fixedStepHz:60,
  graphics:{preferred:"webgpu",fallback:["webgl2","webgl1"],adaptiveDpr:true,terrainLod:true},
  evidenceBoundary:"World and map data drive rendering and navigation. Experimental propulsion remains simulation-only."
};