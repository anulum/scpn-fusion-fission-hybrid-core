# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — device model fixtures

"""Fixtures shared by the tier-G1 and tier-G2 tests.

The anchor geometry is the radial build ORNL/PPA-79/3 tabulates in its
Table C1, entered as the **thicknesses** that table prints so the outer
radii it also prints can be recovered rather than restated.

Every value was read off the rendered page image of the filed scan, never
its OCR text layer, which mangles digits.

The axial length is not an anchor. The filed calculational model is
one-dimensional and prints no length; the value here is declared.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_fusion_fission_hybrid_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
)
from scpn_fusion_fission_hybrid_core.geometry import DeviceGeometry
from scpn_fusion_fission_hybrid_core.parameters import NeutronSource, SubcriticalBlanket

REGISTRY: Final = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

TABLE_C1_THICKNESSES_CM: Final = {
    "plasma_radius_cm": 100.0,
    "vacuum_gap_cm": 50.0,
    "first_wall_thickness_cm": 1.0,
    "coolant_thickness_cm": 0.5,
    "inner_structure_thickness_cm": 1.0,
    "salt_thickness_cm": 42.0,
    "outer_structure_thickness_cm": 1.0,
    "reflector_thickness_cm": 40.0,
    "backing_structure_thickness_cm": 1.0,
}
"""Zone thicknesses of Table C1, page 47 of the filed report, in the order
the table stacks them."""

TABLE_C1_OUTER_RADII_CM: Final = (
    150.0,
    151.0,
    151.5,
    152.5,
    194.5,
    195.5,
    235.5,
    236.5,
)
"""Outer radii the same table prints beside those thicknesses, from the
vacuum zone outward. They are what the built geometry must recover."""

DECLARED_LENGTH_CM: Final = 400.0
"""Axial length. **Declared, not printed** — the filed model is
one-dimensional. It is chosen at four metres so the build is longer than
it is wide, which no source states and nothing depends on."""

REFERENCE_THICKNESSES_CM: Final = {
    "plasma_radius_cm": 60.0,
    "vacuum_gap_cm": 20.0,
    "first_wall_thickness_cm": 2.0,
    "coolant_thickness_cm": 1.0,
    "inner_structure_thickness_cm": 2.0,
    "salt_thickness_cm": 30.0,
    "outer_structure_thickness_cm": 2.0,
    "reflector_thickness_cm": 25.0,
    "backing_structure_thickness_cm": 2.0,
}
"""A synthetic build, deliberately unlike the anchor so that a test which
passes on one and not the other is visible. It anchors nothing."""


def synthetic_configuration(
    k_effective: float = 0.9,
    fertile_class: str = "thorium",
    source_rate_per_s: float = 1.0e19,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration.

    Parameters
    ----------
    k_effective
        Effective neutron multiplication factor of the blanket.
    fertile_class
        Fertile-fuel class of the blanket.
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
            k_effective=k_effective, fertile_class=fertile_class
        ),
        source=NeutronSource(source_rate_per_s=source_rate_per_s),
        registry=REGISTRY,
    )


def anchor_geometry(**overrides: float) -> DeviceGeometry:
    """Build the Table C1 radial build with optional overrides.

    Parameters
    ----------
    **overrides
        Field values replacing those of the table.

    Returns
    -------
    DeviceGeometry
        The validated geometry.
    """
    return DeviceGeometry(
        **{**TABLE_C1_THICKNESSES_CM, "length_cm": DECLARED_LENGTH_CM, **overrides}
    )


def reference_geometry(**overrides: float) -> DeviceGeometry:
    """Build the synthetic reference geometry with optional overrides.

    Parameters
    ----------
    **overrides
        Field values replacing those of the reference build.

    Returns
    -------
    DeviceGeometry
        The validated geometry.
    """
    return DeviceGeometry(
        **{**REFERENCE_THICKNESSES_CM, "length_cm": 200.0, **overrides}
    )


def inscribed_polygon_ratio(segments: int) -> float:
    """Return the area of the inscribed regular polygon over the circle's.

    ``(n / 2 pi) sin(2 pi / n)``. Every body of these tiers is tessellated
    by inscribing a regular polygon in each circular section, so a mesh
    volume is smaller than the analytic volume by exactly this factor.

    Parameters
    ----------
    segments
        Circumferential segment count.

    Returns
    -------
    float
        The ratio, which approaches one from below as the count rises.
    """
    return segments * math.sin(2.0 * math.pi / segments) / (2.0 * math.pi)
