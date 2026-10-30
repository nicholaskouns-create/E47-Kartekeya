import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import {
  detectCityGraphicsCapabilities,
  createAdaptiveFrameController,
} from "../../js/city_graphics_accelerator.js";

const canvas = document.getElementById("stage");
const gpuEl = document.getElementById("gpu");
const drawsEl = document.getElementById("draws");
const fpsEl = document.getElementById("fps");
const dprEl = document.getElementById("dpr");
const dock = document.getElementById("dock");

const N = 5;
const COUNT = N * N * N; // 125
const KERNEL = 47;
const tmp = new THREE.Object3D();
const color = new THREE.Color();

const TECHNIQUES = [
  { id: "instancing", label: "INSTANCING", on: true },
  { id: "adaptive", label: "ADAPTIVE DPR", on: true },
  { id: "shadows", label: "SHADOWS", on: false },
  { id: "lod", label: "LOD", on: true },
  { id: "tone", label: "ACES TONE", on: true },
  { id: "fog", label: "EXP FOG", on: true },
  { id: "kernel", label: "KERNEL LIT", on: true },
  { id: "fixed", label: "FIXED STEP", on: true },
];

const state = Object.fromEntries(TECHNIQUES.map((t) => [t.id, t.on]));

const KERNEL_SITES = (() => {
  const scored = [];
  for (let i = 0; i < COUNT; i++) {
    const x = i % N;
    const y = Math.floor(i / N) % N;
    const z = Math.floor(i / (N * N));
    scored.push([x * x + y * y + z * z, i]);
  }
  scored.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return new Set(scored.slice(0, KERNEL).map((x) => x[1]));
})();

function isKernel(i) {
  return KERNEL_SITES.has(i);
}

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: "high-performance",
  alpha: false,
});
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = false;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0x07090b, 1);
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x07090b, 0.045);

const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 80);
camera.position.set(9.4, 6.2, 11.2);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.target.set(0, 0, 0);

scene.add(new THREE.AmbientLight(0x6a7c80, 0.7));
const key = new THREE.DirectionalLight(0xcfe8e4, 1.35);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
key.position.set(6, 10, 4);
scene.add(key);
fill.position.set(-8, -2, -6);
scene.add(fill);
const ground = new THREE.Mesh(
  new THREE.CircleGeometry(18, 48),
  new THREE.MeshStandardMaterial({ color: 0x0b1012, roughness: 1, metalness: 0 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -4.2;
ground.receiveShadow = true;
scene.add(ground);

const geoHi = new THREE.OctahedronGeometry(0.38, 0);
const geoLo = new THREE.OctahedronGeometry(0.38, 0);
geoLo.scale(0.72, 0.72, 0.72);

const matKernel = new THREE.MeshStandardMaterial({
  color: 0x63d7cf,
  emissive: 0x163a38,
  roughness: 0.28,
  metalness: 0.18,
});
const matRest = new THREE.MeshStandardMaterial({
  color: 0x243033,
  emissive: 0x050708,
  roughness: 0.82,
  metalness: 0.04,
  transparent: true,
  opacity: 0.55,
});

let instKernel, instRest, naive = [];

function place(i, mesh) {
  const x = i % N;
  const y = Math.floor(i / N) % N;
  const z = Math.floor(i / (N * N));
  mesh.position.set((x - 2) * 1.15, (y - 2) * 1.15, (z - 2) * 1.15);
}

function rebuild() {
  if (instKernel) {
    scene.remove(instKernel);
    instKernel.geometry.dispose();
  }
  if (instRest) {
    scene.remove(instRest);
    instRest.geometry.dispose();
  }
  for (const m of naive) {
    scene.remove(m);
    m.geometry.dispose();
  }
  naive = [];

  const geo = state.lod && camera.position.length() > 16 ? geoLo : geoHi;
  let k = 0;
  let r = 0;
  const kIndex = [];
  const rIndex = [];
  for (let i = 0; i < COUNT; i++) {
    if (state.kernel && isKernel(i)) kIndex.push(i);
    else rIndex.push(i);
  }

  if (state.instancing) {
    instKernel = new THREE.InstancedMesh(geo, matKernel, Math.max(1, kIndex.length));
    instRest = new THREE.InstancedMesh(geo, matRest, Math.max(1, rIndex.length));
    instKernel.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    instRest.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    kIndex.forEach((i, n) => {
      place(i, tmp);
      tmp.updateMatrix();
      instKernel.setMatrixAt(n, tmp.matrix);
    });
    rIndex.forEach((i, n) => {
      place(i, tmp);
      tmp.updateMatrix();
      instRest.setMatrixAt(n, tmp.matrix);
    });
    instKernel.count = kIndex.length;
    instRest.count = rIndex.length;
    instKernel.castShadow = instRest.castShadow = true;
    instKernel.receiveShadow = instRest.receiveShadow = true;
    scene.add(instKernel, instRest);
  } else {
    for (const i of kIndex) {
      const m = new THREE.Mesh(geo, matKernel);
      place(i, m);
      scene.add(m);
      naive.push(m);
    }
    for (const i of rIndex) {
      const m = new THREE.Mesh(geo, matRest);
      place(i, m);
      scene.add(m);
      naive.push(m);
    }
  }
  void k;
  void r;
}

const adapter = createAdaptiveFrameController({ targetFps: 60, dprCap: 2 });

function resize() {
  const w = canvas.clientWidth || innerWidth;
  const h = canvas.clientHeight || innerHeight;
  camera.aspect = w / Math.max(1, h);
  camera.updateProjectionMatrix();
  const dpr = state.adaptive
    ? adapter.pixelRatio()
    : Math.min(devicePixelRatio || 1, 2);
  renderer.setPixelRatio(dpr);
  renderer.setSize(w, h, false);
  dprEl.textContent = dpr.toFixed(2);
}

addEventListener("resize", resize);
document.addEventListener("visibilitychange", () => {
  if (document.hidden) renderer.setAnimationLoop(null);
  else renderer.setAnimationLoop(tick);
});

TECHNIQUES.forEach((t) => {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = t.label;
  b.className = t.on ? "on" : "";
  b.addEventListener("click", () => {
    state[t.id] = !state[t.id];
    b.classList.toggle("on", state[t.id]);
    if (t.id === "shadows") {
      renderer.shadowMap.enabled = state.shadows;
      matKernel.needsUpdate = true;
    }
    if (t.id === "tone") {
      renderer.toneMapping = state.tone ? THREE.ACESFilmicToneMapping : THREE.NoToneMapping;
    }
    if (t.id === "fog") {
      scene.fog = state.fog ? new THREE.FogExp2(0x07090b, 0.045) : null;
    }
    rebuild();
    resize();
  });
  dock.appendChild(b);
});

let acc = 0;
let last = performance.now();
let frames = 0;
let fpsT = 0;
const FIXED = 1 / 60;
let spin = 0;

function tick(now) {
  const raw = Math.min(0.1, (now - last) / 1000);
  last = now;
  adapter.sample(now);
  if (state.adaptive && frames % 12 === 0) resize();

  if (state.fixed) {
    acc += raw;
    while (acc >= FIXED) {
      spin += FIXED * 0.18;
      acc -= FIXED;
    }
  } else {
    spin += raw * 0.18;
  }

  if (instKernel) instKernel.rotation.y = spin;
  if (instRest) instRest.rotation.y = spin * 0.35;
  scene.rotation.y = state.instancing ? 0 : spin * 0.15;

  controls.update();
  renderer.render(scene, camera);

  frames += 1;
  fpsT += raw;
  if (fpsT >= 0.4) {
    fpsEl.textContent = String(Math.round(frames / fpsT));
    drawsEl.textContent = String(renderer.info.render.calls);
    frames = 0;
    fpsT = 0;
  }
}

rebuild();
resize();
renderer.setAnimationLoop(tick);

detectCityGraphicsCapabilities().then((cap) => {
  gpuEl.textContent = `GPU · ${String(cap.backend || "webgl").toUpperCase()} · ${String(cap.tier || "")}`;
}).catch(() => {
  gpuEl.textContent = "GPU · WEBGL";
});

console.info("WEBGL LAB · kernel display sites", KERNEL_SITES.size, "/ 125 (visual selection, not ker K)");
