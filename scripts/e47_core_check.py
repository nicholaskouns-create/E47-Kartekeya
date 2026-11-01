#!/usr/bin/env python3
"""e47_core_check.py - read-only drift check for the E47 constants (stdlib only).

Recomputes SHA-256 of the embedded canonical constants block, compares it with the
pinned certificate hash (from Identity: simulation/e47_core/e47_core_certificate.json),
then scans this repo's py/js/md/json/html/txt/tex files for E47 constants that
CONTRADICT the canonical values (near-miss numbers such as 99114, 48/125, 0.367, a
wrong multiplicity list). Consistent statements and absence are fine.
Usage: python e47_core_check.py [repo_root]   Exit 0 = no drift, 1 = drift. Modifies nothing.
"""
import hashlib, json, os, re, subprocess, sys
from fractions import Fraction

PINNED_SHA256 = "a393ec7c3d53933795d5f4a41b93ca35f43beec8d88de8429f21c27017bbf624"
CONSTANTS_JSON = '{"Omega_c":"47/125","Omega_c_decimal":"0.376","basis_size":125,"casimir_eigenspace_dims":[1,9,25,28,27,22,13],"casimir_spectrum":[0,2,6,12,20,30,42],"denominator":99144,"epsilon":"1/99144","gamma_by_node":["103/153","10825/12393","1/1","15/17","9943/12393","1/1","-15/17"],"k_squared_off_kernel":[11664,12544,19600,32400,186624],"kernel_rank":47,"kernel_spins":[2,5],"lam_by_node":[180,112,0,-108,-140,0,432],"multiplicities":[1,3,5,4,3,2,1],"pr_coefficients":[1,-107,4088,-66940,430848,-624960,0],"pr_normalizer":1814400,"rho":"15/17","schema":"e47-core-constants/1","tower":{"D":47,"F3":2,"F5":5,"J":5,"L5":11,"j":2},"weight_counts":[19,18,15,10,6,3,1]}'
EXTS = {".py", ".js", ".mjs", ".ts", ".md", ".json", ".html", ".txt", ".tex", ".rst"}
SKIP_DIRS = {".git", "node_modules", "vendor", ".lake", "build", "dist", ".venv", "__pycache__",
             "upstream", "toolchain", "site-packages"}
CTX_EPS = re.compile(r"ε|epsilon|\beps\b|Γ|gamma|denominator|99144|contraction|step size|selector|kernel", re.I)
CTX_K2 = re.compile(r"K\^?2|K²|eigenvalue|rho_?m|11664|186624|12544", re.I)
CTX_OM = re.compile(r"kernel|Ω|omega|protected|fraction|subspace|(?<![\w.])47(?![\w.])", re.I)
CTX_OMD = re.compile(r"Ω|omega|protected (?:fraction|share)|kernel (?:fraction|share)", re.I)
CTX_RHO = re.compile(r"contraction|Γ|99144|15/17", re.I)
NUM = re.compile(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?![\w]|\.\d)|(?<![\w.])\d+(?![\w]|\.\d)")
DEC = re.compile(r"(?<![\w.])0\.(\d{3,})(?![\w])")


def near(a, b):
    """True if digit strings differ by one substitution, transposition, insertion or deletion."""
    if a == b: return False
    if len(a) == len(b):
        d = [i for i in range(len(a)) if a[i] != b[i]]
        return len(d) == 1 or (len(d) == 2 and d[1] == d[0] + 1 and a[d[0]] == b[d[1]] and a[d[1]] == b[d[0]])
    if abs(len(a) - len(b)) != 1: return False
    s, l = sorted((a, b), key=len)
    return any(l[:i] + l[i + 1:] == s for i in range(len(l)))


def dec_drift(m, canon):
    """0.xyz... (3+ digits) is drift if it is a one-digit slip of canon and not a rounding of it."""
    raw = m.group(1); v = Fraction(int(raw), 10 ** len(raw)); t = raw.rstrip("0")[:5]
    c = str(int(canon * 10 ** 12)).zfill(12)[:len(t)]
    return len(t) >= 3 and v != round(canon, len(raw)) and near(t, c)


def near_miss(line, targets, ctx):
    out = []
    if not ctx.search(line): return out
    for m in NUM.finditer(line):
        tok = m.group().replace(",", "")
        for t in targets:
            if near(tok, str(t)) and len(tok) >= len(str(t)): out.append((tok, str(t)))
    return out


def scan_line(line, C):
    res = []
    o = Fraction(C["Omega_c"]); r = Fraction(C["rho"]); k = C["kernel_rank"]; n = C["basis_size"]
    res += near_miss(line, [C["denominator"]], CTX_EPS)
    res += near_miss(line, [C["pr_normalizer"]], re.compile(""))
    res += near_miss(line, C["k_squared_off_kernel"], CTX_K2)
    if CTX_OM.search(line):
        for m in re.finditer(r"(?<![\w.])(\d+)\s*/\s*%d(?![\w.])" % n, line):
            if int(m.group(1)) != k and abs(int(m.group(1)) - k) <= 5: res.append((m.group(), "%d/%d" % (k, n)))
        if CTX_OMD.search(line) or ("47" in line and "125" in line):
            res += [(m.group(), C["Omega_c_decimal"]) for m in DEC.finditer(line) if dec_drift(m, o)]
        for m in re.finditer(r"(?:rank(?:\(P\))?|kernel(?: dimension)?)\s*(?:=|is|of|:)?\s*(\d+)", line, re.I):
            if int(m.group(1)) != k and abs(int(m.group(1)) - k) <= 3: res.append((m.group(), str(k)))
    if CTX_RHO.search(line):
        for m in re.finditer(r"(?<![\w.])(\d+)\s*/\s*17(?![\w.])", line):
            if Fraction(int(m.group(1)), 17) != r and 10 <= int(m.group(1)) <= 17: res.append((m.group(), C["rho"]))
        res += [(m.group(), C["rho"]) for m in DEC.finditer(line) if dec_drift(m, r)]
    for key in ("casimir_eigenspace_dims", "multiplicities", "weight_counts"):
        want = C[key]
        for m in re.finditer(r"(?<![\d.])\d+(?:\s*[,;/]\s*\d+){6}(?![\d.])", line):
            got = [int(x) for x in re.findall(r"\d+", m.group())]
            if got != want and got != want[::-1] and sum(a == b for a, b in zip(got, want)) >= 5:
                res.append((m.group(), str(want)))
    return res


def files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.splitext(f)[1].lower() in EXTS and f != "e47_core_check.py" and os.path.getsize(p) < 3_000_000:
                yield p


def main(argv):
    ok_hash = hashlib.sha256(CONSTANTS_JSON.encode()).hexdigest() == PINNED_SHA256
    C = json.loads(CONSTANTS_JSON)
    print("E47 core check | constants block sha256 %s pinned hash %s"
          % ("MATCHES" if ok_hash else "DIFFERS FROM", PINNED_SHA256[:16] + "..."))
    root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    if len(argv) <= 1:
        try: root = subprocess.check_output(["git", "-C", root, "rev-parse", "--show-toplevel"], text=True,
                                            stderr=subprocess.DEVNULL).strip()
        except Exception: pass
    drift, nfiles, skipped = [], 0, 0
    for p in sorted(files(root)):
        try: lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
        except OSError: continue
        nfiles += 1
        for i, line in enumerate(lines, 1):
            if len(line) > 3000: skipped += 1; continue
            for found, canon in scan_line(line.replace("\u2212", "-"), C):
                drift.append("DRIFT %s:%d  found %r  canonical %s" % (os.path.relpath(p, root), i, found, canon))
    print("scanned %d files under %s (%d over-long lines skipped)" % (nfiles, root, skipped))
    for d in drift: print(d)
    if not ok_hash: print("DRIFT embedded constants block does not match the pinned hash")
    print("RESULT: %s" % ("OK, no contradicting E47 constants" if not drift and ok_hash else "DRIFT (%d findings)" % len(drift)))
    return 0 if not drift and ok_hash else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
