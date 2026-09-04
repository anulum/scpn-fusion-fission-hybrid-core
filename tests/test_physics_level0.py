# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — level-0 physics record tests

"""Every branch of the level-0 physics record and its anchors.

The anchor tests build a record and recover from it the numbers
ORNL/PPA-79/3 prints, which is a stronger statement than storing those
numbers beside it. Nothing here describes any real machine.
"""

from __future__ import annotations

import hashlib
import json
import math

import pytest

from physics_fixtures import (
    DD_PRINTED_OFFLINE_RATIO,
    DD_PRINTED_SELF_SUFFICIENT_Q,
    DD_PRINTED_THERMAL_COEFFICIENT,
    TABLE_1_ROWS,
    dd_molten_salt_inputs,
    reference_inputs,
    synthetic_configuration,
    table_1_inputs,
)
from scpn_fusion_fission_hybrid_core.errors import DeviceConfigurationError
from scpn_fusion_fission_hybrid_core.physics import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    HybridInputs,
    level0_physics,
)


@pytest.mark.parametrize(
    ("field", "override"),
    [
        ("breeding_rate", {"breeding_rate": 0.0}),
        ("energy_multiplication", {"energy_multiplication": -1.0}),
        ("engineering_q", {"engineering_q": math.nan}),
        ("conversion_ratio", {"conversion_ratio": 1.0}),
        ("capture_fission_ratio", {"capture_fission_ratio": -0.1}),
        ("thermal_efficiency", {"thermal_efficiency": 1.5}),
        ("neutron_fraction", {"neutron_fraction": 0.0}),
        ("fusion_energy_mev", {"fusion_energy_mev": 0.0}),
        ("fission_energy_mev", {"fission_energy_mev": math.inf}),
    ],
)
def test_declared_inputs_are_refused_by_name_at_construction(
    field: str, override: dict[str, float]
) -> None:
    """A record can never be built from a set the relations would refuse.

    The inputs are validated where they are declared, not only where they
    are used, so the rejection names the field rather than surfacing from
    inside an arithmetic expression.
    """
    good = {
        "breeding_rate": 1.0,
        "energy_multiplication": 2.0,
        "engineering_q": 2.0,
        "conversion_ratio": 0.5,
        "capture_fission_ratio": 0.25,
        "thermal_efficiency": 0.4,
    }
    with pytest.raises(DeviceConfigurationError, match=field):
        HybridInputs(**{**good, **override})


def test_the_reference_record_composes_the_synthetic_configuration() -> None:
    """The record carries the configuration's digest and its source rate."""
    configuration = synthetic_configuration()
    record = level0_physics(configuration, reference_inputs())
    assert record.configuration_digest_sha256 == configuration.digest_sha256()
    assert record.operating_point.fissile_production_per_s == (
        configuration.source.source_rate_per_s
    )


def test_the_two_multiplications_are_reported_separately() -> None:
    """The blanket's neutron multiplication is the configuration's, not the input.

    The declared energy multiplication and ``1 / (1 - k_eff)`` are
    different quantities. The record reports both and derives neither from
    the other, which this test states by moving one and watching the other
    stand still.
    """
    inputs = reference_inputs()
    point = level0_physics(synthetic_configuration(k_effective=0.8), inputs)
    assert point.operating_point.blanket_neutron_multiplication == pytest.approx(5.0)
    assert inputs.energy_multiplication == 2.0
    other = level0_physics(synthetic_configuration(k_effective=0.5), inputs)
    assert other.operating_point.blanket_neutron_multiplication == pytest.approx(2.0)
    assert (
        other.operating_point.thermal_power_ratio
        == point.operating_point.thermal_power_ratio
    )


def test_the_record_recovers_the_coefficient_printed_in_equation_17() -> None:
    """The printed 1.33 is recoverable from a built record.

    The record stores the thermal power ratio, not the coefficient; the
    coefficient is what remains once the driver term is removed.
    """
    point = level0_physics(
        synthetic_configuration(), dd_molten_salt_inputs()
    ).operating_point
    assert point.thermal_power_ratio - 1.0 / DD_PRINTED_SELF_SUFFICIENT_Q == (
        DD_PRINTED_THERMAL_COEFFICIENT
    )


def test_the_record_recovers_the_offline_ratio_printed_in_equation_19() -> None:
    """The printed R_o = 68 is recoverable from a built record."""
    point = level0_physics(
        synthetic_configuration(), dd_molten_salt_inputs()
    ).operating_point
    assert round(point.offline_capacity_ratio) == DD_PRINTED_OFFLINE_RATIO


def test_the_record_recovers_the_printed_self_sufficiency_point() -> None:
    """At the printed Q' the molten-salt hybrid is electrically self-sufficient.

    The report states that Q' ~ 1.4 gives a hybrid electrical efficiency
    of zero. The record built at that Q' carries an efficiency of six
    parts in ten thousand, which rounds to the printed zero, and the
    recirculating share accounts for essentially the whole of the plant's
    thermal efficiency.
    """
    point = level0_physics(
        synthetic_configuration(), dd_molten_salt_inputs()
    ).operating_point
    assert abs(point.hybrid_electrical_efficiency) < 1e-3
    assert point.recirculating_power_fraction == pytest.approx(0.35, abs=1e-3)


def test_the_fraction_of_ultimate_depends_only_on_the_driver_blanket_product() -> None:
    """The record's own two reactor numbers stand in a closed relation.

    ``N / N_ultimate`` is ``Q' B / (1 + Q' B)`` with ``B`` the blanket
    term, so two rows of Table 1 evaluated at Q' inversely proportional to
    their ``B`` sit at the same fraction of their own ceilings, however
    different those ceilings are.
    """
    fractions = []
    ceilings = []
    for name, _, multiplication, _, _ in TABLE_1_ROWS:
        term = 1.0 + 0.8 * (multiplication - 1.0)
        point = level0_physics(
            synthetic_configuration(), table_1_inputs(name, 9.0 / term)
        ).operating_point
        fractions.append(point.supported_fraction_of_ultimate)
        ceilings.append(point.ultimate_supported_fission_reactors)
    for fraction in fractions:
        assert math.isclose(fraction, 0.9, rel_tol=1e-12)
    assert max(ceilings) / min(ceilings) > 4.0


def test_the_supported_number_stays_below_its_own_ceiling() -> None:
    """No finite driver reaches the ceiling."""
    for name, _, _, _, _ in TABLE_1_ROWS:
        point = level0_physics(
            synthetic_configuration(), table_1_inputs(name, 5.0)
        ).operating_point
        assert 0.0 < point.supported_fraction_of_ultimate < 1.0
        assert (
            point.supported_fission_reactors < point.ultimate_supported_fission_reactors
        )


def test_the_online_ratio_falls_below_the_offline_one() -> None:
    """The record states the cost of generating electricity on-line."""
    point = level0_physics(
        synthetic_configuration(), table_1_inputs("thorium_fresh", 5.0)
    ).operating_point
    assert point.online_capacity_ratio > point.offline_capacity_ratio
    assert point.online_capacity_ratio - point.offline_capacity_ratio < (
        point.thermal_power_ratio
    )


def test_the_record_projects_every_field_it_carries() -> None:
    """The projection loses nothing the operating point holds."""
    record = level0_physics(synthetic_configuration(), reference_inputs())
    projected = record.to_record()
    point = projected["operating_point"]
    assert set(point) == set(record.operating_point.__slots__)
    assert projected["schema"] == LEVEL0_SCHEMA
    assert projected["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert projected["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert projected["configuration_digest_sha256"] == (
        record.configuration_digest_sha256
    )


def test_the_canonical_bytes_are_canonical() -> None:
    """Sorted keys, minimal separators, one trailing newline, and idempotent.

    Idempotence is the property that matters: re-canonicalising the parsed
    bytes reproduces them exactly. Asserting the absence of a separator
    would be wrong here, because the non-claims are English prose that
    contains commas of its own.
    """
    record = level0_physics(synthetic_configuration(), reference_inputs())
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    parsed = json.loads(data)
    again = json.dumps(parsed, sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert (again + "\n").encode("utf-8") == data


def test_the_digest_identifies_the_record() -> None:
    """The digest is the SHA-256 of the canonical bytes and moves with them."""
    record = level0_physics(synthetic_configuration(), reference_inputs())
    assert (
        record.digest_sha256() == hashlib.sha256(record.canonical_bytes()).hexdigest()
    )
    moved = level0_physics(
        synthetic_configuration(source_rate_per_s=2.0e19), reference_inputs()
    )
    assert moved.digest_sha256() != record.digest_sha256()


def test_the_anchor_row_names_are_the_ones_the_fixtures_offer() -> None:
    """An unknown row name is refused rather than silently substituted."""
    with pytest.raises(KeyError, match="deuterium_blanket"):
        table_1_inputs("deuterium_blanket", 2.0)
