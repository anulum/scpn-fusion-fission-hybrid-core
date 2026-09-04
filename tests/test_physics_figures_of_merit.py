# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — hybrid figures of merit tests

"""Every branch of the hybrid figures of merit, and their anchors.

The anchors reproduce numbers ORNL/PPA-79/3 prints from the inputs it
prints alongside them. Nothing here describes any real machine.
"""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    DD_BREEDING_RATE,
    DD_ENERGY_MULTIPLICATION,
    DD_FUSION_ENERGY_MEV,
    DD_NEUTRON_FRACTION,
    DD_PRINTED_OFFLINE_RATIO,
    DD_PRINTED_SELF_SUFFICIENT_Q,
    DD_PRINTED_THERMAL_COEFFICIENT,
    TABLE_1_ROWS,
    THERMAL_EFFICIENCY,
    U233_CAPTURE_FISSION_RATIO,
    U233_CONVERSION_RATIO,
)
from scpn_fusion_fission_hybrid_core.errors import DeviceConfigurationError
from scpn_fusion_fission_hybrid_core.physics.figures_of_merit import (
    DT_NEUTRON_FRACTION,
    hybrid_electrical_efficiency,
    offline_capacity_ratio,
    online_capacity_ratio,
    require_conversion_ratio,
    require_fraction,
    require_non_negative,
    supported_fission_reactors,
    thermal_power_ratio,
)


def blanket_term(neutron_fraction: float, energy_multiplication: float) -> float:
    """Return the driver-independent part of the thermal power ratio."""
    return 1.0 + neutron_fraction * (energy_multiplication - 1.0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, 0.0, -0.5, 1.5])
def test_require_fraction_refuses_everything_outside_the_unit_interval(
    value: float,
) -> None:
    """The fraction guard names its field and refuses rather than clamps."""
    with pytest.raises(DeviceConfigurationError, match="share"):
        require_fraction("share", value)


@pytest.mark.parametrize("value", [1e-300, 0.5, 1.0])
def test_require_fraction_admits_the_half_open_unit_interval(value: float) -> None:
    """One is admitted, zero is not, and the value passes through unchanged."""
    assert require_fraction("share", value) == value


@pytest.mark.parametrize("value", [math.nan, math.inf, -0.1, 1.0, 1.5])
def test_require_conversion_ratio_refuses_a_reactor_that_needs_no_makeup(
    value: float,
) -> None:
    """A conversion ratio of one or more is refused, not clamped to just below."""
    with pytest.raises(DeviceConfigurationError, match="conversion_ratio"):
        require_conversion_ratio("conversion_ratio", value)


@pytest.mark.parametrize("value", [0.0, 0.6, 0.85])
def test_require_conversion_ratio_admits_zero_through_almost_one(value: float) -> None:
    """Zero is a valid conversion ratio; the value passes through unchanged."""
    assert require_conversion_ratio("conversion_ratio", value) == value


@pytest.mark.parametrize("value", [math.nan, -math.inf, -1e-300])
def test_require_non_negative_refuses_negative_and_non_finite(value: float) -> None:
    """The guard names its field."""
    with pytest.raises(DeviceConfigurationError, match="alpha"):
        require_non_negative("alpha", value)


@pytest.mark.parametrize("value", [0.0, 0.3, 1e6])
def test_require_non_negative_admits_zero(value: float) -> None:
    """A reactor with no parasitic capture is a valid declaration."""
    assert require_non_negative("alpha", value) == value


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("engineering_q", {"engineering_q": 0.0}),
        ("engineering_q", {"engineering_q": math.nan}),
        ("neutron_fraction", {"neutron_fraction": 1.5}),
        ("energy_multiplication", {"energy_multiplication": 0.0}),
    ],
)
def test_thermal_power_ratio_names_the_field_it_refuses(
    field: str, kwargs: dict[str, float]
) -> None:
    """Each guard of equation 1 refuses by name."""
    good = {
        "engineering_q": 2.0,
        "neutron_fraction": DT_NEUTRON_FRACTION,
        "energy_multiplication": 8.5,
    }
    with pytest.raises(DeviceConfigurationError, match=field):
        thermal_power_ratio(**{**good, **kwargs})


def test_thermal_power_ratio_always_exceeds_one() -> None:
    """A hybrid's thermal power exceeds its fusion power, whatever the driver.

    The input power is counted in full and the blanket cannot subtract, so
    the ratio has no way to fall to one even for a blanket that multiplies
    nothing.
    """
    for engineering_q in (1e-3, 0.5, 1.0, 10.0, 1e6):
        assert thermal_power_ratio(engineering_q, 1.0, 1.0) > 1.0


def test_thermal_power_ratio_recovers_the_coefficient_printed_in_equation_17() -> None:
    """The report's printed 1.33 is the ratio less its driver term.

    Equation 17 prints the denominator ``1 + 1.33 Q'`` for the D-D
    molten-salt case. That coefficient is ``1 + f_n (M - 1)`` at the
    printed ``f_n = 0.66`` and ``M = 1.5``, and it is recovered here
    exactly rather than to a tolerance: measured, the two are the same
    IEEE double.
    """
    ratio = thermal_power_ratio(
        DD_PRINTED_SELF_SUFFICIENT_Q, DD_NEUTRON_FRACTION, DD_ENERGY_MULTIPLICATION
    )
    assert ratio - 1.0 / DD_PRINTED_SELF_SUFFICIENT_Q == (
        DD_PRINTED_THERMAL_COEFFICIENT
    )


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("thermal_efficiency", {"thermal_efficiency": 0.0}),
        ("thermal_efficiency", {"thermal_efficiency": 1.5}),
        ("engineering_q", {"engineering_q": -1.0}),
    ],
)
def test_hybrid_electrical_efficiency_names_the_field_it_refuses(
    field: str, kwargs: dict[str, float]
) -> None:
    """Equation 2 refuses through its own guard and through equation 1's."""
    good = {
        "thermal_efficiency": THERMAL_EFFICIENCY,
        "engineering_q": 2.0,
        "neutron_fraction": DT_NEUTRON_FRACTION,
        "energy_multiplication": 8.5,
    }
    with pytest.raises(DeviceConfigurationError, match=field):
        hybrid_electrical_efficiency(**{**good, **kwargs})


def test_hybrid_electrical_efficiency_crosses_zero_at_the_printed_q() -> None:
    """The molten-salt hybrid becomes electrically self-sufficient near Q' = 1.4.

    The report states that value on page 26. The efficiency is negative
    just below it and positive just above, and the crossing sits within a
    percent of the printed figure — closer than a value printed to two
    significant figures can distinguish.
    """
    inputs = {
        "neutron_fraction": DD_NEUTRON_FRACTION,
        "energy_multiplication": DD_ENERGY_MULTIPLICATION,
    }
    crossing = (1.0 / THERMAL_EFFICIENCY - 1.0) / DD_PRINTED_THERMAL_COEFFICIENT
    assert (
        hybrid_electrical_efficiency(THERMAL_EFFICIENCY, crossing * 0.99, **inputs)
        < 0.0
    )
    assert (
        hybrid_electrical_efficiency(THERMAL_EFFICIENCY, crossing * 1.01, **inputs)
        > 0.0
    )
    assert abs(crossing - DD_PRINTED_SELF_SUFFICIENT_Q) < 0.01 * (
        DD_PRINTED_SELF_SUFFICIENT_Q
    )


def test_hybrid_electrical_efficiency_is_negative_when_the_driver_dominates() -> None:
    """A driver that returns less than it takes is reported, not refused.

    The report's own molten-salt case sits near the zero crossing, so a
    figure of merit that could not express the unfavourable side of it
    would say less than the source does.
    """
    assert hybrid_electrical_efficiency(0.35, 0.05, 0.66, 1.5) < 0.0


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("breeding_rate", {"breeding_rate": 0.0}),
        ("conversion_ratio", {"conversion_ratio": 1.0}),
        ("capture_fission_ratio", {"capture_fission_ratio": -0.1}),
        ("fission_energy_mev", {"fission_energy_mev": 0.0}),
        ("fusion_energy_mev", {"fusion_energy_mev": math.inf}),
    ],
)
def test_offline_capacity_ratio_names_the_field_it_refuses(
    field: str, kwargs: dict[str, float]
) -> None:
    """Each guard of equation 6 refuses by name."""
    good = {
        "breeding_rate": DD_BREEDING_RATE,
        "conversion_ratio": U233_CONVERSION_RATIO,
        "capture_fission_ratio": U233_CAPTURE_FISSION_RATIO,
    }
    with pytest.raises(DeviceConfigurationError, match=field):
        offline_capacity_ratio(**{**good, **kwargs})


def test_offline_capacity_ratio_recovers_the_value_printed_in_equation_19() -> None:
    """The report prints R_o = 68 for the D-D molten-salt hybrid.

    It is recovered from the printed F, C, alpha and fusion energy to
    better than a quarter of a percent, which is all a value printed
    without a decimal place can assert.
    """
    ratio = offline_capacity_ratio(
        DD_BREEDING_RATE,
        U233_CONVERSION_RATIO,
        U233_CAPTURE_FISSION_RATIO,
        fusion_energy_mev=DD_FUSION_ENERGY_MEV,
    )
    assert round(ratio) == DD_PRINTED_OFFLINE_RATIO
    assert abs(ratio - DD_PRINTED_OFFLINE_RATIO) < 0.0025 * DD_PRINTED_OFFLINE_RATIO


def test_supported_fission_reactors_refuses_a_non_positive_offline_ratio() -> None:
    """Equation 4 guards its own argument as well as equation 1's."""
    with pytest.raises(DeviceConfigurationError, match="offline_ratio"):
        supported_fission_reactors(0.0, 2.0, DT_NEUTRON_FRACTION, 8.5)


def test_supported_fission_reactors_approaches_its_ceiling_from_below() -> None:
    """N rises with Q' towards the blanket's own ceiling and never reaches it."""
    _, breeding, multiplication, conversion, capture = TABLE_1_ROWS[0]
    offline = offline_capacity_ratio(breeding, conversion, capture)
    ceiling = offline / blanket_term(DT_NEUTRON_FRACTION, multiplication)
    previous = 0.0
    for engineering_q in (0.1, 0.5, 1.0, 5.0, 50.0, 5000.0):
        supported = supported_fission_reactors(
            offline, engineering_q, DT_NEUTRON_FRACTION, multiplication
        )
        assert previous < supported < ceiling
        previous = supported
    assert math.isclose(previous, ceiling, rel_tol=1e-3)


def test_the_thorium_blankets_support_three_to_five_times_the_uranium_ones() -> None:
    """The first point the report calls noteworthy on page 10, reproduced.

    Both comparisons are made at the same fissile buildup, fresh against
    fresh and exposed against exposed, because the report's third point
    is that buildup itself moves N.
    """
    ceilings = {}
    for name, breeding, multiplication, conversion, capture in TABLE_1_ROWS:
        offline = offline_capacity_ratio(breeding, conversion, capture)
        ceilings[name] = offline / blanket_term(DT_NEUTRON_FRACTION, multiplication)
    for state in ("fresh", "exposed"):
        ratio = ceilings[f"thorium_{state}"] / ceilings[f"uranium_{state}"]
        assert 3.0 <= ratio <= 5.0


def test_fissile_buildup_roughly_halves_the_supported_reactor_number() -> None:
    """The third point the report calls noteworthy on page 10, reproduced.

    Both exposed rows of Table 1 carry a fissile buildup near 3% of the
    heavy metal, and for both fuels the ceiling falls by a factor between
    two and two and a half.
    """
    ceilings = {}
    for name, breeding, multiplication, conversion, capture in TABLE_1_ROWS:
        offline = offline_capacity_ratio(breeding, conversion, capture)
        ceilings[name] = offline / blanket_term(DT_NEUTRON_FRACTION, multiplication)
    for fuel in ("uranium", "thorium"):
        assert 2.0 <= ceilings[f"{fuel}_fresh"] / ceilings[f"{fuel}_exposed"] <= 2.5


def test_a_larger_energy_multiplication_reaches_its_ceiling_at_a_lower_q() -> None:
    """The second point the report calls noteworthy on page 10, proved.

    The fraction of the ceiling reached is ``Q' B / (1 + Q' B)`` with
    ``B = 1 + f_n (M - 1)``, so it depends on the driver and the blanket
    only through their product. Any fixed fraction is therefore reached at
    ``Q'`` inversely proportional to ``B``, and the uranium blankets,
    whose energy multiplication is the larger, reach it first. This is an
    identity rather than a sampled observation, so it is asserted as one.
    """
    thresholds = {}
    for name, breeding, multiplication, conversion, capture in TABLE_1_ROWS:
        offline = offline_capacity_ratio(breeding, conversion, capture)
        term = blanket_term(DT_NEUTRON_FRACTION, multiplication)
        ceiling = offline / term
        threshold = 9.0 / term
        assert math.isclose(
            supported_fission_reactors(
                offline, threshold, DT_NEUTRON_FRACTION, multiplication
            )
            / ceiling,
            0.9,
            rel_tol=1e-12,
        )
        thresholds[name] = threshold
    assert thresholds["uranium_exposed"] < thresholds["uranium_fresh"]
    assert thresholds["uranium_fresh"] < thresholds["thorium_exposed"]
    assert thresholds["thorium_exposed"] < thresholds["thorium_fresh"]


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("offline_ratio", {"offline_ratio": -1.0}),
        ("thermal_efficiency", {"thermal_efficiency": 0.0}),
        ("engineering_q", {"engineering_q": 0.0}),
        ("neutron_fraction", {"neutron_fraction": 0.0}),
        ("energy_multiplication", {"energy_multiplication": math.nan}),
    ],
)
def test_online_capacity_ratio_names_the_field_it_refuses(
    field: str, kwargs: dict[str, float]
) -> None:
    """Each guard of equation 7 refuses by name."""
    good = {
        "offline_ratio": 33.0,
        "thermal_efficiency": THERMAL_EFFICIENCY,
        "engineering_q": 2.0,
        "neutron_fraction": DT_NEUTRON_FRACTION,
        "energy_multiplication": 8.5,
    }
    with pytest.raises(DeviceConfigurationError, match=field):
        online_capacity_ratio(**{**good, **kwargs})


def test_the_two_printed_forms_of_the_online_capacity_ratio_agree() -> None:
    """Equation 7 equals equation 5, which the report derives it from.

    The agreement is asserted within a relative tolerance rather than as
    an equality. Measured over a sweep of 6372 parameter points, 317 of
    them disagree in the last places because the two forms group the same
    factors differently and floating-point multiplication is not
    associative; the largest disagreement is 7.6e-16 relative.
    """
    offline = 33.0
    for engineering_q in (0.1, 0.5, 1.0, 1.4, 7.0, 100.0):
        for multiplication in (1.5, 2.13, 4.59, 8.5, 17.0):
            ratio = thermal_power_ratio(
                engineering_q, DT_NEUTRON_FRACTION, multiplication
            )
            efficiency = hybrid_electrical_efficiency(
                THERMAL_EFFICIENCY,
                engineering_q,
                DT_NEUTRON_FRACTION,
                multiplication,
            )
            assert math.isclose(
                efficiency / THERMAL_EFFICIENCY * ratio + offline,
                online_capacity_ratio(
                    offline,
                    THERMAL_EFFICIENCY,
                    engineering_q,
                    DT_NEUTRON_FRACTION,
                    multiplication,
                ),
                rel_tol=1e-14,
            )


def test_the_online_capacity_ratio_falls_below_the_offline_one() -> None:
    """An on-line hybrid spends part of what it generates on its own driver.

    At a thermal efficiency of one the recirculating term vanishes and the
    two coincide apart from the blanket's own contribution; below one it
    is strictly negative.
    """
    for efficiency in (0.25, THERMAL_EFFICIENCY, 0.99):
        recirculating = online_capacity_ratio(
            33.0, efficiency, 2.0, DT_NEUTRON_FRACTION, 8.5
        ) - online_capacity_ratio(33.0, 1.0, 2.0, DT_NEUTRON_FRACTION, 8.5)
        assert recirculating < 0.0
