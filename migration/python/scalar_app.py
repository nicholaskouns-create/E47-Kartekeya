r"""
SCALAR
Algebraic Quantum Scalar Fields
===============================

Interactive Dash visualizer for the finite E47 spectral core and a deterministic
scalar-field visualization lift.

Finite algebra (machine-checkable):
    V = V_2^{\otimes 3}, dim V = 125
    C = J_tot^2
    K = (C - 6 I)(C - 30 I)
    E47 = ker K = E_6 ⊕ E_30
    P47 = orthogonal spectral projector onto E47
    Omega_c = Tr(P47) / 125 = 47 / 125
    Gamma_eps = I - eps K^2

Continuum visualization convention:
    L := -Delta
    K_field := (L - 6)(L - 30)

Every plane-wave component used by the visual lift is assigned |k|^2 equal to
its Casimir eigenvalue lambda, so L exp(i k·x) = lambda exp(i k·x).
The E47 terminal field therefore contains only lambda = 6 and lambda = 30
shells and satisfies K_field phi = 0 term-by-term.

This continuum plane-wave lift is a visualization map from the finite algebra.
It is not asserted here to be a uniquely derived physical spacetime model.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html


# =============================================================================
# 0. Canonical constants
# =============================================================================

J = 2
LOCAL_DIM = 2 * J + 1
DIM = LOCAL_DIM ** 3

TARGET_EIGENVALUES = (6.0, 30.0)
OMEGA_C = 47 / 125

EPS_STAR = 1 / 99144
EPS_STABILITY_MAX = 1 / 93312

REFERENCE_CERTIFICATE = "MC-AQSFT-E47-20260825"
REFERENCE_CERT_SHA256 = (
    "f4ab4b046e3da00e71db7105972209e1027a21e5aa2af72035a283476dde5dfc"
)

GRID_N = 58
DEFAULT_SEED = 470125


# =============================================================================
# 1. SPECTRAL CORE
# =============================================================================

def spin_matrices(j: int = 2):
    """Return the standard spin-j generators Jx, Jy, Jz."""
    m = np.arange(j, -j - 1, -1, dtype=float)
    d = len(m)

    J_plus = np.zeros((d, d), dtype=complex)
    for col in range(1, d):
        m_col = m[col]
        J_plus[col - 1, col] = np.sqrt(
            j * (j + 1) - m_col * (m_col + 1)
        )

    J_minus = J_plus.conj().T
    Jx = 0.5 * (J_plus + J_minus)
    Jy = (J_plus - J_minus) / (2j)
    Jz = np.diag(m)
    return Jx, Jy, Jz


def embed_local(op: np.ndarray, site: int) -> np.ndarray:
    """Embed a 5x5 local operator into one site of V_2^{tensor 3}."""
    ident = np.eye(LOCAL_DIM, dtype=complex)
    ops = [ident, ident, ident]
    ops[site] = op
    return np.kron(np.kron(ops[0], ops[1]), ops[2])


@dataclass(frozen=True)
class SpectralCore:
    C: np.ndarray
    K: np.ndarray
    K2: np.ndarray
    P47: np.ndarray
    evals: np.ndarray
    evecs: np.ndarray
    k_eigs: np.ndarray
    k2_eigs: np.ndarray
    kernel_mask: np.ndarray
    sector_values: np.ndarray
    sector_dims: np.ndarray
    audit: dict


def build_spectral_core() -> SpectralCore:
    Jx, Jy, Jz = spin_matrices(J)

    Jx_tot = sum(embed_local(Jx, s) for s in range(3))
    Jy_tot = sum(embed_local(Jy, s) for s in range(3))
    Jz_tot = sum(embed_local(Jz, s) for s in range(3))

    C = Jx_tot @ Jx_tot + Jy_tot @ Jy_tot + Jz_tot @ Jz_tot
    ident = np.eye(DIM, dtype=complex)
    K = (C - 6 * ident) @ (C - 30 * ident)
    K2 = K @ K

    evals, evecs = np.linalg.eigh(C)
    kernel_mask = (
        np.isclose(evals, 6.0, atol=1e-9)
        | np.isclose(evals, 30.0, atol=1e-9)
    )

    kernel_basis = evecs[:, kernel_mask]
    P47 = kernel_basis @ kernel_basis.conj().T

    k_eigs = (evals - 6.0) * (evals - 30.0)
    k2_eigs = k_eigs ** 2

    sector_values = np.array([0, 2, 6, 12, 20, 30, 42], dtype=float)
    sector_dims = np.array(
        [np.count_nonzero(np.isclose(evals, lam, atol=1e-8))
         for lam in sector_values],
        dtype=int,
    )

    positive_k2 = k2_eigs[k2_eigs > 1e-8]
    spectral_gap = float(np.min(positive_k2))
    spectral_norm = float(np.max(k2_eigs))

    gamma_eigs = 1.0 - EPS_STAR * k2_eigs
    complement_radius = float(
        np.max(np.abs(gamma_eigs[~kernel_mask]))
    )

    audit = {
        "carrier_dimension": DIM,
        "sector_dimensions": sector_dims.tolist(),
        "kernel_dimension": int(np.count_nonzero(kernel_mask)),
        "omega_c": float(np.trace(P47).real / DIM),
        "C_hermiticity": float(np.linalg.norm(C - C.conj().T)),
        "K_hermiticity": float(np.linalg.norm(K - K.conj().T)),
        "P47_hermiticity": float(np.linalg.norm(P47 - P47.conj().T)),
        "P47_idempotence": float(np.linalg.norm(P47 @ P47 - P47)),
        "KP47": float(np.linalg.norm(K @ P47)),
        "P47_trace": float(np.trace(P47).real),
        "spectral_gap_K2": spectral_gap,
        "spectral_norm_K2": spectral_norm,
        "epsilon_star": EPS_STAR,
        "epsilon_stability_max": EPS_STABILITY_MAX,
        "complement_spectral_radius_at_epsilon_star": complement_radius,
    }

    # Startup invariants.
    assert DIM == 125
    assert sector_dims.tolist() == [1, 9, 25, 28, 27, 22, 13]
    assert audit["kernel_dimension"] == 47
    assert np.isclose(audit["omega_c"], OMEGA_C, atol=1e-12)
    assert audit["P47_idempotence"] < 1e-10
    assert audit["KP47"] < 1e-8
    assert np.isclose(spectral_gap, 11664.0, atol=1e-6)
    assert np.isclose(spectral_norm, 186624.0, atol=1e-6)
    assert np.isclose(complement_radius, 15 / 17, atol=1e-12)

    return SpectralCore(
        C=C,
        K=K,
        K2=K2,
        P47=P47,
        evals=evals,
        evecs=evecs,
        k_eigs=k_eigs,
        k2_eigs=k2_eigs,
        kernel_mask=kernel_mask,
        sector_values=sector_values,
        sector_dims=sector_dims,
        audit=audit,
    )


CORE = build_spectral_core()


# =============================================================================
# 2. ALGEBRAIC -> SCALAR FIELD VISUALIZATION LIFT
# =============================================================================

def fibonacci_directions(n: int) -> np.ndarray:
    """
    Deterministic directions on S^2.

    The direction assignment is only a visualization embedding. Each direction
    is rescaled so |k_i|^2 = lambda_i, preserving the Casimir eigenvalue as the
    eigenvalue of L = -Delta for the corresponding plane wave.
    """
    idx = np.arange(n, dtype=float)
    z = 1.0 - 2.0 * (idx + 0.5) / n
    golden_angle = np.pi * (3.0 - np.sqrt(5.0))
    theta = golden_angle * idx
    r = np.sqrt(np.maximum(0.0, 1.0 - z * z))

    dirs = np.column_stack((r * np.cos(theta), r * np.sin(theta), z))
    return dirs


DIRECTIONS = fibonacci_directions(DIM)
K_VECTORS = DIRECTIONS * np.sqrt(np.maximum(CORE.evals, 0.0))[:, None]

axis = np.linspace(-np.pi, np.pi, GRID_N)
X_GRID, Y_GRID = np.meshgrid(axis, axis)
PHASE_XY = (
    K_VECTORS[:, 0, None, None] * X_GRID[None, :, :]
    + K_VECTORS[:, 1, None, None] * Y_GRID[None, :, :]
)

# Balance visual contribution across Casimir sectors.
MODE_SCALE = np.empty(DIM, dtype=float)
for lam, d in zip(CORE.sector_values, CORE.sector_dims):
    mask = np.isclose(CORE.evals, lam, atol=1e-8)
    MODE_SCALE[mask] = 1.0 / np.sqrt(d)


def seeded_carrier_coefficients(seed: int) -> np.ndarray:
    """Create a deterministic normalized carrier state and express it in C basis."""
    rng = np.random.default_rng(int(seed))
    x = rng.standard_normal(DIM) + 1j * rng.standard_normal(DIM)
    x /= np.linalg.norm(x)
    return CORE.evecs.conj().T @ x


def apply_contraction(
    coeff: np.ndarray,
    epsilon_scale: float,
    iterations: int,
) -> np.ndarray:
    """
    Apply Gamma_epsilon^n in the Casimir eigenbasis.

        Gamma_epsilon = I - epsilon K^2

    epsilon_scale is restricted by the UI to (0, 1], so epsilon never exceeds
    epsilon_star and therefore remains within the certified stability interval.
    """
    eps = float(epsilon_scale) * EPS_STAR
    factors = 1.0 - eps * CORE.k2_eigs
    return coeff * (factors ** int(iterations))


def filtered_coefficients(coeff: np.ndarray, view: str) -> np.ndarray:
    if view == "e47":
        return coeff * CORE.kernel_mask
    if view == "transverse":
        return coeff * (~CORE.kernel_mask)
    if view == "residual":
        # Normalize K by its largest absolute eigenvalue for a readable surface.
        return coeff * (CORE.k_eigs / np.max(np.abs(CORE.k_eigs)))
    return coeff


def scalar_field(
    coeff: np.ndarray,
    phase: float,
    z_slice: float,
    view: str,
) -> np.ndarray:
    """
    Build a real scalar field on a 2D slice through R^3:

        phi(x,y,z) = Re sum_i a_i s_i exp(i k_i · r)

    with |k_i|^2 = lambda_i.

    At the E47 limit only lambda=6,30 terms remain, hence
        ((-Delta)-6)((-Delta)-30) phi = 0
    term-by-term.
    """
    c = filtered_coefficients(coeff, view) * MODE_SCALE
    phase_tensor = (
        PHASE_XY
        + K_VECTORS[:, 2, None, None] * float(z_slice)
        + float(phase)
    )
    waves = np.exp(1j * phase_tensor)
    phi = np.real(np.sum(c[:, None, None] * waves, axis=0))
    return phi


# =============================================================================
# 3. SCALAR POTENTIAL / CURVATURE GEOMETRY
# =============================================================================

def scalar_potential(rho: np.ndarray):
    """
    Octic potential centered at Omega_c, as archived in the scalar-field corpus.

    y = rho - Omega_c
    f(y) =
      34749/1024 y^8
      - 81081/1280 y^6
      + 18711/512 y^4
      - 1701/256 y^2
      + 3/40 y
      + 957/1024
    """
    y = rho - OMEGA_C

    a8 = 34749 / 1024
    a6 = -81081 / 1280
    a4 = 18711 / 512
    a2 = -1701 / 256
    a1 = 3 / 40
    a0 = 957 / 1024

    f = a8*y**8 + a6*y**6 + a4*y**4 + a2*y**2 + a1*y + a0
    fp = 8*a8*y**7 + 6*a6*y**5 + 4*a4*y**3 + 2*a2*y + a1
    fpp = 56*a8*y**6 + 30*a6*y**4 + 12*a4*y**2 + 2*a2
    return f, fp, fpp


# =============================================================================
# 4. DIAGNOSTICS / AUDIT
# =============================================================================

def sector_energies(coeff: np.ndarray) -> np.ndarray:
    energies = []
    for lam in CORE.sector_values:
        mask = np.isclose(CORE.evals, lam, atol=1e-8)
        energies.append(float(np.sum(np.abs(coeff[mask]) ** 2)))
    return np.array(energies)


def state_metrics(coeff: np.ndarray) -> dict:
    norm2 = float(np.sum(np.abs(coeff) ** 2))
    kernel_mass = float(np.sum(np.abs(coeff[CORE.kernel_mask]) ** 2))
    transverse_mass = float(np.sum(np.abs(coeff[~CORE.kernel_mask]) ** 2))
    residual = float(np.linalg.norm(CORE.k_eigs * coeff))
    occupancy = kernel_mass / norm2 if norm2 > 0 else 0.0

    packed = np.concatenate(
        [np.round(coeff.real, 12), np.round(coeff.imag, 12)]
    ).astype(np.float64)
    run_hash = hashlib.sha256(packed.tobytes()).hexdigest()

    return {
        "norm2": norm2,
        "kernel_mass": kernel_mass,
        "transverse_mass": transverse_mass,
        "kernel_occupancy_Q": occupancy,
        "K_residual_norm": residual,
        "run_sha256": run_hash,
    }


def coeff_to_payload(coeff: np.ndarray, step: int, seed: int) -> dict:
    return {
        "step": int(step),
        "seed": int(seed),
        "coeff_real": coeff.real.tolist(),
        "coeff_imag": coeff.imag.tolist(),
    }


def payload_to_coeff(payload: dict) -> np.ndarray:
    return (
        np.asarray(payload["coeff_real"], dtype=float)
        + 1j * np.asarray(payload["coeff_imag"], dtype=float)
    )


# =============================================================================
# 5. PLOTLY FIGURES
# =============================================================================

BG = "#090B10"
PANEL = "#11151D"
TEXT = "#F2F5F7"
MUTED = "#9BA7B4"
ACCENT = "#6DE2D0"
ACCENT_2 = "#C7A7FF"
WARN = "#FFB86B"
GRID = "#252B35"


def make_field_figure(
    coeff: np.ndarray,
    phase: float,
    z_slice: float,
    view: str,
    step: int,
):
    phi = scalar_field(coeff, phase, z_slice, view)
    vmax = max(float(np.max(np.abs(phi))), 1e-12)

    labels = {
        "full": "Full algebraic scalar field",
        "e47": "E47 invariant field: lambda = 6 and 30",
        "transverse": "Transverse field: complement of E47",
        "residual": "Normalized field residual K_field phi",
    }

    fig = go.Figure(
        data=[
            go.Surface(
                x=X_GRID,
                y=Y_GRID,
                z=phi,
                surfacecolor=phi,
                colorscale="RdBu",
                cmin=-vmax,
                cmax=vmax,
                colorbar=dict(title="phi"),
                contours=dict(
                    z=dict(show=True, usecolormap=True, project_z=True)
                ),
                lighting=dict(
                    ambient=0.55,
                    diffuse=0.75,
                    roughness=0.75,
                    specular=0.15,
                ),
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{labels[view]}</b><br><sup>contraction step {step}</sup>",
            x=0.02,
        ),
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=0, r=0, t=70, b=0),
        scene=dict(
            xaxis=dict(title="x", gridcolor=GRID),
            yaxis=dict(title="y", gridcolor=GRID),
            zaxis=dict(title="phi(x,y,z)", gridcolor=GRID),
            camera=dict(eye=dict(x=1.55, y=-1.55, z=1.12)),
            bgcolor=PANEL,
        ),
        uirevision="scalar-field-camera",
    )
    return fig


def make_spectrum_figure(coeff: np.ndarray):
    energies = sector_energies(coeff)
    labels = [str(int(x)) for x in CORE.sector_values]
    colors = [
        ACCENT if lam in TARGET_EIGENVALUES else WARN
        for lam in CORE.sector_values
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=energies,
            marker_color=colors,
            text=[f"{e:.3e}" for e in energies],
            textposition="outside",
            cliponaxis=False,
        )
    )
    fig.update_layout(
        title="<b>Casimir shell population</b><br><sup>green = E47 shells</sup>",
        xaxis_title="Casimir eigenvalue lambda",
        yaxis_title="sum |a_lambda|^2",
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=55, r=20, t=70, b=55),
        yaxis=dict(gridcolor=GRID),
        xaxis=dict(gridcolor=GRID),
    )
    return fig


def make_potential_figure():
    rho = np.linspace(0.0, 1.15, 700)
    f, fp, fpp = scalar_potential(rho)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rho, y=f, name="f(rho - Omega_c)", mode="lines"))
    fig.add_trace(go.Scatter(x=rho, y=fp, name="f' sensitivity", mode="lines"))
    fig.add_trace(go.Scatter(x=rho, y=fpp, name="f'' Hessian", mode="lines"))
    fig.add_vline(
        x=OMEGA_C,
        line_dash="dash",
        annotation_text="Omega_c = 47/125",
        annotation_position="top",
    )
    fig.update_layout(
        title="<b>Scalar potential / gradient / Hessian</b>",
        xaxis_title="rho",
        yaxis_title="value",
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=60, r=20, t=70, b=55),
        yaxis=dict(gridcolor=GRID),
        xaxis=dict(gridcolor=GRID),
        legend=dict(orientation="h", y=1.08),
    )
    return fig


# =============================================================================
# 6. DASH UI
# =============================================================================

def metric_card(label: str, value: str, detail: str = ""):
    return html.Div(
        [
            html.Div(label, style={"fontSize": "12px", "color": MUTED}),
            html.Div(
                value,
                style={
                    "fontSize": "25px",
                    "fontWeight": "700",
                    "letterSpacing": "-0.02em",
                    "marginTop": "3px",
                },
            ),
            html.Div(detail, style={"fontSize": "11px", "color": MUTED}),
        ],
        style={
            "background": PANEL,
            "border": f"1px solid {GRID}",
            "borderRadius": "14px",
            "padding": "14px 16px",
            "minWidth": "150px",
            "flex": "1",
        },
    )


def control_label(text):
    return html.Div(
        text,
        style={
            "fontSize": "11px",
            "letterSpacing": "0.08em",
            "textTransform": "uppercase",
            "color": MUTED,
            "marginBottom": "7px",
        },
    )


INITIAL_COEFF = seeded_carrier_coefficients(DEFAULT_SEED)

app = Dash(__name__)
app.title = "Scalar · Algebraic Quantum Scalar Fields"

app.layout = html.Div(
    style={
        "backgroundColor": BG,
        "color": TEXT,
        "fontFamily": "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
        "minHeight": "100vh",
        "padding": "24px",
    },
    children=[
        dcc.Store(
            id="state-store",
            data=coeff_to_payload(INITIAL_COEFF, 0, DEFAULT_SEED),
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "THE MATHEMATICAL CITY · MINI AI LAB",
                            style={
                                "fontSize": "11px",
                                "letterSpacing": "0.16em",
                                "color": ACCENT,
                                "fontWeight": "700",
                            },
                        ),
                        html.H1(
                            "SCALAR",
                            style={
                                "fontSize": "54px",
                                "margin": "6px 0 0 0",
                                "letterSpacing": "-0.04em",
                            },
                        ),
                        html.Div(
                            "Algebraic Quantum Scalar Fields",
                            style={
                                "fontSize": "20px",
                                "color": MUTED,
                                "marginTop": "-4px",
                            },
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            "What scalar field survives the algebra?",
                            style={
                                "fontWeight": "700",
                                "fontSize": "18px",
                                "textAlign": "right",
                            },
                        ),
                        html.Div(
                            "V₂⊗³ → C → K → E₄₇ → P₄₇ → φ",
                            style={
                                "fontFamily": "ui-monospace, SFMono-Regular, monospace",
                                "color": ACCENT_2,
                                "marginTop": "6px",
                                "textAlign": "right",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "end",
                "gap": "20px",
                "maxWidth": "1500px",
                "margin": "0 auto 20px auto",
            },
        ),

        html.Div(
            id="metrics",
            style={
                "display": "flex",
                "gap": "10px",
                "flexWrap": "wrap",
                "maxWidth": "1500px",
                "margin": "0 auto 14px auto",
            },
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        control_label("Field view"),
                                        dcc.Dropdown(
                                            id="view-select",
                                            options=[
                                                {"label": "Full field", "value": "full"},
                                                {"label": "E47 invariant field", "value": "e47"},
                                                {"label": "Transverse field", "value": "transverse"},
                                                {"label": "K-field residual", "value": "residual"},
                                            ],
                                            value="full",
                                            clearable=False,
                                            style={"color": "#111"},
                                        ),
                                    ],
                                    style={"minWidth": "210px", "flex": "1.25"},
                                ),
                                html.Div(
                                    [
                                        control_label("Seed"),
                                        dcc.Input(
                                            id="seed-input",
                                            type="number",
                                            value=DEFAULT_SEED,
                                            step=1,
                                            style={
                                                "width": "100%",
                                                "height": "36px",
                                                "borderRadius": "7px",
                                                "border": f"1px solid {GRID}",
                                                "padding": "0 10px",
                                            },
                                        ),
                                    ],
                                    style={"minWidth": "120px", "flex": "0.7"},
                                ),
                                html.Div(
                                    [
                                        control_label("Contraction"),
                                        html.Div(
                                            [
                                                html.Button("1 step", id="step-btn", n_clicks=0),
                                                html.Button("10 steps", id="run10-btn", n_clicks=0),
                                                html.Button("Reset", id="reset-btn", n_clicks=0),
                                            ],
                                            style={
                                                "display": "flex",
                                                "gap": "7px",
                                                "flexWrap": "wrap",
                                            },
                                        ),
                                    ],
                                    style={"minWidth": "260px", "flex": "1.4"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "gap": "16px",
                                "flexWrap": "wrap",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    [
                                        control_label("Global phase"),
                                        dcc.Slider(
                                            id="phase-slider",
                                            min=0,
                                            max=float(2*np.pi),
                                            step=0.05,
                                            value=0.0,
                                            marks={
                                                0: "0",
                                                float(np.pi): "π",
                                                float(2*np.pi): "2π",
                                            },
                                            tooltip={"placement": "bottom"},
                                        ),
                                    ],
                                    style={"flex": "1"},
                                ),
                                html.Div(
                                    [
                                        control_label("z slice"),
                                        dcc.Slider(
                                            id="z-slider",
                                            min=float(-np.pi),
                                            max=float(np.pi),
                                            step=0.05,
                                            value=0.0,
                                            marks={
                                                float(-np.pi): "-π",
                                                0: "0",
                                                float(np.pi): "π",
                                            },
                                            tooltip={"placement": "bottom"},
                                        ),
                                    ],
                                    style={"flex": "1"},
                                ),
                                html.Div(
                                    [
                                        control_label("epsilon / epsilon*"),
                                        dcc.Slider(
                                            id="eps-slider",
                                            min=0.1,
                                            max=1.0,
                                            step=0.05,
                                            value=1.0,
                                            marks={0.1: "0.1", 0.5: "0.5", 1.0: "1.0"},
                                            tooltip={"placement": "bottom"},
                                        ),
                                    ],
                                    style={"flex": "1"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "gap": "22px",
                                "marginTop": "20px",
                                "flexWrap": "wrap",
                            },
                        ),
                    ],
                    style={
                        "background": PANEL,
                        "border": f"1px solid {GRID}",
                        "borderRadius": "16px",
                        "padding": "16px",
                    },
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.B("Finite operator: "),
                                "K = (C - 6I)(C - 30I). ",
                                html.B("Contraction: "),
                                "Γε = I - εK². ",
                                html.B("Field convention: "),
                                "L = -Δ, so the terminal field obeys "
                                "(L - 6)(L - 30)φ = 0.",
                            ],
                            style={"lineHeight": "1.55"},
                        ),
                        html.Div(
                            "The plane-wave lift is an explicit visualization map. "
                            "The finite 125→47 spectral theorem is the audited core; "
                            "continuum/physical interpretation is a separate layer.",
                            style={
                                "fontSize": "12px",
                                "color": MUTED,
                                "marginTop": "8px",
                            },
                        ),
                    ],
                    style={
                        "background": "#0D1820",
                        "border": f"1px solid {ACCENT}55",
                        "borderRadius": "16px",
                        "padding": "15px 17px",
                        "marginTop": "10px",
                    },
                ),
            ],
            style={"maxWidth": "1500px", "margin": "0 auto"},
        ),

        html.Div(
            [
                dcc.Graph(
                    id="scalar-field",
                    style={"height": "690px", "minWidth": "0"},
                    config={"displaylogo": False},
                ),
                dcc.Graph(
                    id="spectrum",
                    style={"height": "690px", "minWidth": "0"},
                    config={"displaylogo": False},
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "minmax(0, 2fr) minmax(330px, 0.9fr)",
                "gap": "12px",
                "maxWidth": "1500px",
                "margin": "12px auto 0 auto",
            },
        ),

        html.Div(
            [
                dcc.Graph(
                    id="potential",
                    figure=make_potential_figure(),
                    style={"height": "460px"},
                    config={"displaylogo": False},
                ),
                html.Div(
                    [
                        html.Div(
                            "AUDIT",
                            style={
                                "fontSize": "11px",
                                "letterSpacing": "0.15em",
                                "fontWeight": "800",
                                "color": ACCENT,
                            },
                        ),
                        html.Pre(
                            id="audit",
                            style={
                                "whiteSpace": "pre-wrap",
                                "fontSize": "12px",
                                "lineHeight": "1.55",
                                "color": TEXT,
                                "marginTop": "12px",
                            },
                        ),
                    ],
                    style={
                        "background": PANEL,
                        "border": f"1px solid {GRID}",
                        "borderRadius": "16px",
                        "padding": "18px",
                    },
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "minmax(0, 1.5fr) minmax(330px, 0.8fr)",
                "gap": "12px",
                "maxWidth": "1500px",
                "margin": "12px auto 0 auto",
            },
        ),

        html.Div(
            [
                html.B("SCALAR · narrow bright use: "),
                "turn a 125-dimensional algebraic state into a visible scalar field, "
                "then watch Γε erase every Casimir shell except λ=6 and λ=30.",
            ],
            style={
                "maxWidth": "1500px",
                "margin": "14px auto 0 auto",
                "padding": "18px",
                "borderTop": f"1px solid {GRID}",
                "color": MUTED,
                "fontSize": "13px",
            },
        ),
    ],
)


# Shared button styling injected after layout construction.
for _id in ("step-btn", "run10-btn", "reset-btn"):
    pass


# =============================================================================
# 7. CALLBACK
# =============================================================================

@app.callback(
    Output("scalar-field", "figure"),
    Output("spectrum", "figure"),
    Output("state-store", "data"),
    Output("metrics", "children"),
    Output("audit", "children"),
    Input("step-btn", "n_clicks"),
    Input("run10-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    Input("phase-slider", "value"),
    Input("z-slider", "value"),
    Input("eps-slider", "value"),
    Input("view-select", "value"),
    State("seed-input", "value"),
    State("state-store", "data"),
)
def update_scalar(
    step_clicks,
    run10_clicks,
    reset_clicks,
    phase,
    z_slice,
    epsilon_scale,
    view,
    seed_value,
    state_data,
):
    del step_clicks, run10_clicks, reset_clicks

    coeff = payload_to_coeff(state_data)
    step = int(state_data["step"])
    active_seed = int(state_data["seed"])

    trigger = ctx.triggered_id

    if trigger == "reset-btn":
        active_seed = int(seed_value if seed_value is not None else DEFAULT_SEED)
        coeff = seeded_carrier_coefficients(active_seed)
        step = 0

    elif trigger == "step-btn":
        coeff = apply_contraction(coeff, epsilon_scale, 1)
        step += 1

    elif trigger == "run10-btn":
        coeff = apply_contraction(coeff, epsilon_scale, 10)
        step += 10

    metrics = state_metrics(coeff)

    cards = [
        metric_card("Carrier", "125", "V₂⊗³"),
        metric_card("Invariant sector", "47", "E₆ ⊕ E₃₀"),
        metric_card("Ωc", f"{OMEGA_C:.3f}", "dim(E47) / dim(V)"),
        metric_card(
            "Q[ψ]",
            f"{metrics['kernel_occupancy_Q']:.5f}",
            "state kernel occupancy",
        ),
        metric_card(
            "Transverse mass",
            f"{metrics['transverse_mass']:.3e}",
            "→ 0 under Γε",
        ),
        metric_card(
            "||Kψ||",
            f"{metrics['K_residual_norm']:.3e}",
            "terminal criterion",
        ),
    ]

    audit_lines = [
        f"Reference certificate : {REFERENCE_CERTIFICATE}",
        f"Reference SHA-256     : {REFERENCE_CERT_SHA256}",
        "",
        f"Tr(P47)               : {CORE.audit['P47_trace']:.12f}",
        f"||P47²-P47||_F        : {CORE.audit['P47_idempotence']:.3e}",
        f"||K P47||_F           : {CORE.audit['KP47']:.3e}",
        f"gap(K²)               : {CORE.audit['spectral_gap_K2']:.0f}",
        f"||K²||₂               : {CORE.audit['spectral_norm_K2']:.0f}",
        f"epsilon*              : {EPS_STAR:.12e}",
        f"rho_perp(epsilon*)    : {CORE.audit['complement_spectral_radius_at_epsilon_star']:.12f}",
        "",
        f"run seed               : {active_seed}",
        f"contraction step       : {step}",
        f"epsilon/epsilon*       : {float(epsilon_scale):.2f}",
        f"||state||²             : {metrics['norm2']:.12f}",
        f"kernel mass            : {metrics['kernel_mass']:.12f}",
        f"transverse mass        : {metrics['transverse_mass']:.12e}",
        f"run SHA-256            : {metrics['run_sha256']}",
    ]

    return (
        make_field_figure(coeff, phase, z_slice, view, step),
        make_spectrum_figure(coeff),
        coeff_to_payload(coeff, step, active_seed),
        cards,
        "\n".join(audit_lines),
    )


# =============================================================================
# 8. SERVER ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    print("SCALAR backend audit")
    print(json.dumps(CORE.audit, indent=2))
    print()
    print("Launch: http://127.0.0.1:8050")
    app.run(debug=True)
