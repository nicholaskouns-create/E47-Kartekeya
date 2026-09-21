/** Q5 ledger bind. GitHub JSONL row + Notion slot + Pages cube.

No wrapping layer. Certificates become rows later.
*/

import { CELLS, type Cell, type Role } from "./q5";
import slots from "./slots.json";

export const GITHUB_REPO = "nicholaskouns-create/E47-Kartekeya";
export const GITHUB_Q5 = `https://github.com/${GITHUB_REPO}/blob/main/q5`;
export const PAGES_CUBE =
  "https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/";
export const NOTION_CITY =
  "https://www.notion.so/0b778ea1fbe04d20b7b3e998abd4ca76";
export const NOTION_KARTEKEYA =
  "https://www.notion.so/3a446094fd3081d0b1eddeecff16aa71";
export const NOTION_Q5_HUB =
  "https://www.notion.so/3e246094fd308151966ae74dedb2976a";
export const NOTION_Q5_DB =
  "https://www.notion.so/3807a3510c28401fa2924610628093b8";

type Word = keyof typeof slots;

export type LedgerRecord = {
  i: number;
  x: number;
  y: number;
  z: number;
  word: string;
  m: [number, number, number];
  role: Role;
  title: string;
  blurb: string;
  github: {
    cell: string;
    map: string;
    codec: string;
    validator: string;
    host: string;
    pages: string;
  };
  notion: {
    href: string;
    label: string;
  };
};

function titleOf(cell: Cell): string {
  if (cell.i === 47) return "Ω_c index · 47 = 142₅";
  if (cell.i === 78) return "Complement index · 78 = 303₅";
  if (cell.i === 62) return "Magnetic origin";
  if (cell.word === "000") return "Minimum corner";
  if (cell.word === "444") return "Maximum corner";
  if (cell.role === "corner") return "Corner address";
  if (cell.role === "edge") return "Edge address";
  if (cell.role === "face") return "Face address";
  return "Core address";
}

function blurbOf(cell: Cell): string {
  if (cell.i === 47) {
    return "Quinary spelling of 47. Same integer as dim ker K. The address is not identified with the kernel.";
  }
  if (cell.i === 78) {
    return "Quinary spelling of 78. Complement 125 − 47. Reserved ledger slot, not a new operator.";
  }
  if (cell.i === 62) {
    return "Center of the cube. Magnetic labels m = (0,0,0). Digit d maps to m = d − 2.";
  }
  return `Packing address in Σ = {0,1,2,3,4}³. Word is xyz₅. i = 25x + 5y + z. This cubie is that Notion row.`;
}

export function ledgerOf(cell: Cell): LedgerRecord {
  const line = cell.i + 1;
  const href = slots[cell.word as Word] ?? NOTION_Q5_HUB;
  return {
    i: cell.i,
    x: cell.x,
    y: cell.y,
    z: cell.z,
    word: cell.word,
    m: cell.m,
    role: cell.role,
    title: titleOf(cell),
    blurb: blurbOf(cell),
    github: {
      cell: `${GITHUB_Q5}/cells.jsonl#L${line}`,
      map: `${GITHUB_Q5}/README.md#z--${cell.z}`,
      codec: `${GITHUB_Q5}/codec.py`,
      validator: `${GITHUB_Q5}/validator.py`,
      host: `${GITHUB_Q5}/host.py`,
      pages: PAGES_CUBE,
    },
    notion: {
      href,
      label: `Notion ${cell.word}`,
    },
  };
}

export function encodeCell(cell: Cell) {
  return {
    i: cell.i,
    x: cell.x,
    y: cell.y,
    z: cell.z,
    word: cell.word,
  };
}

export const LEDGER: LedgerRecord[] = CELLS.map(ledgerOf);
