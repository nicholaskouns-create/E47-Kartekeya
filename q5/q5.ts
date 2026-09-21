/** Q5 packing map. Isomorphic to codec.py.

No new operator. π(x,y,z) = 25x + 5y + z.
Σ = {0,1,2,3,4}³. |Σ| = 125. Word = xyz as quinary digits.
Not identified with ker K.
*/

export const RADIX = 5;
export const DIM = 125;
export const KERNEL = 47;
export const COMPLEMENT = 78;

export type Role = "core" | "face" | "edge" | "corner";
export type Axis = "x" | "y" | "z";
export type Topology = "cube" | "torus";

export type Cell = {
  i: number;
  x: number;
  y: number;
  z: number;
  word: string;
  m: [number, number, number];
  role: Role;
  bounds: 0 | 1 | 2 | 3;
  cubeDegree: number;
};

export type Neighbor = {
  i: number;
  axis: Axis;
  dir: -1 | 1;
};

export function pi(x: number, y: number, z: number): number {
  return (x * RADIX + y) * RADIX + z;
}

export function unpi(i: number): [number, number, number] {
  const z = i % RADIX;
  const y = Math.floor(i / RADIX) % RADIX;
  const x = Math.floor(i / (RADIX * RADIX));
  return [x, y, z];
}

export function wordOf(x: number, y: number, z: number): string {
  return `${x}${y}${z}`;
}

function onBound(c: number): boolean {
  return c === 0 || c === RADIX - 1;
}

function roleOf(x: number, y: number, z: number): Role {
  const n = Number(onBound(x)) + Number(onBound(y)) + Number(onBound(z));
  if (n === 3) return "corner";
  if (n === 2) return "edge";
  if (n === 1) return "face";
  return "core";
}

function cubeDegree(x: number, y: number, z: number): number {
  let d = 0;
  for (const c of [x, y, z]) {
    if (c > 0) d += 1;
    if (c < RADIX - 1) d += 1;
  }
  return d;
}

export const CELLS: Cell[] = Array.from({ length: DIM }, (_, i) => {
  const [x, y, z] = unpi(i);
  const bounds = (Number(onBound(x)) +
    Number(onBound(y)) +
    Number(onBound(z))) as 0 | 1 | 2 | 3;
  return {
    i,
    x,
    y,
    z,
    word: wordOf(x, y, z),
    m: [x - 2, y - 2, z - 2],
    role: roleOf(x, y, z),
    bounds,
    cubeDegree: cubeDegree(x, y, z),
  };
});

export const BY_INDEX: Cell[] = CELLS;

export const CENTER = CELLS[pi(2, 2, 2)]!;
export const WORD_47 = CELLS[47]!;
export const WORD_78 = CELLS[78]!;

export const ROLE_COUNTS: Record<Role, number> = {
  core: CELLS.filter((c) => c.role === "core").length,
  face: CELLS.filter((c) => c.role === "face").length,
  edge: CELLS.filter((c) => c.role === "edge").length,
  corner: CELLS.filter((c) => c.role === "corner").length,
};

export function neighbors(cell: Cell, topology: Topology): Neighbor[] {
  const out: Neighbor[] = [];
  const axes: Axis[] = ["x", "y", "z"];
  for (const axis of axes) {
    for (const dir of [-1, 1] as const) {
      let next = cell[axis] + dir;
      if (topology === "torus") {
        next = ((next % RADIX) + RADIX) % RADIX;
      } else if (next < 0 || next >= RADIX) {
        continue;
      }
      const x = axis === "x" ? next : cell.x;
      const y = axis === "y" ? next : cell.y;
      const z = axis === "z" ? next : cell.z;
      out.push({ i: pi(x, y, z), axis, dir });
    }
  }
  return out;
}

export function sliceCells(axis: Axis | "all", value: number): Cell[] {
  if (axis === "all") return CELLS;
  return CELLS.filter((c) => c[axis] === value);
}

export function nextIndex(i: number): number {
  return (i + 1) % DIM;
}

export function stepAxis(
  cell: Cell,
  axis: Axis,
  dir: -1 | 1,
  wrap: boolean,
): number {
  let next = cell[axis] + dir;
  if (wrap) next = ((next % RADIX) + RADIX) % RADIX;
  else if (next < 0 || next >= RADIX) return cell.i;
  const x = axis === "x" ? next : cell.x;
  const y = axis === "y" ? next : cell.y;
  const z = axis === "z" ? next : cell.z;
  return pi(x, y, z);
}

export const INVARIANTS = {
  omega: "47/125",
  omegaQuinary: "0.142₅",
  epsStar: "1/99144",
  rhoStar: "15/17",
  k2Gap: "11664",
  k2Max: "186624",
  cubeFrob: "8√3",
  cubeSpec: "2√2",
  word47: "142",
  word78: "303",
  packing: "π(x,y,z) = 25x + 5y + z",
} as const;
