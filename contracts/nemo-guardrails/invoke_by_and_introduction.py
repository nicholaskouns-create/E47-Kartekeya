"""INVOKE BY ∧I

    ValidSig(d) ⊭ Invoke
    Candidate(d), G_syn, X ⊢ Invoke
"""
from __future__ import annotations

from dataclasses import dataclass


ATOMS = frozenset({
    "ValidSig", "Candidate", "Issued", "InWindow", "ToolOk", "ArgsOk",
    "Bound", "Fresh", "G_syn", "X", "Invoke", "Active", "Amnesty",
    "SelfAttested", "Verified", "token_missing", "nonce_spent",
})


@dataclass(frozen=True)
class Line:
    n: int
    formula: str
    rule: str
    cites: tuple[int, ...]
    hyp: bool = False


PROOF: list[Line] = [
    Line(1, "ValidSig", "hyp", (), True),
    Line(2, "Candidate", "hyp", (), True),
    Line(3, "Issued", "hyp", (), True),
    Line(4, "InWindow", "hyp", (), True),
    Line(5, "ToolOk", "hyp", (), True),
    Line(6, "ArgsOk", "hyp", (), True),
    Line(7, "G_syn", "andI", (3, 4, 5, 6)),
    Line(8, "Bound", "hyp", (), True),
    Line(9, "Fresh", "hyp", (), True),
    Line(10, "X", "andI", (8, 9)),
    Line(11, "Invoke", "andI", (2, 7, 10)),
    Line(12, "Amnesty", "hyp", (), True),
    Line(13, "¬Active", "ax_partition", (12,)),
    Line(14, "¬X", "hyp", (), True),
    Line(15, "¬Invoke", "notI", (14,)),
    Line(16, "¬Fresh", "hyp", (), True),
    Line(17, "¬X", "not_fresh_elim", (16,)),
    Line(18, "¬Invoke", "notI", (17,)),
]


AND_I = {
    "G_syn": frozenset({"Issued", "InWindow", "ToolOk", "ArgsOk"}),
    "X": frozenset({"Bound", "Fresh"}),
    "Invoke": frozenset({"Candidate", "G_syn", "X"}),
}

ILLEGAL = [("ValidSig", "Invoke"), ("ValidSig", "X"), ("ValidSig", "G_syn"),
           ("Candidate", "Invoke"), ("SelfAttested", "Active"), ("Amnesty", "Active")]


def entails(gamma: set[str], target: str) -> bool:
    closed = set(gamma)
    changed = True
    while changed:
        changed = False
        for conc, need in AND_I.items():
            if need <= closed and conc not in closed:
                closed.add(conc)
                changed = True
    return target in closed


def available(proof: list[Line], n: int) -> dict[int, str]:
    return {ln.n: ln.formula for ln in proof if ln.n < n}


def check_line(proof: list[Line], ln: Line) -> bool:
    prior = available(proof, ln.n)
    if ln.hyp:
        return ln.formula in ATOMS or ln.formula.startswith("¬")
    if ln.rule == "andI":
        need = AND_I[ln.formula]
        got = {prior[i] for i in ln.cites if i in prior}
        return got == need
    if ln.rule == "ax_partition":
        return prior.get(ln.cites[0]) == "Amnesty" and ln.formula == "¬Active"
    if ln.rule == "notI":
        prem = prior.get(ln.cites[0], "")
        return prem in {"¬X", "¬Fresh"} and ln.formula == "¬Invoke"
    if ln.rule == "not_fresh_elim":
        return prior.get(ln.cites[0]) == "¬Fresh" and ln.formula == "¬X"
    return False


def main() -> int:
    rows: list[tuple[str, bool]] = []
    def chk(name: str, ok: bool) -> None:
        rows.append((name, ok))
        print(("PASS" if ok else "FAIL"), name)
    for ln in PROOF:
        chk(f"L{ln.n}  {ln.formula}  {ln.rule}", check_line(PROOF, ln))
    chk("ValidSig ⊭ Invoke", not entails({"ValidSig"}, "Invoke"))
    chk("Candidate ⊭ Invoke", not entails({"Candidate"}, "Invoke"))
    chk("Candidate,G_syn,X ⊢ Invoke", entails({"Candidate", "G_syn", "X"}, "Invoke"))
    chk("Issued,InWindow,ToolOk,ArgsOk ⊢ G_syn", entails({"Issued", "InWindow", "ToolOk", "ArgsOk"}, "G_syn"))
    chk("Bound,Fresh ⊢ X", entails({"Bound", "Fresh"}, "X"))
    chk("full open ctx ⊢ Invoke", entails(
        {"Candidate", "Issued", "InWindow", "ToolOk", "ArgsOk", "Bound", "Fresh"}, "Invoke"
    ))
    for a, b in ILLEGAL:
        chk(f"{a} ⊭ {b}", not entails({a}, b))
    failed = sum(1 for _, ok in rows if not ok)
    print(f"VERDICT  {len(rows)-failed} of {len(rows)}  INVOKE BY ∧I")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
