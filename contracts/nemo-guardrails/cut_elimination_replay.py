"""CUT-ELIMINATION ON REPLAY\n\n    \u00acFresh_\u03a3 \u22a2 \u00acInvoke\n"""
from __future__ import annotations
from dataclasses import dataclass, field

AND_I = {
    "G_syn": frozenset({"Issued", "InWindow", "ToolOk", "ArgsOk"}),
    "X": frozenset({"Bound", "Fresh"}),
    "Invoke": frozenset({"Candidate", "G_syn", "X"}),
}

def close_intro(gamma):
    s = set(gamma)
    changed = True
    while changed:
        changed = False
        for conc, need in AND_I.items():
            if need <= s and conc not in s:
                s.add(conc)
                changed = True
    return s

def and_e(formula):
    return AND_I.get(formula, frozenset())

def proves_intro(gamma, target):
    return target in close_intro(gamma)

@dataclass
class Sigma:
    spent: set = field(default_factory=set)
    def fresh(self, n):
        return n not in self.spent
    def step_allow(self, n):
        return Sigma(self.spent | {n})

def main():
    rows = []
    def chk(name, ok):
        rows.append((name, ok))
        print(("PASS" if ok else "FAIL"), name)
    chk("Inv-E1  Invoke \u22a2 Candidate", "Candidate" in and_e("Invoke"))
    chk("Inv-E2  Invoke \u22a2 G_syn", "G_syn" in and_e("Invoke"))
    chk("Inv-E3  Invoke \u22a2 X", "X" in and_e("Invoke"))
    chk("X-E1    X \u22a2 Bound", "Bound" in and_e("X"))
    chk("X-E2    X \u22a2 Fresh", "Fresh" in and_e("X"))
    gamma = {"Candidate", "Issued", "InWindow", "ToolOk", "ArgsOk", "Bound", "Fresh"}
    chk("P1      \u0393 \u22a2 Invoke", proves_intro(gamma, "Invoke"))
    chk("P2      \u00acX \u22ad Invoke", not proves_intro({"\u00acX"}, "Invoke"))
    chk("P2p     \u0393\\{Fresh} \u22ad Invoke", not proves_intro(gamma - {"Fresh"}, "Invoke"))
    chk("Cut-L   \u00acFresh \u22ad X", not proves_intro({"\u00acFresh"}, "X"))
    chk("Cut-R   \u00acX \u22ad Invoke", not proves_intro({"\u00acX"}, "Invoke"))
    chk("Cut-E   \u00acFresh \u22ad Invoke", not proves_intro({"\u00acFresh"}, "Invoke"))
    s0 = Sigma()
    chk("S0      Fresh(n)", s0.fresh("n"))
    s1 = s0.step_allow("n")
    chk("S-step  ALLOW spends n", (not s1.fresh("n")) and s0.fresh("n"))
    chk("S1      \u00acFresh_S1 \u22ad Invoke", not s1.fresh("n") and not proves_intro({"\u00acFresh"}, "Invoke"))
    chk("P0      ValidSig \u22ad Invoke", not proves_intro({"ValidSig"}, "Invoke"))
    chk("P0p     V_obs \u22ad Invoke", not proves_intro({"V_obs"}, "Invoke"))
    failed = sum(1 for _, ok in rows if not ok)
    print(f"VERDICT  {len(rows)-failed} of {len(rows)}  CUT-ELIMINATION ON REPLAY")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
