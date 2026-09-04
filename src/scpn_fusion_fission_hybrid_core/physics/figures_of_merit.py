# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — hybrid figures of merit

"""Closed-form figures of merit of a fusion-fission hybrid.

The forms are those of M. J. Saltmarsh, W. R. Grimes and R. T. Santoro,
*An Optimization of the Fission-Fusion Hybrid Concept*, ORNL/PPA-79/3
(1979): the total thermal power of the hybrid relative to its fusion
power (equation 1), the hybrid's overall electrical efficiency
(equation 2), the number of fission reactors one hybrid supports
(equation 4), and the two capacity ratios of on-line and off-line
operation (equations 5 to 7).

Each is a ratio of energies and efficiencies. Nothing here solves a
transport equation, and no neutronics is performed: the blanket enters
through two declared numbers the report tabulates, its fissile breeding
rate ``F`` in atoms per source neutron and its energy multiplication
``M``, and the fission reactors through two more, the conversion ratio
``C`` and the capture-to-fission ratio ``alpha``.

The ``M`` of this module is the blanket's **energy** multiplication —
energy deposited in the blanket per source neutron, divided by the
average energy of a source neutron. It is a different quantity from the
neutron multiplication ``1 / (1 - k_eff)`` that
:meth:`~scpn_fusion_fission_hybrid_core.parameters.SubcriticalBlanket.multiplication`
returns, and neither is computed from the other here. Conflating them
would be a claim no filed source supports.
"""

from __future__ import annotations

from typing import Final

from scpn_fusion_fission_hybrid_core.errors import DeviceConfigurationError
from scpn_fusion_fission_hybrid_core.parameters import require_finite, require_positive

FISSION_ENERGY_MEV: Final = 200.0
"""Energy released per fission the report takes throughout (page 10)."""

DT_FUSION_ENERGY_MEV: Final = 17.6
"""Energy released per D-T fusion reaction the report takes (page 10)."""

DT_NEUTRON_FRACTION: Final = 0.8
"""Fraction of D-T fusion power carried by neutrons (page 10)."""


def require_fraction(name: str, value: float) -> float:
    """Return ``value`` when it lies in ``(0, 1]``.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite, not positive, or exceeds one.
    """
    require_finite(name, value)
    if not 0.0 < value <= 1.0:
        raise DeviceConfigurationError(f"{name}: must lie in (0, 1], got {value!r}")
    return value


def require_conversion_ratio(name: str, value: float) -> float:
    """Return ``value`` when it lies in ``[0, 1)``.

    A conversion ratio of one is a break-even breeder, for which the net
    fissile consumption in the denominator of equation 6 vanishes and the
    ratio is undefined; above one the reactor breeds and consumes no net
    fissile material at all. Both are refused rather than clamped,
    because the figure of merit does not describe either.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite, negative, or one or greater.
    """
    require_finite(name, value)
    if not 0.0 <= value < 1.0:
        raise DeviceConfigurationError(
            f"{name}: must lie in [0, 1) — a reactor that consumes no net "
            f"fissile material supports no hybrid, got {value!r}"
        )
    return value


def require_non_negative(name: str, value: float) -> float:
    """Return ``value`` when finite and not negative.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or negative.
    """
    require_finite(name, value)
    if value < 0.0:
        raise DeviceConfigurationError(f"{name}: must not be negative, got {value!r}")
    return value


def thermal_power_ratio(
    engineering_q: float,
    neutron_fraction: float,
    energy_multiplication: float,
) -> float:
    """Total hybrid thermal power divided by its fusion power.

    Equation 1 of the report, ``P_T / P_F = 1/Q' + 1 + f_n (M - 1)``.
    The three terms are the input power the driver needs, the fusion
    power itself, and the extra power the blanket releases beyond the
    neutron energy that entered it. The input power is counted in full
    even when it couples to the plasma poorly, because it must still be
    absorbed and dissipated somewhere in the plant.

    Parameters
    ----------
    engineering_q
        Engineering Q of the fusion driver, ``Q' = P_F / P_in``;
        strictly positive.
    neutron_fraction
        Fraction of the fusion power carried by neutrons, in ``(0, 1]``.
    energy_multiplication
        Blanket energy multiplication ``M``; strictly positive.

    Returns
    -------
    float
        The ratio, always greater than one.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("engineering_q", engineering_q)
    require_fraction("neutron_fraction", neutron_fraction)
    require_positive("energy_multiplication", energy_multiplication)
    return 1.0 / engineering_q + 1.0 + neutron_fraction * (energy_multiplication - 1.0)


def hybrid_electrical_efficiency(
    thermal_efficiency: float,
    engineering_q: float,
    neutron_fraction: float,
    energy_multiplication: float,
) -> float:
    """Overall electrical efficiency of the hybrid.

    Equation 2 of the report: the thermal-to-electric efficiency less the
    share of the hybrid's own thermal power that recirculates to drive
    the plasma, ``eta_H - (1/Q') / (P_T / P_F)``.

    The result is negative when the driver consumes more than the plant
    generates. That is reported, not refused: the report's own molten-salt
    case sits near the zero crossing, and a figure of merit that could not
    express the unfavourable side of it would say less than the source
    does.

    Parameters
    ----------
    thermal_efficiency
        Thermal-to-electric conversion efficiency ``eta_H``, in
        ``(0, 1]``.
    engineering_q
        Engineering Q of the fusion driver; strictly positive.
    neutron_fraction
        Fraction of the fusion power carried by neutrons, in ``(0, 1]``.
    energy_multiplication
        Blanket energy multiplication ``M``; strictly positive.

    Returns
    -------
    float
        The efficiency, which may be negative.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_fraction("thermal_efficiency", thermal_efficiency)
    ratio = thermal_power_ratio(engineering_q, neutron_fraction, energy_multiplication)
    return thermal_efficiency - (1.0 / engineering_q) / ratio


def offline_capacity_ratio(
    breeding_rate: float,
    conversion_ratio: float,
    capture_fission_ratio: float,
    fission_energy_mev: float = FISSION_ENERGY_MEV,
    fusion_energy_mev: float = DT_FUSION_ENERGY_MEV,
) -> float:
    """Fission power the bred fuel supports, divided by the fusion power.

    Equation 6 of the report,
    ``R_o = (E_fiss / E_fus) F / [(1 - C)(1 + alpha)]``. Each fissile
    atom the blanket breeds is burned in a fission reactor whose
    conversion ratio ``C`` replaces part of it and whose capture-to-
    fission ratio ``alpha`` wastes another part, so ``(1 - C)(1 + alpha)``
    fissile atoms must be supplied for each one that fissions.

    This is also the capacity ratio of a hybrid operated off-line, which
    generates no electricity of its own.

    Parameters
    ----------
    breeding_rate
        Fissile breeding rate ``F`` in atoms per source neutron;
        strictly positive.
    conversion_ratio
        Conversion ratio ``C`` of the fission reactors, in ``[0, 1)``.
    capture_fission_ratio
        Capture-to-fission ratio ``alpha``; not negative.
    fission_energy_mev
        Energy released per fission; strictly positive.
    fusion_energy_mev
        Energy released per fusion reaction; strictly positive.

    Returns
    -------
    float
        The ratio, strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("breeding_rate", breeding_rate)
    require_conversion_ratio("conversion_ratio", conversion_ratio)
    require_non_negative("capture_fission_ratio", capture_fission_ratio)
    require_positive("fission_energy_mev", fission_energy_mev)
    require_positive("fusion_energy_mev", fusion_energy_mev)
    net = (1.0 - conversion_ratio) * (1.0 + capture_fission_ratio)
    return fission_energy_mev / fusion_energy_mev * breeding_rate / net


def supported_fission_reactors(
    offline_ratio: float,
    engineering_q: float,
    neutron_fraction: float,
    energy_multiplication: float,
) -> float:
    """Count the fission reactors one hybrid of equal thermal power supports.

    Equation 4 of the report, which is equation 6 divided by equation 1.
    The number rises with ``Q'`` towards a ceiling set by the blanket
    alone. A large energy multiplication reaches that ceiling at a lower
    ``Q'``, because the blanket's own contribution to the thermal power
    then dwarfs the recirculating term that ``Q'`` governs; it also puts
    the ceiling lower, because the same fission power is divided by a
    larger thermal power.

    Parameters
    ----------
    offline_ratio
        The off-line capacity ratio ``R_o``; strictly positive.
    engineering_q
        Engineering Q of the fusion driver; strictly positive.
    neutron_fraction
        Fraction of the fusion power carried by neutrons, in ``(0, 1]``.
    energy_multiplication
        Blanket energy multiplication ``M``; strictly positive.

    Returns
    -------
    float
        The number of reactors supported, not rounded to an integer.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("offline_ratio", offline_ratio)
    return offline_ratio / thermal_power_ratio(
        engineering_q, neutron_fraction, energy_multiplication
    )


def online_capacity_ratio(
    offline_ratio: float,
    thermal_efficiency: float,
    engineering_q: float,
    neutron_fraction: float,
    energy_multiplication: float,
) -> float:
    """Capacity ratio of a hybrid operated on-line.

    Equation 7 of the report,
    ``R = (1/Q')(1 - 1/eta_H) + 1 + f_n (M - 1) + R_o``, which the report
    derives from equations 1 and 2 and which equals the form of
    equation 5, ``(eta_HB / eta_H)(P_T / P_F) + R_o``.

    The first term is negative for any thermal efficiency below one: an
    on-line hybrid spends part of what it generates on its own driver,
    so its capacity ratio falls below the off-line value by exactly that
    recirculating share.

    Parameters
    ----------
    offline_ratio
        The off-line capacity ratio ``R_o``; strictly positive.
    thermal_efficiency
        Thermal-to-electric conversion efficiency ``eta_H``, in
        ``(0, 1]``.
    engineering_q
        Engineering Q of the fusion driver; strictly positive.
    neutron_fraction
        Fraction of the fusion power carried by neutrons, in ``(0, 1]``.
    energy_multiplication
        Blanket energy multiplication ``M``; strictly positive.

    Returns
    -------
    float
        The ratio.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("offline_ratio", offline_ratio)
    require_fraction("thermal_efficiency", thermal_efficiency)
    require_positive("engineering_q", engineering_q)
    require_fraction("neutron_fraction", neutron_fraction)
    require_positive("energy_multiplication", energy_multiplication)
    recirculating = (1.0 / engineering_q) * (1.0 - 1.0 / thermal_efficiency)
    blanket = 1.0 + neutron_fraction * (energy_multiplication - 1.0)
    return recirculating + blanket + offline_ratio
