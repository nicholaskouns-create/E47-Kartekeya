"""Tests for SU(2) spectral-kernel compilation."""

from __future__ import annotations

import json

import pytest

from e47.spectral_compilation import (
    compile_spectral_kernel,
    parse_spin,
    spectral_passport,
    write_spectral_compilation,
)


def test_compile_spectral_kernel_canonical_certificate() -> None:
    """The canonical spin-2 triple tensor product reproduces E47 data."""

    compilation = compile_spectral_kernel(
        parse_spin("2"),
        3,
        [parse_spin("2"), parse_spin("5")],
    )

    assert compilation.carrier_dimension == 125
    assert compilation.multiplicities == {
        "0": 1,
        "1": 3,
        "2": 5,
        "3": 4,
        "4": 3,
        "5": 2,
        "6": 1,
    }
    assert compilation.casimir_spectrum == (
        parse_spin("0"),
        parse_spin("2"),
        parse_spin("6"),
        parse_spin("12"),
        parse_spin("20"),
        parse_spin("30"),
        parse_spin("42"),
    )
    assert compilation.selected_spins == (parse_spin("2"), parse_spin("5"))
    assert compilation.selected_dimension == 47
    assert compilation.coherence_fraction == parse_spin("47/125")
    assert compilation.kernel_roots == (parse_spin("6"), parse_spin("30"))
    assert compilation.kernel_polynomial_coefficients == (
        parse_spin("1"),
        parse_spin("-36"),
        parse_spin("180"),
    )
    assert compilation.q_spectrum == (
        parse_spin("0"),
        parse_spin("11664"),
        parse_spin("12544"),
        parse_spin("19600"),
        parse_spin("32400"),
        parse_spin("186624"),
    )
    assert compilation.spectral_gap == parse_spin("11664")
    assert compilation.maximum_q_eigenvalue == parse_spin("186624")
    assert compilation.epsilon_max == parse_spin("1/93312")
    assert compilation.optimal_epsilon == parse_spin("1/99144")
    assert compilation.optimal_rate == parse_spin("583/656")
    assert compilation.numerical_residuals["matrix_rank_projector"] == 47.0
    assert compilation.numerical_residuals["casimir_hermiticity"] < 1e-10
    assert compilation.numerical_residuals["projector_idempotence"] < 1e-10
    assert compilation.numerical_residuals["projector_hermiticity"] < 1e-10
    assert compilation.numerical_residuals["kernel_projector_annihilation"] < 1e-8
    assert compilation.numerical_residuals["channel_completeness"] < 1e-10


def test_compile_spectral_kernel_without_matrix_witness() -> None:
    """The exact combinatorial certificate works without matrix diagnostics."""

    compilation = compile_spectral_kernel(
        parse_spin("2"),
        3,
        [parse_spin("2"), parse_spin("5")],
        build_matrix_witness=False,
    )

    assert compilation.numerical_residuals == {}


def test_compile_spectral_kernel_rejects_full_selection() -> None:
    """Selecting every sector leaves no complementary spectral gap."""

    with pytest.raises(
        ValueError,
        match="selected sectors span the entire carrier",
    ):
        compile_spectral_kernel(
            parse_spin("1/2"),
            2,
            [parse_spin("0"), parse_spin("1")],
            build_matrix_witness=False,
        )


def test_write_spectral_compilation_outputs_files(tmp_path) -> None:
    """The certificate writer emits both JSON and passport artifacts."""

    compilation = compile_spectral_kernel(
        parse_spin("2"),
        3,
        [parse_spin("2"), parse_spin("5")],
        build_matrix_witness=False,
    )

    certificate = tmp_path / "certificate.json"
    passport = tmp_path / "passport.md"
    written_certificate, written_passport = write_spectral_compilation(
        compilation,
        certificate,
        passport,
    )

    assert written_certificate == certificate
    assert written_passport == passport
    payload = json.loads(certificate.read_text(encoding="utf-8"))
    assert payload["spin"] == {"numerator": 2, "denominator": 1}
    assert payload["coherence_fraction"] == {"numerator": 47, "denominator": 125}
    assert payload["selected_spins"] == [
        {"numerator": 2, "denominator": 1},
        {"numerator": 5, "denominator": 1},
    ]
    assert "Spectral gap of Q = K†K: 11664" in passport.read_text(encoding="utf-8")


def test_spectral_passport_reports_selected_sectors() -> None:
    """The passport contains the key human-readable summary values."""

    compilation = compile_spectral_kernel(
        parse_spin("2"),
        3,
        [parse_spin("2"), parse_spin("5")],
        build_matrix_witness=False,
    )

    passport = spectral_passport(compilation)

    assert "Carrier: spin-2 tensor power 3" in passport
    assert "Selected total-spin sectors: 2, 5" in passport
    assert "Machine status: PASS" in passport
