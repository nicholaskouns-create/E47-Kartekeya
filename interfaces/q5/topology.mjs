// Q5 browser/runtime topology grammar.
// Mirrors q5.ts without TypeScript syntax so the live Pages cube can execute it directly.
// No new operator: this is only the 5×5×5 packing and adjacency map.

export const RADIX = 5;
export const DIM = RADIX ** 3;
export const TOPOLOGIES = Object.freeze(["cube", "torus"]);
export const AXES = Object.freeze(["x", "y", "z"]);

export function pi(x, y, z) {
  if (![x, y, z].every((v) => Number.isInteger(v) && v >= 0 && v < RADIX)) {
    throw new RangeError("Q5 coordinates must lie in {0,1,2,3,4}");
  }
  return (x * RADIX + y) * RADIX + z;
}

export function unpi(i) {
  if (!Number.isInteger(i) || i < 0 || i >= DIM) {
    throw new RangeError("Q5 index must lie in {0,...,124}");
  }
  const z = i % RADIX;
  const y = Math.floor(i / RADIX) % RADIX;
  const x = Math.floor(i / (RADIX * RADIX));
  return [x, y, z];
}

export function wordOf(x, y, z) {
  pi(x, y, z);
  return String(x) + String(y) + String(z);
}

function onBound(c) {
  return c === 0 || c === RADIX - 1;
}

function roleOf(x, y, z) {
  const n = Number(onBound(x)) + Number(onBound(y)) + Number(onBound(z));
  if (n === 3) return "corner";
  if (n === 2) return "edge";
  if (n === 1) return "face";
  return "core";
}

function cubeDegree(x, y, z) {
  let d = 0;
  for (const c of [x, y, z]) {
    if (c > 0) d += 1;
    if (c < RADIX - 1) d += 1;
  }
  return d;
}

export const CELLS = Object.freeze(Array.from({ length: DIM }, (_, i) => {
  const [x, y, z] = unpi(i);
  return Object.freeze({
    i,
    x,
    y,
    z,
    word: wordOf(x, y, z),
    m: Object.freeze([x - 2, y - 2, z - 2]),
    role: roleOf(x, y, z),
    cubeDegree: cubeDegree(x, y, z)
  });
}));

export function neighbors(cell, topology = "cube") {
  if (!TOPOLOGIES.includes(topology)) throw new RangeError("topology must be cube or torus");
  const out = [];
  for (const axis of AXES) {
    for (const dir of [-1, 1]) {
      let next = cell[axis] + dir;
      if (topology === "torus") {
        next = ((next % RADIX) + RADIX) % RADIX;
      } else if (next < 0 || next >= RADIX) {
        continue;
      }
      const x = axis === "x" ? next : cell.x;
      const y = axis === "y" ? next : cell.y;
      const z = axis === "z" ? next : cell.z;
      out.push(Object.freeze({ i: pi(x, y, z), axis, dir }));
    }
  }
  return out;
}

export function stepAxis(cell, axis, dir, wrap = false) {
  if (!AXES.includes(axis)) throw new RangeError("axis must be x, y or z");
  if (dir !== -1 && dir !== 1) throw new RangeError("dir must be -1 or 1");
  let next = cell[axis] + dir;
  if (wrap) next = ((next % RADIX) + RADIX) % RADIX;
  else if (next < 0 || next >= RADIX) return cell.i;
  const x = axis === "x" ? next : cell.x;
  const y = axis === "y" ? next : cell.y;
  const z = axis === "z" ? next : cell.z;
  return pi(x, y, z);
}

export function sliceCells(axis = "all", value = 0) {
  if (axis === "all") return CELLS.slice();
  if (!AXES.includes(axis)) throw new RangeError("slice axis must be all, x, y or z");
  if (!Number.isInteger(value) || value < 0 || value >= RADIX) {
    throw new RangeError("slice value must lie in {0,1,2,3,4}");
  }
  return CELLS.filter((c) => c[axis] === value);
}

export function nextIndex(i) {
  return (i + 1) % DIM;
}
