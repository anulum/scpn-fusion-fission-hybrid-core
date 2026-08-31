# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — hybrid parameter model

"""Validated parameter objects of a fusion-fission-hybrid configuration.

The derived quantity implements one standard result and nothing more:
the source-driven subcritical multiplication ``M = 1 / (1 - k_eff)``
(cf. H. A. Bethe, Phys. Today 32 (1979) 44). It is a rough consistency
instrument with documented applicability bounds; no claim about any
real machine follows from it, and nothing here is a nuclear-safety,
criticality-safety, or licensing statement.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_fusion_fission_hybrid_core.errors import DeviceConfigurationError

FERTILE_CLASSES: Final = ("depleted_uranium", "natural_uranium", "thorium")


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

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
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

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
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class SubcriticalBlanket:
    """Subcritical fission-blanket parameters of a hybrid configuration.

    Parameters
    ----------
    k_effective
        Effective neutron multiplication factor; strictly inside
        ``(0, 1)`` — a driven hybrid blanket never reaches criticality.
    fertile_class
        Fertile-fuel class: ``depleted_uranium``, ``natural_uranium``,
        or ``thorium``.

    Raises
    ------
    DeviceConfigurationError
        If the multiplication factor leaves the strictly subcritical
        interval or the fertile class is unknown.
    """

    k_effective: float
    fertile_class: str

    def __post_init__(self) -> None:
        """Validate the blanket invariants.

        Raises
        ------
        DeviceConfigurationError
            If the multiplication factor leaves the strictly
            subcritical interval or the fertile class is unknown.
        """
        require_finite("k_effective", self.k_effective)
        if not 0.0 < self.k_effective < 1.0:
            raise DeviceConfigurationError(
                "k_effective: must be strictly inside (0, 1) — a driven "
                f"hybrid blanket never reaches criticality, "
                f"got {self.k_effective!r}"
            )
        if self.fertile_class not in FERTILE_CLASSES:
            raise DeviceConfigurationError(
                f"fertile_class: must be one of {FERTILE_CLASSES!r}, "
                f"got {self.fertile_class!r}"
            )

    def multiplication(self) -> float:
        """Source-driven subcritical multiplication of the blanket.

        Returns
        -------
        float
            ``M = 1 / (1 - k_eff)`` — a bookkeeping instrument, not a
            performance or safety claim.
        """
        return 1.0 / (1.0 - self.k_effective)


@dataclass(frozen=True, slots=True)
class NeutronSource:
    """Fusion neutron-source declaration of a hybrid configuration.

    Parameters
    ----------
    source_rate_per_s
        Declared fusion neutron source rate in neutrons per second;
        strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the rate is non-finite or not strictly positive.
    """

    source_rate_per_s: float

    def __post_init__(self) -> None:
        """Validate the neutron-source invariants.

        Raises
        ------
        DeviceConfigurationError
            If the rate is non-finite or not strictly positive.
        """
        require_positive("source_rate_per_s", self.source_rate_per_s)
