#!/usr/bin/env python3
"""
LINGUISTICS BUREAU // UNIVERSAL TRANSLATOR
Mathematical City / Numerical Civilizations

Architecture
------------
Natural language:
    L_natural -> E_IG -> Sigma_L -> K_L -> Psi_L -> Gamma^n -> Lambda_L -> Omega_L -> I_L

Exact numerical dialects:
    source -> parse -> Q exact normalization -> target -> inverse reconstruction -> certificate

The natural-language branch is a typed semantic compiler, not a truth oracle.
If OPENAI_API_KEY is configured, an AI parser can populate the semantic envelope.
Otherwise the app uses a conservative deterministic skeleton parser that preserves
raw claims, obvious negation/modality, quantities, and time expressions.

The numerical branch delegates to Mathematical City Engine v1.0 when installed.

Run:
    streamlit run linguistics_bureau_universal_translator.py

Optional AI:
    pip install openai
    export OPENAI_API_KEY=...
    export OPENAI_MODEL=gpt-5.6-sol   # or another model available to your account

Self-test:
    python linguistics_bureau_universal_translator.py --self-test
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
import argparse
import hashlib
import json
import os
import re
from typing import Any, Iterable

from city_spectral_engine import semantic_constraint_system, compact_payload


APP_NAME = "Linguistics Bureau // Universal Translator"
APP_VERSION = "0.3.1"
IG_PIPELINE = ["Σ", "K", "Ψ", "Γ", "Λ", "Ω", "I"]
DEFAULT_CONSTRAINTS = [
    "logic",
    "type",
    "evidence",
    "provenance",
    "temporal_order",
    "contradiction_memory",
]
SEMANTIC_FIELDS = [
    "entities",
    "actions",
    "objects",
    "relations",
    "claims",
    "negations",
    "conditions",
    "quantities",
    "times",
    "modalities",
    "provenance",
    "evidence_class",
    "authority",
    "confidence",
    "dependencies",
    "contradictions",
    "unresolved",
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uniq(items: Iterable[Any]) -> list[Any]:
    seen = set()
    out = []
    for item in items:
        key = canonical_json(item) if isinstance(item, (dict, list)) else str(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


@dataclass
class SemanticEnvelope:
    raw_text: str
    source_language: str = "auto"
    entities: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    negations: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    quantities: list[str] = field(default_factory=list)
    times: list[str] = field(default_factory=list)
    modalities: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    evidence_class: list[str] = field(default_factory=list)
    authority: list[str] = field(default_factory=list)
    confidence: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    parser: str = "deterministic-skeleton"
    interpretive: bool = True

    def normalized(self) -> "SemanticEnvelope":
        data = asdict(self)
        for name in SEMANTIC_FIELDS:
            data[name] = _uniq(data.get(name, []))
        data["raw_text"] = self.raw_text.strip()
        data["source_language"] = self.source_language.strip() or "auto"
        return SemanticEnvelope(**data)


@dataclass
class InvariantGrammarPacket:
    schema: str
    schema_version: str
    created_at_utc: str
    sigma: dict[str, Any]
    k: dict[str, Any]
    psi: dict[str, Any]
    gamma: dict[str, Any]
    lambda_state: dict[str, Any]
    omega: dict[str, Any]
    interpretation: dict[str, Any]
    evidence_boundary: str
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_NUMBER_RE = re.compile(r"(?<!\w)[+-]?(?:\d+(?:\.\d+)?|\d+\/\d+)(?:%|°)?")
_TIME_RE = re.compile(
    r"\b(?:today|tomorrow|yesterday|tonight|morning|afternoon|evening|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"january|february|march|april|may|june|july|august|september|october|november|december|"
    r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2})\b",
    re.I,
)
_NEGATION_RE = re.compile(r"\b(?:no|not|never|none|without|cannot|can't|won't|didn't|doesn't|isn't|aren't)\b", re.I)
_MODAL_RE = re.compile(r"\b(?:may|might|can|could|should|would|must|will|predicted|pending|failed|verified|observed|inferred)\b", re.I)
_CONDITION_RE = re.compile(r"\b(?:if|unless|provided that|when|whenever|only if)\b", re.I)
_PROPER_RE = re.compile(r"\b[A-Z][A-Za-z0-9_\-]*(?:\s+[A-Z][A-Za-z0-9_\-]*)*\b")


def deterministic_semantic_parse(text: str, source_language: str = "auto") -> SemanticEnvelope:
    raw = text.strip()
    if not raw:
        raise ValueError("Input text is empty.")
    sentences = [s.strip() for s in _SENTENCE_RE.split(raw) if s.strip()]
    if not sentences:
        sentences = [raw]

    entities = []
    for phrase in _PROPER_RE.findall(raw):
        if phrase.lower() not in {"i", "the", "a", "an"}:
            entities.append(phrase)

    negations = [s for s in sentences if _NEGATION_RE.search(s)]
    conditions = [s for s in sentences if _CONDITION_RE.search(s)]
    quantities = _NUMBER_RE.findall(raw)
    times = _TIME_RE.findall(raw)
    modalities = _uniq(m.group(0).lower() for m in _MODAL_RE.finditer(raw))

    return SemanticEnvelope(
        raw_text=raw,
        source_language=source_language,
        entities=_uniq(entities),
        claims=sentences,
        negations=negations,
        conditions=conditions,
        quantities=_uniq(quantities),
        times=_uniq(times),
        modalities=modalities,
        unresolved=[
            "Deterministic mode does not infer hidden relations, truth, intent, or referents."
        ],
        parser="deterministic-skeleton",
        interpretive=True,
    ).normalized()


def _semantic_prompt(text: str, source_language: str) -> str:
    schema = {name: [] for name in SEMANTIC_FIELDS}
    schema.update({"source_language": source_language, "raw_text": text})
    return f"""
You are the semantic front end for the Mathematical City Linguistics Bureau.
Convert the supplied natural-language utterance into a conservative typed semantic envelope.

Rules:
1. Preserve the user's propositions, negations, conditions, quantities, dates/times, modality, uncertainty, provenance, and unresolved ambiguity.
2. Do not add facts not present in the utterance.
3. Do not resolve contradictions by deleting either side. Record them.
4. Evidence labels are descriptive only. Never promote evidence beyond the utterance.
5. If a field is unknown, use an empty list or put the ambiguity in unresolved.
6. Return exactly one JSON object and no markdown.

Required JSON shape:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Utterance:
{text}
""".strip()


def ai_semantic_parse(text: str, source_language: str = "auto", model: str | None = None) -> SemanticEnvelope:
    """Optional AI parser. Hashing certifies the returned packet, not its truth."""
    try:
        from openai import OpenAI  # type: ignore
    except Exception as exc:
        raise RuntimeError("OpenAI package not installed. Run: pip install openai") from exc
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI()
    response = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
        input=_semantic_prompt(text, source_language),
    )
    payload = json.loads(response.output_text)
    clean = {name: payload.get(name, []) for name in SEMANTIC_FIELDS}
    return SemanticEnvelope(
        raw_text=text.strip(),
        source_language=str(payload.get("source_language", source_language)),
        parser=f"openai:{getattr(response, 'model', model or os.getenv('OPENAI_MODEL', 'unknown'))}",
        interpretive=True,
        **clean,
    ).normalized()


def validate_semantic_envelope(envelope: SemanticEnvelope) -> dict[str, Any]:
    d = asdict(envelope.normalized())
    checks = {
        "raw_text_present": bool(d["raw_text"]),
        "claims_present": bool(d["claims"]),
        "list_types_valid": all(isinstance(d[name], list) for name in SEMANTIC_FIELDS),
        "negation_memory_preserved": all(item in d["claims"] for item in d["negations"]),
        "condition_memory_preserved": all(item in d["claims"] for item in d["conditions"]),
    }
    return {"checks": checks, "passed": all(checks.values())}


def compile_invariant_grammar(envelope: SemanticEnvelope) -> InvariantGrammarPacket:
    env = envelope.normalized()
    validation = validate_semantic_envelope(env)
    if not validation["passed"]:
        raise ValueError(f"Typed semantic envelope failed structural checks: {validation}")

    env_dict = asdict(env)
    populated = sum(1 for f in SEMANTIC_FIELDS if env_dict.get(f))
    omega_schema = populated / len(SEMANTIC_FIELDS)

    # Shared Mathematical City spectral bus. This reuses the operator grammar,
    # not E47's carrier, eigenvalues, or 47/125 occupancy.
    spectral_system = semantic_constraint_system(env)
    spectral_payload = compact_payload(spectral_system)
    spectral_report = spectral_payload["report"]

    sigma = {
        "type": "linguistic_possibility_space",
        "raw_text": env.raw_text,
        "source_language": env.source_language,
        "candidate_semantics": {name: env_dict[name] for name in SEMANTIC_FIELDS},
    }
    k = {
        "type": "constraint_bundle",
        "constraints": DEFAULT_CONSTRAINTS,
        "structural_validation": validation,
        "rule": "preserve typed claims, uncertainty, provenance, contradictions, and failure memory",
        "spectral_operator": {
            "K_L": "typed semantic incidence / constraint operator",
            "Q_L": "K_L^T K_L",
            "dimension": spectral_report["dimension"],
            "constraint_rows": spectral_report["constraint_rows"],
            "operator_hash": spectral_report["operator_hash"],
        },
    }
    psi = {
        "type": "typed_surviving_structure",
        "claims": env.claims,
        "negations": env.negations,
        "conditions": env.conditions,
        "quantities": env.quantities,
        "times": env.times,
        "modalities": env.modalities,
        "contradictions": env.contradictions,
        "unresolved": env.unresolved,
        "note": "survival here means schema/type preservation, not empirical truth certification",
    }
    gamma = {
        "type": "recursive_normalization_and_spectral_contraction",
        "steps": [
            "normalize whitespace and duplicate semantic items",
            "preserve explicit negation and modality",
            "preserve provenance/evidence labels without promotion",
            "retain contradictions and unresolved ambiguity",
            "canonicalize JSON for deterministic hashing",
        ],
        "spectral_execution": {
            "generator": "Q_L = K_L^T K_L",
            "rule": "Gamma_L = I - epsilon_star Q_L",
            "epsilon_max": spectral_report["epsilon_max"],
            "epsilon_star": spectral_report["epsilon_star"],
            "rho_star": spectral_report["rho_star"],
            "positive_min": spectral_report["positive_min"],
            "positive_max": spectral_report["positive_max"],
            "contraction_residuals": spectral_payload["trajectory"]["residuals"],
        },
    }

    lambda_seed = {
        "schema": "mathematical-city.invariant-language-packet",
        "schema_version": APP_VERSION,
        "semantic_envelope": env_dict,
        "constraints": DEFAULT_CONSTRAINTS,
        "spectral_operator_hash": spectral_report["operator_hash"],
    }
    lambda_state = {
        "type": "canonical_semantic_projection",
        "canonical_json": canonical_json(lambda_seed),
        "semantic_digest": sha256_json(lambda_seed),
        "spectral_projector": {
            "limit": "Gamma_L^n -> P_ker(K_L)",
            "kernel_dimension": spectral_report["kernel_dimension"],
            "rank": spectral_report["rank"],
            "projector_residual": spectral_report["projector_residual"],
            "annihilation_residual": spectral_report["annihilation_residual"],
            "gamma_projector_residual": spectral_report["gamma_projector_residual"],
        },
    }
    omega = {
        "type": "schema_occupancy",
        "value": omega_schema,
        "numerator": populated,
        "denominator": len(SEMANTIC_FIELDS),
        "boundary": "This is a schema-population measure, not the E47 coherence ratio 47/125.",
    }
    interpretation = {
        "type": "canonical_english",
        "text": render_canonical_english(env),
        "parser": env.parser,
        "interpretive": env.interpretive,
    }
    boundary = (
        "The natural-language branch compiles and preserves a typed semantic representation. "
        "Its hash certifies the exact packet bytes, not the truth or uniqueness of the interpretation. "
        "The spectral animation certifies execution of the declared K_L -> Q_L -> ker(K_L) -> P -> Gamma_L chain; "
        "it does not import E47 constants into linguistics or establish a universal empirical language law."
    )

    packet = InvariantGrammarPacket(
        schema="mathematical-city.invariant-grammar-translation",
        schema_version=APP_VERSION,
        created_at_utc=utc_now(),
        sigma=sigma,
        k=k,
        psi=psi,
        gamma=gamma,
        lambda_state=lambda_state,
        omega=omega,
        interpretation=interpretation,
        evidence_boundary=boundary,
    )
    body = packet.to_dict()
    body.pop("sha256", None)
    packet.sha256 = sha256_json(body)
    return packet

def render_canonical_english(envelope: SemanticEnvelope) -> str:
    lines = []
    if envelope.claims:
        lines.append("Claims: " + " | ".join(envelope.claims))
    if envelope.negations:
        lines.append("Negation retained: " + " | ".join(envelope.negations))
    if envelope.conditions:
        lines.append("Conditions: " + " | ".join(envelope.conditions))
    if envelope.quantities:
        lines.append("Quantities: " + ", ".join(envelope.quantities))
    if envelope.times:
        lines.append("Times: " + ", ".join(envelope.times))
    if envelope.modalities:
        lines.append("Modality: " + ", ".join(envelope.modalities))
    if envelope.contradictions:
        lines.append("Contradictions retained: " + " | ".join(envelope.contradictions))
    if envelope.unresolved:
        lines.append("Unresolved: " + " | ".join(envelope.unresolved))
    return "\n".join(lines) if lines else envelope.raw_text


def render_python_assertions(packet: InvariantGrammarPacket) -> str:
    digest = packet.sha256
    claims = packet.psi.get("claims", [])
    contradictions = packet.psi.get("contradictions", [])
    spectral = packet.lambda_state.get("spectral_projector", {})
    execution = packet.gamma.get("spectral_execution", {})
    return "\n".join([
        f"PACKET_SHA256 = {digest!r}",
        f"CLAIMS = {claims!r}",
        f"CONTRADICTIONS = {contradictions!r}",
        f"KERNEL_DIMENSION = {spectral.get('kernel_dimension', 0)!r}",
        f"EPSILON_STAR = {execution.get('epsilon_star', 0.0)!r}",
        f"RHO_STAR = {execution.get('rho_star', 0.0)!r}",
        "assert PACKET_SHA256",
        "assert isinstance(CLAIMS, list)",
        "assert isinstance(CONTRADICTIONS, list)",
        "assert KERNEL_DIMENSION >= 1",
        "assert 0.0 <= RHO_STAR <= 1.0",
    ])

def ai_render_from_packet(packet: InvariantGrammarPacket, target_language: str, model: str | None = None) -> str:
    try:
        from openai import OpenAI  # type: ignore
    except Exception as exc:
        raise RuntimeError("OpenAI package not installed. Run: pip install openai") from exc
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    client = OpenAI()
    prompt = f"""
Render the following canonical invariant-language packet into {target_language}.
Preserve every claim, negation, condition, number, time, modality, contradiction,
uncertainty marker, provenance/evidence label, and unresolved item. Do not add facts.
Return only the translated natural-language text.

PACKET:
{json.dumps(packet.to_dict(), ensure_ascii=False, indent=2)}
""".strip()
    response = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
        input=prompt,
    )
    return response.output_text.strip()


# ---------- Exact Numerical Civilizations branch ----------

def _load_city_engine():
    try:
        from mathematical_city.dialects import DIALECTS  # type: ignore
        from mathematical_city.workflows import run_full_workflow  # type: ignore
        return DIALECTS, run_full_workflow
    except Exception:
        return None, None


def numerical_translate(source: str, target: str, value: Any) -> dict[str, Any]:
    dialects, workflow = _load_city_engine()
    if workflow is None:
        raise RuntimeError(
            "Mathematical City Engine v1.0 is not importable. Install it first with `pip install -e .`."
        )
    return workflow(source, target, value)


# ---------- Streamlit interface ----------
CSS = r"""
<style>
:root { --bg:#070a12; --panel:#0d1322; --line:#27334d; --cyan:#5ee7f2; --violet:#b995ff; --gold:#f3d47b; --text:#edf3ff; --muted:#8d9ab5; }
.stApp { background: radial-gradient(circle at 50% -10%, #17213b 0%, #090d17 42%, #05070d 100%); color:var(--text); }
.block-container { max-width:1180px; padding-top:2rem; }
.lab-kicker { letter-spacing:.22em; font-size:.76rem; color:var(--cyan); text-transform:uppercase; font-weight:700; }
.lab-title { font-size:3rem; line-height:1; font-weight:800; letter-spacing:-.04em; margin:.2rem 0 .35rem 0; }
.lab-sub { color:var(--muted); font-size:1.04rem; margin-bottom:1.2rem; }
.pipeline { display:flex; align-items:center; gap:.4rem; flex-wrap:wrap; margin:.8rem 0 1.4rem 0; }
.glyph { border:1px solid var(--line); background:rgba(13,19,34,.78); border-radius:999px; padding:.36rem .65rem; color:var(--gold); font-weight:800; }
.arrow { color:#566481; }
.card { border:1px solid var(--line); background:linear-gradient(180deg,rgba(15,22,39,.96),rgba(8,12,22,.96)); border-radius:18px; padding:1rem 1.1rem; margin:.35rem 0; box-shadow:0 12px 40px rgba(0,0,0,.18); }
.card-label { color:var(--cyan); font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; font-weight:800; }
.card-value { color:var(--text); font-size:.96rem; margin-top:.28rem; }
.boundary { border-left:3px solid var(--gold); padding:.7rem 1rem; background:rgba(243,212,123,.06); color:#cbd3e3; border-radius:0 12px 12px 0; }
.digest { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.78rem; color:var(--violet); word-break:break-all; }
div[data-testid="stTabs"] button { font-weight:700; }
</style>
"""


def _packet_card(glyph: str, title: str, value: Any) -> str:
    if isinstance(value, (dict, list)):
        preview = json.dumps(value, ensure_ascii=False, indent=2)
    else:
        preview = str(value)
    if len(preview) > 950:
        preview = preview[:950] + "\n…"
    return f'<div class="card"><div class="card-label">{glyph} · {title}</div><pre class="card-value">{_html(preview)}</pre></div>'


def _html(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def spectral_animation_html(payload: dict[str, Any], height: int = 365) -> str:
    """Render the Python-computed contraction trajectory as a deterministic live canvas."""
    safe = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#070b14;color:#edf3ff;font:12px Inter,system-ui,sans-serif}}
    .wrap{{position:relative;height:{height}px;border:1px solid #27334d;border-radius:18px;overflow:hidden;background:radial-gradient(circle at 50% 25%,#17213b 0,#0a101d 52%,#05070d 100%)}}
    canvas{{position:absolute;inset:0;width:100%;height:100%}}.tag{{position:absolute;left:16px;top:14px;letter-spacing:.18em;color:#5ee7f2;font-weight:800}}
    .stats{{position:absolute;left:16px;bottom:14px;color:#9caccc;font-family:ui-monospace,monospace}}.step{{position:absolute;right:16px;bottom:14px;color:#f3d47b;font-family:ui-monospace,monospace}}
    </style></head><body><div class='wrap'><canvas id='c'></canvas><div class='tag'>SPECTRAL BUS · SEMANTIC CONSTRAINT FIELD</div><div class='stats' id='stats'></div><div class='step' id='step'></div></div>
    <script>const D={safe};const c=document.getElementById('c'),x=c.getContext('2d');function rs(){{const r=c.getBoundingClientRect(),d=devicePixelRatio||1;c.width=r.width*d;c.height=r.height*d;x.setTransform(d,0,0,d,0,0)}}rs();addEventListener('resize',rs);const col={{claim:'#5ee7f2',entities:'#b995ff',quantities:'#f3d47b',negations:'#ff8299',conditions:'#8dd9a6',times:'#93b5ff',modalities:'#d2a8ff',provenance:'#e5bd70',contradictions:'#ff667d',unresolved:'#ffb86b'}};function h(s){{let q=2166136261;for(let i=0;i<s.length;i++){{q^=s.charCodeAt(i);q=Math.imul(q,16777619)}}return q>>>0}}function pos(n,w,hg){{const z=h(n.kind+':'+n.label),a=(z%6283)/1000,r=.18+.28*((z>>>8)%1000)/1000;return [w*(.5+r*Math.cos(a)),hg*(.48+r*.82*Math.sin(a))]}}let t=performance.now();function draw(){{const w=c.clientWidth,hg=c.clientHeight,S=D.trajectory.states||[],R=D.trajectory.residuals||[],i=S.length?Math.floor(((performance.now()-t)/95)%S.length):0,st=S[i]||[],mx=Math.max(.001,...st.map(Math.abs)),P=D.nodes.map(n=>pos(n,w,hg));x.clearRect(0,0,w,hg);x.strokeStyle='rgba(72,94,137,.28)';D.edges.forEach(e=>{{const a=P[e.source],b=P[e.target];x.beginPath();x.moveTo(...a);x.lineTo(...b);x.stroke()}});D.nodes.forEach((n,j)=>{{const p=P[j],v=(st[j]||0)/mx,cc=col[n.kind]||'#8fa1c5';x.shadowBlur=12+22*Math.abs(v);x.shadowColor=cc;x.fillStyle=cc;x.globalAlpha=.4+.58*Math.abs(v);x.beginPath();x.arc(p[0],p[1],n.kind==='claim'?6.4:3.7,0,Math.PI*2);x.fill();x.shadowBlur=0;x.globalAlpha=1}});if(R.length>1){{const bx=16,by=hg-58,bw=Math.min(220,w*.3),bh=25,rm=Math.max(...R,1e-12);x.strokeStyle='rgba(94,231,242,.75)';x.beginPath();R.forEach((v,k)=>{{const xx=bx+bw*k/(R.length-1),yy=by+bh-bh*v/rm;k?x.lineTo(xx,yy):x.moveTo(xx,yy)}});x.stroke()}}document.getElementById('stats').textContent=`dim ${{D.report.dimension}} · constraints ${{D.report.constraint_rows}} · ker ${{D.report.kernel_dimension}} · ε* ${{Number(D.report.epsilon_star).toPrecision(4)}} · ρ* ${{Number(D.report.rho_star).toFixed(4)}}`;document.getElementById('step').textContent=`n=${{i}} · residual ${{Number(R[i]||0).toExponential(2)}}`;requestAnimationFrame(draw)}}requestAnimationFrame(draw);</script></body></html>"""


def run_streamlit_app() -> None:
    import streamlit as st  # type: ignore

    st.set_page_config(page_title="Universal Translator · Linguistics Bureau", page_icon="🌐", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="lab-kicker">The Mathematical City · Linguistics Bureau</div>', unsafe_allow_html=True)
    st.markdown('<div class="lab-title">UNIVERSAL TRANSLATOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="lab-sub">One invariant. Many dialects. The relation survives; the glyph may change.</div>', unsafe_allow_html=True)
    st.markdown('<div class="pipeline">' + ''.join(
        f'<span class="glyph">{g}</span>' + ('<span class="arrow">→</span>' if i < len(IG_PIPELINE)-1 else '')
        for i, g in enumerate(IG_PIPELINE)
    ) + '</div>', unsafe_allow_html=True)

    if "spectral_payload" not in st.session_state:
        _hero_env = deterministic_semantic_parse("One invariant survives translation. Different dialects preserve the relation, but unsupported claims must not be promoted.")
        st.session_state["spectral_payload"] = compact_payload(semantic_constraint_system(_hero_env))
    st.components.v1.html(spectral_animation_html(st.session_state["spectral_payload"]), height=385, scrolling=False)
    st.caption("Live operator witness: K_L → Q_L=K_LᵀK_L → P_ker(K_L) → Γ_Lⁿ. The animation is computed from the current input, not a decorative loop.")

    lang_tab, number_tab, about_tab = st.tabs(["🌐 Universal Translator", "🏛️ Numerical Civilizations", "◎ Boundary"])

    with lang_tab:
        left, right = st.columns([1.03, .97], gap="large")
        with left:
            text = st.text_area(
                "Input language",
                height=230,
                placeholder="Paste a statement, argument, translation target, research note, or ordinary sentence…",
            )
            c1, c2 = st.columns(2)
            with c1:
                source_language = st.text_input("Source language", value="auto")
            with c2:
                target_language = st.text_input("Render language", value="English")
            ai_available = bool(os.getenv("OPENAI_API_KEY"))
            use_ai = st.toggle("AI semantic parser", value=ai_available, disabled=not ai_available,
                               help="When off, the conservative deterministic skeleton parser is used.")
            project = st.button("PROJECT TO INVARIANT", type="primary", use_container_width=True)

        if project:
            try:
                env = ai_semantic_parse(text, source_language) if use_ai else deterministic_semantic_parse(text, source_language)
                packet = compile_invariant_grammar(env)
                st.session_state["ig_packet"] = packet.to_dict()
                st.session_state["ig_env"] = asdict(env)
                st.session_state["spectral_payload"] = compact_payload(semantic_constraint_system(env))
                if target_language.strip().lower() == "english":
                    rendered = packet.interpretation["text"]
                elif use_ai:
                    rendered = ai_render_from_packet(packet, target_language)
                else:
                    rendered = "AI rendering is disabled. The invariant packet is available below."
                st.session_state["ig_render"] = rendered
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        packet_dict = st.session_state.get("ig_packet")
        if packet_dict:
            packet = InvariantGrammarPacket(**packet_dict)
            with right:
                st.markdown("#### Invariant render")
                st.text_area("Output", value=st.session_state.get("ig_render", ""), height=230, label_visibility="collapsed")
                st.markdown(f'<div class="digest">SHA-256 · {packet.sha256}</div>', unsafe_allow_html=True)
                st.caption("The digest seals this representation. It does not certify that an AI interpretation is uniquely true.")

            sr = packet.gamma.get("spectral_execution", {})
            sp = packet.lambda_state.get("spectral_projector", {})
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Semantic dimension", packet.k.get("spectral_operator", {}).get("dimension", 0))
            m2.metric("Kernel rank", sp.get("kernel_dimension", 0))
            m3.metric("ε*", f"{float(sr.get('epsilon_star', 0.0)):.6g}")
            m4.metric("ρ*", f"{float(sr.get('rho_star', 0.0)):.6g}")
            st.markdown("### Typed projection")
            cols = st.columns(3)
            cards = [
                ("Σ", "possibility space", packet.sigma),
                ("K", "constraint bundle", packet.k),
                ("Ψ", "surviving typed structure", packet.psi),
                ("Γ", "recursive normalization", packet.gamma),
                ("Λ", "canonical projection", packet.lambda_state),
                ("Ω", "schema occupancy", packet.omega),
            ]
            for idx, (glyph, title, val) in enumerate(cards):
                with cols[idx % 3]:
                    st.markdown(_packet_card(glyph, title, val), unsafe_allow_html=True)

            with st.expander("Canonical JSON"):
                st.json(packet.to_dict())
            with st.expander("Python assertion render"):
                st.code(render_python_assertions(packet), language="python")
            st.markdown(f'<div class="boundary">{_html(packet.evidence_boundary)}</div>', unsafe_allow_html=True)

    with number_tab:
        dialects, _ = _load_city_engine()
        if dialects is None:
            st.warning("Mathematical City Engine v1.0 is not importable in this environment.")
        else:
            names = sorted(dialects.keys())
            a, b, c = st.columns([1,1,2])
            with a:
                source = st.selectbox("Source dialect", names, index=names.index("decimal") if "decimal" in names else 0)
            with b:
                target = st.selectbox("Target dialect", names, index=names.index("babylonian") if "babylonian" in names else 0)
            with c:
                value = st.text_input("Exact value / numeral", value="125")
            if st.button("TRANSLATE EXACTLY", use_container_width=True):
                try:
                    result = numerical_translate(source, target, value)
                    tr = result["translation"]
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("Output", tr["target_output"])
                    p2.metric("Exact value", f'{tr["exact_numerator"]}/{tr["exact_denominator"]}')
                    p3.metric("Round trip", "PASS" if tr["round_trip_passed"] else "FAIL")
                    p4.metric("Evidence", result["proof"]["evidence_class"])
                    st.code(f'{source}({value})  →  {target}({tr["target_output"]})  →  {source}({tr["round_trip_source"]})')
                    st.json(result["proof"])
                    st.markdown(f'<div class="digest">Certificate · {tr["certificate"]["sha256"]}</div>', unsafe_allow_html=True)
                except Exception as exc:
                    st.error(str(exc))

    with about_tab:
        st.markdown("""
### Bureau contract
The exact numerical branch preserves the existing City Engine gate:

`T_j→i(T_i→j(x)) = x`

The natural-language branch adds a front-end compiler:

`L_natural → E_IG → Σ_L → K_L → Q_L=K_LᵀK_L → Γ_L^n → P_ker(K_L) → I_target`

**Shared spectral bus:** the language interface uses the same positive-generator contraction grammar as Kartekeya/SPECTRA and the Hodge/Laplacian Murmuration bridge: `Q=K†K`, `P=P_ker(K)`, `Γ=I-εQ`. The language-specific `K_L` is built from the typed semantic incidence structure; no E47 eigenvalues or 47/125 occupancy are imported.

**Crucial boundary:** `Ψ_L` means the semantic record survived the declared typing and memory constraints. It does **not** mean every proposition is empirically true. AI parsing and AI rendering remain interpretive operations. Raw input, contradictions, uncertainties, and provenance are retained so later agents can audit them rather than inheriting polished ambiguity.
        """)
        st.info("Ω in this app is schema occupancy only. It is deliberately not identified with the E47 ratio 47/125.")


def self_test() -> None:
    text = "Mnemosyne predicted 2 loops, but the Fold gate did not pass. If runtime telemetry arrives tomorrow, seal the forecast before reveal."
    env = deterministic_semantic_parse(text)
    assert len(env.claims) == 2
    assert any("did not pass" in x for x in env.negations)
    assert "2" in env.quantities
    assert "tomorrow" in [x.lower() for x in env.times]
    packet = compile_invariant_grammar(env)
    assert packet.sha256 and len(packet.sha256) == 64
    assert packet.omega["value"] != Fraction(47, 125)
    assert "truth" in packet.evidence_boundary.lower()
    system = semantic_constraint_system(env)
    report = system["report"]
    assert report.dimension == len(system["nodes"])
    assert report.kernel_dimension >= 1
    assert report.projector_residual < 1e-8
    assert report.annihilation_residual < 1e-8
    assert system["trajectory"]["residuals"][-1] <= system["trajectory"]["residuals"][0] + 1e-12

    dialects, workflow = _load_city_engine()
    if workflow is not None:
        result = numerical_translate("decimal", "babylonian", "125")
        assert result["translation"]["target_output"] == "2:5"
        assert result["translation"]["round_trip_passed"] is True
    print("UNIVERSAL TRANSLATOR SELF-TEST: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--self-test", action="store_true")
    args, _ = parser.parse_known_args()
    if args.self_test:
        self_test()
        return
    run_streamlit_app()


if __name__ == "__main__":
    main()
