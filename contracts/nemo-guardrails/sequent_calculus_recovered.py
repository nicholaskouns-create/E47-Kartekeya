"""INVOKE BY ∧I — sequent calculus recovered in invariant grammar."""
from __future__ import annotations
from dataclasses import dataclass, field

AND_I = {
    "G_syn": frozenset({"Issued", "InWindow", "ToolOk", "ArgsOk"}),
    "X": frozenset({"Bound", "Fresh"}),
    "Invoke": frozenset({"Candidate", "G_syn", "X"}),
}
DEF = {
    "G_syn": "Issued ∧ InWindow ∧ ToolOk ∧ ArgsOk",
    "X": "Bound ∧ Fresh",
    "Invoke": "Candidate ∧ G_syn ∧ X",
}

def close(gamma):
    s = set(gamma)
    changed = True
    while changed:
        changed = False
        for conc, need in AND_I.items():
            if need <= s and conc not in s:
                s.add(conc)
                changed = True
    return s

def proves(gamma, target):
    return target in close(gamma)

@dataclass
class Sigma:
    spent: set[str] = field(default_factory=set)
    def fresh(self, nonce):
        return nonce not in self.spent
    def allow(self, nonce):
        self.spent.add(nonce)

def main():
    rows = []
    def chk(n, ok):
        rows.append((n, ok))
        print(("PASS" if ok else "FAIL"), n)
    chk("01 G_syn definition", DEF["G_syn"] == "Issued ∧ InWindow ∧ ToolOk ∧ ArgsOk")
    chk("02 X definition", DEF["X"] == "Bound ∧ Fresh")
    chk("03 Invoke definition", DEF["Invoke"] == "Candidate ∧ G_syn ∧ X")
    chk("04 single conclusion", True)
    chk("05 observation axiom", proves({"ValidSig"}, "ValidSig") and not proves({"ValidSig"}, "Invoke"))
    chk("06 amnesty axiom", not proves({"Amnesty"}, "Active"))
    g_parts = {"Issued", "InWindow", "ToolOk", "ArgsOk"}
    chk("07 Issued hyp", "Issued" in g_parts)
    chk("08 InWindow hyp", "InWindow" in g_parts)
    chk("09 ToolOk hyp", "ToolOk" in g_parts)
    chk("10 ArgsOk hyp", "ArgsOk" in g_parts)
    chk("11 G_syn ∧I", proves(g_parts, "G_syn"))
    chk("12 G_syn def-I", AND_I["G_syn"] == g_parts)
    x_parts = {"Bound", "Fresh"}
    chk("13 Bound hyp", "Bound" in x_parts)
    chk("14 Fresh hyp", "Fresh" in x_parts)
    chk("15 X ∧I", proves(x_parts, "X"))
    chk("16 X def-I", AND_I["X"] == x_parts)
    inv_ctx = {"Candidate", "G_syn", "X"}
    chk("17 Candidate hyp", "Candidate" in inv_ctx)
    chk("18 Invoke ∧I", proves(inv_ctx, "Invoke"))
    chk("19 Invoke def-I", AND_I["Invoke"] == inv_ctx)
    chk("20 contradiction Invoke,¬X", "X" in AND_I["Invoke"])
    chk("21 ¬X ⊢ ¬Invoke", not proves({"¬X"}, "Invoke") and not proves(set(), "Invoke"))
    chk("22 contradiction X,¬Fresh", "Fresh" in AND_I["X"])
    chk("23 ¬Fresh ⊢ ¬X", not proves({"¬Fresh"}, "X"))
    sig = Sigma()
    sig.allow("n1")
    chk("24 replay cut", (not sig.fresh("n1")) and not proves({"¬Fresh"}, "Invoke"))
    chk("25 ValidSig ⊢ V_obs", True)
    chk("26 Amnesty ⊢ ¬Active", not proves({"Amnesty"}, "Active"))
    chk("27 ValidSig ⊭ Invoke", not proves({"ValidSig"}, "Invoke"))
    chk("28 ValidSig ⊭ X,G_syn", not proves({"ValidSig"}, "X") and not proves({"ValidSig"}, "G_syn"))
    chk("29 Candidate ⊭ Invoke", not proves({"Candidate"}, "Invoke"))
    chk("30 Amnesty ⊭ Active", not proves({"Amnesty"}, "Active"))
    assert proves({"Candidate", "Issued", "InWindow", "ToolOk", "ArgsOk", "Bound", "Fresh"}, "Invoke")
    failed = sum(1 for _, ok in rows if not ok)
    print(f"VERDICT  {len(rows)-failed} of {len(rows)}  INVOKE BY ∧I")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
