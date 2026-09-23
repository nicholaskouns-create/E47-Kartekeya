"""Source-typed E47 lexical normalization and executable Invariant Grammar.

Normalization is an idempotent finite alias map, not a natural-language model.
Explicit namespaces preserve polysemy. No source records are mutated.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from fractions import Fraction
import unicodedata
import numpy as np

@dataclass(frozen=True)
class Term:
    id: str
    namespace: str
    glyph: str
    python_name: str
    meaning: str
    type: str
    aliases: tuple[str, ...]
    sources: tuple[str, ...]

G = ('notiongrammar',)
TERMS = (
    Term('grammar.ambient','grammar','Σ','Σ','Ambient state space','Space[C,125]',('Sigma','ambient space'),G),
    Term('grammar.selector','grammar','K','K','(C−6I)(C−30I)','End[C^125]',('kernel operator','selector'),('kernel',)+G),
    Term('grammar.survivor','grammar','Ψ','Ψ','ker K; represented by a 125×47 orthonormal basis','Subspace[C^125,47]',('Psi','E47','E₄₇','ker K'),G),
    Term('grammar.contraction','grammar','Γ','Γ','I−εK†K; equals I−εK² here','End[C^125]',('Gamma','contraction'),('contract',)+G),
    Term('grammar.projector','grammar','Λ','Λ','P47, the asymptotic projection','End[C^125]',('Lambda','P47','P₄₇','projector'),G),
    Term('grammar.coherence','grammar','Ω','Ω','||P47 x||²/||x||² for nonzero x','C^125\\{0} -> R',('Omega','coherence'),G),
    Term('grammar.interpretation','grammar','I','I','Caller-supplied interpretation/readout','E47 -> J',('𝓘','𝕀','interpretation','readout'),G),
    Term('grammar.memory','grammar','M','M','Caller-supplied Mnemosyne regeneration','J -> C^125',('𝓜','Mnemosyne','memory'),G),
    Term('grammar.next','grammar','Σ′','Σ_next','Regenerated state; next ambient carrier is C^125 in this implementation','C^125',("Σ'",'Σ’','Sigma_next','Sigma prime'),G),
    Term('algebra.identity','algebra','I','I_identity','125×125 identity matrix','End[C^125]',('identity','I125'),('kernel',)),
    Term('algebra.ratio','algebra','Ω_c','Omega_c','Exact rank fraction 47/125','Q',('OMEGA_C','omega_c'),('kernel','attachment')),
    Term('block.cosmological','block','Λ','Lambda','R/2 in block Einstein closure','R',('Lambda','Lambda_forced'),('attachment',)),
    Term('block.complement','block','Q','Q','I−P47','End[C^125]',('complement projector',),('attachment',)),
    Term('geometry.connection','geometry','Γ','Gamma','Levi-Civita connection coefficients','Tensor[4,4,4]',('Gamma','Gamma_r_mn'),('research/e47-current-20260922/e47_bures_fisher_curvature_validation.py',)),
    Term('geometry.seed','geometry','Ω','Omega','Normalized equal-amplitude cube state','C^125',('uniform state',),('intrinsic','drivecurrent')),
    Term('geometry.generators','geometry','M','M','Three first-factor generators in K² eigenbasis','List[End[C^125]]',('fiber generators',),('research/e47-current-20260922/e47_bures_fisher_curvature_validation.py',)),
    Term('prior_snippet.evolution','prior_snippet','Ψ','Ψ','User-supplied state evolution in prior assistant snippet','C^125 -> C^125',('Psi',),('conversation:prior-assistant-code',)),
    Term('prior_snippet.gate','prior_snippet','Ω','Ω','Boolean residual test in prior assistant snippet','bool',('Omega',),('conversation:prior-assistant-code',)),
    Term('prior_snippet.state','prior_snippet','M','M','State vector in prior assistant snippet','C^125',('state',),('conversation:prior-assistant-code',)),
    Term('prior_snippet.aggregate','prior_snippet','Σ','Σ','Sum of inputs in prior assistant snippet','C^125',('Sigma',),('conversation:prior-assistant-code',)),
    Term('base5.carrier','base5','Σ','BASE5_CARRIER','Quinary carrier with separately typed five-tier register','FiniteSet[125]',('Base 5 carrier','quinary carrier','Base-five pyramid','five-tier pyramid','5 x 5 x 5 carrier','125-state carrier','powers of five pyramid','Python Base 5 renderer','typed quinary object','the invariant Base 5 pyramid carrier'),('drivelexical','lexicalrows')),
)

def spelling(text):
    # Preserve case, scripts, and subscripts. Fold only explicitly equivalent primes.
    return ' '.join(unicodedata.normalize('NFC',text).replace('’','′').replace("'",'′').split())

class AmbiguousTerm(ValueError):
    pass

class LexicalAttractor:
    def __init__(self, terms=TERMS):
        self.terms = {t.id:t for t in terms}
        self.index = {}
        for t in terms:
            for a in (t.id,t.glyph,t.python_name,*t.aliases):
                self.index.setdefault(spelling(a),set()).add(t.id)

    def resolve(self, token, namespace=None):
        if token in self.terms:
            t=self.terms[token]
            if namespace is not None and t.namespace != namespace:
                raise KeyError((token,namespace))
            return t.id
        ids=self.index.get(spelling(token),set())
        if namespace is not None:
            ids={i for i in ids if self.terms[i].namespace == namespace}
        if not ids:
            raise KeyError((token,namespace))
        if len(ids)!=1:
            raise AmbiguousTerm(f'{token!r} has meanings {sorted(ids)}; supply namespace')
        return next(iter(ids))

    def parse(self, sentence, namespace='grammar'):
        """Parse a comma-separated declaration of the nine-symbol dependency spine."""
        ids=[self.resolve(t.strip(),namespace) for t in sentence.split(',')]
        expected=[t.id for t in TERMS if t.namespace=='grammar']
        if ids != expected:
            raise ValueError('Expected the declared nine-symbol spine in source order')
        return {'kind':'dependency_spine','terms':ids,
                'execution':'M(I(Λ @ Γ**n @ x)); Ω is a parallel readout'}

    def manifest(self):
        return {'schema':'E47-LEXICAL-ATTRACTOR-1.0','normalization':'N(N(s))=N(s)',
                'terms':[asdict(t) for t in self.terms.values()]}

@dataclass(frozen=True)
class Space:
    field: str = 'complex'
    dimension: int = 125
    construction: str = 'V2 tensor V2 tensor V2'

@dataclass(frozen=True)
class Operators:
    C: np.ndarray
    K: np.ndarray
    Ψ: np.ndarray
    Γ: np.ndarray
    Λ: np.ndarray
    I_identity: np.ndarray
    epsilon: float

def build_operators(epsilon=Fraction(1,99144)):
    ε=float(epsilon)
    if not np.isfinite(ε) or not 0 < ε < 1/93312:
        raise ValueError('Need 0 < epsilon < 1/93312')
    m=np.arange(2,-3,-1,dtype=float)
    jp=np.zeros((5,5),complex)
    for col in range(1,5):
        jp[col-1,col]=np.sqrt(6-m[col]*(m[col]+1))
    generators=((jp+jp.conj().T)/2,(jp-jp.conj().T)/(2j),np.diag(m))
    e=np.eye(5)
    def k3(a,b,c): return np.kron(np.kron(a,b),c)
    total=[k3(g,e,e)+k3(e,g,e)+k3(e,e,g) for g in generators]
    C=sum(g@g for g in total)
    I_identity=np.eye(125,dtype=complex)
    K=(C-6*I_identity)@(C-30*I_identity)
    w,v=np.linalg.eigh(C)
    mask=np.isclose(w,6,atol=1e-10,rtol=0)|np.isclose(w,30,atol=1e-10,rtol=0)
    Ψ=v[:,mask]
    Λ=Ψ@Ψ.conj().T
    Γ=I_identity-ε*(K.conj().T@K)
    return Operators(C,K,Ψ,Γ,Λ,I_identity,ε)

def finite_state(x):
    a=np.array(x,dtype=complex,copy=True)
    if a.shape != (125,) or not np.all(np.isfinite(a)):
        raise ValueError('Expected finite complex state of shape (125,)')
    return a

def recursive_step(x, *, I, M, operators=None, iterations=220):
    """I and M must be supplied: interpretation and regeneration remain local.

    K defines the survivor; it is NOT applied to x ahead of contraction.
    Ω measures coherence; it is NOT a Boolean permission gate.
    """
    if isinstance(iterations,bool) or not isinstance(iterations,int) or iterations<0:
        raise ValueError('iterations must be a nonnegative integer')
    op=operators if operators is not None else build_operators()
    x=finite_state(x)
    Γ,Λ,K,Ψ=op.Γ,op.Λ,op.K,op.Ψ
    y=np.linalg.matrix_power(Γ,iterations)@x
    locked=Λ@y
    def Ω(state):
        state=finite_state(state)
        norm=float(np.vdot(state,state).real)
        if norm == 0: raise ValueError('Coherence is undefined for the zero state')
        p=Λ@state
        return float(np.vdot(p,p).real/norm)
    readout=I(locked.copy())
    Σ_next=finite_state(M(readout))
    result={
        'Σ':Space(), 'K':K, 'Ψ':Ψ, 'Γ':Γ, 'Λ':Λ,
        'Ω':Ω, 'I':I, 'M':M,
        'Σ′':Σ_next, 'Σ_next':Σ_next,
        'I_identity':op.I_identity, 'Ω_c':Fraction(47,125),
        'input':x, 'contracted':y, 'locked':locked, 'readout':readout,
        'kernel_residual':float(np.linalg.norm(K@locked)),
    }
    return result

def next_state_record(result):
    """JSON-safe alias pair. Object identity is retained before JSON serialization."""
    if result['Σ′'] is not result['Σ_next']:
        raise ValueError('Next-state aliases must reference the same object')
    a=finite_state(result['Σ_next'])
    encoded={'real':a.real.tolist(),'imag':a.imag.tolist(),'shape':[125]}
    return {'Σ′':encoded,'Σ_next':encoded}
