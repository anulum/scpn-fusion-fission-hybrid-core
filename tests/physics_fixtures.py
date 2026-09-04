# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — level-0 physics fixtures

"""Fixtures shared by the level-0 physics tests.

Two kinds live here and they are not interchangeable. The reference
fixture is synthetic: round numbers chosen so a reader can follow the
arithmetic, describing nothing. The anchor fixtures are built from
values ORNL/PPA-79/3 prints, so that the tests can show each printed
value is recoverable from the built record rather than merely stored
next to it.

Every value in the anchor fixtures was read off the rendered page image
of the filed scan. Its OCR text layer mangles digits — it renders the
17.0 of Table 1 as ``]7.0`` and the 5 of Table C4 as ``J`` — and was
not trusted for any number here.
"""

from __future__ import annotations

from typing import Final

from scpn_fusion_fission_hybrid_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
)
from scpn_fusion_fission_hybrid_core.parameters import NeutronSource, SubcriticalBlanket
from scpn_fusion_fission_hybrid_core.physics import HybridInputs

REGISTRY: Final = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

PU239_CONVERSION_RATIO: Final = 0.6
PU239_CAPTURE_FISSION_RATIO: Final = 0.3
U233_CONVERSION_RATIO: Final = 0.85
U233_CAPTURE_FISSION_RATIO: Final = 0.1
"""Table 2, page 10: light-water reactors burning plutonium and
high-temperature gas-cooled reactors burning uranium-233."""

THERMAL_EFFICIENCY: Final = 0.35
"""The thermal-to-electric efficiency the report uses (pages 26, 34)."""

DD_FUSION_ENERGY_MEV: Final = 12.45
DD_NEUTRON_FRACTION: Final = 0.66
DD_BREEDING_RATE: Final = 0.7
DD_ENERGY_MULTIPLICATION: Final = 1.5
"""Section 6, page 26: the semicatalyzed D-D driver with a molten-salt
thorium blanket, for which the report prints the derived quantities the
anchor tests recover."""

DD_PRINTED_THERMAL_COEFFICIENT: Final = 1.33
"""The coefficient of Q' printed in the denominator of equation 17."""

DD_PRINTED_OFFLINE_RATIO: Final = 68
"""R_o printed in equation 19."""

DD_PRINTED_SELF_SUFFICIENT_Q: Final = 1.4
"""The engineering Q the report states is required for electrical
self-sufficiency of the molten-salt hybrid (page 26)."""

TABLE_1_ROWS: Final = (
    ("uranium_fresh", 1.53, 8.5, PU239_CONVERSION_RATIO, PU239_CAPTURE_FISSION_RATIO),
    (
        "uranium_exposed",
        1.45,
        17.0,
        PU239_CONVERSION_RATIO,
        PU239_CAPTURE_FISSION_RATIO,
    ),
    ("thorium_fresh", 0.62, 2.13, U233_CONVERSION_RATIO, U233_CAPTURE_FISSION_RATIO),
    ("thorium_exposed", 0.52, 4.59, U233_CONVERSION_RATIO, U233_CAPTURE_FISSION_RATIO),
)
"""Table 1, page 9, paired with the reactor of Table 2 that burns what
each blanket breeds: name, breeding rate F, energy multiplication M,
conversion ratio C, capture-to-fission ratio alpha. The two exposed rows
carry the fissile buildup the report reaches at 5 and 12 MW yr per square
metre, about 3% of the heavy metal in both cases."""


def synthetic_configuration(
    k_effective: float = 0.9, source_rate_per_s: float = 1.0e19
) -> DeviceConfiguration:
    """Build a valid synthetic configuration.

    Parameters
    ----------
    k_effective
        Effective neutron multiplication factor of the blanket.
    source_rate_per_s
        Declared fusion neutron source rate.

    Returns
    -------
    DeviceConfiguration
        A configuration describing no real machine.
    """
    return DeviceConfiguration(
        identifier="fusion_fission_hybrid",
        blanket=SubcriticalBlanket(
            k_effective=k_effective, fertile_class="depleted_uranium"
        ),
        source=NeutronSource(source_rate_per_s=source_rate_per_s),
        registry=REGISTRY,
    )


def reference_inputs() -> HybridInputs:
    """Build the synthetic reference input set.

    Returns
    -------
    HybridInputs
        Round declared values; no printed number is claimed for them.
    """
    return HybridInputs(
        breeding_rate=1.0,
        energy_multiplication=2.0,
        engineering_q=2.0,
        conversion_ratio=0.5,
        capture_fission_ratio=0.25,
        thermal_efficiency=0.4,
    )


def dd_molten_salt_inputs(
    engineering_q: float = DD_PRINTED_SELF_SUFFICIENT_Q,
) -> HybridInputs:
    """Build the anchor input set of the report's D-D molten-salt hybrid.

    Parameters
    ----------
    engineering_q
        Engineering Q to evaluate at; the default is the value the report
        states is required for electrical self-sufficiency.

    Returns
    -------
    HybridInputs
        The declared inputs the report prints for this case.
    """
    return HybridInputs(
        breeding_rate=DD_BREEDING_RATE,
        energy_multiplication=DD_ENERGY_MULTIPLICATION,
        engineering_q=engineering_q,
        conversion_ratio=U233_CONVERSION_RATIO,
        capture_fission_ratio=U233_CAPTURE_FISSION_RATIO,
        thermal_efficiency=THERMAL_EFFICIENCY,
        neutron_fraction=DD_NEUTRON_FRACTION,
        fusion_energy_mev=DD_FUSION_ENERGY_MEV,
    )


def table_1_inputs(name: str, engineering_q: float) -> HybridInputs:
    """Build the anchor input set of one Table 1 row.

    Parameters
    ----------
    name
        Row name from :data:`TABLE_1_ROWS`.
    engineering_q
        Engineering Q to evaluate at.

    Returns
    -------
    HybridInputs
        The row's declared blanket paired with its fission reactor, at the
        D-T constants the report takes on page 10.

    Raises
    ------
    KeyError
        If no row carries that name.
    """
    for row, breeding, multiplication, conversion, capture in TABLE_1_ROWS:
        if row == name:
            return HybridInputs(
                breeding_rate=breeding,
                energy_multiplication=multiplication,
                engineering_q=engineering_q,
                conversion_ratio=conversion,
                capture_fission_ratio=capture,
                thermal_efficiency=THERMAL_EFFICIENCY,
            )
    raise KeyError(name)
