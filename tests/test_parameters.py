# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — parameter model tests

"""Every validation branch of the hybrid parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_fusion_fission_hybrid_core.errors import DeviceConfigurationError
from scpn_fusion_fission_hybrid_core.parameters import (
    NeutronSource,
    SubcriticalBlanket,
    require_finite,
    require_positive,
)


def synthetic_blanket(**overrides: Any) -> SubcriticalBlanket:
    """Build a valid synthetic blanket with optional overrides."""
    values: dict[str, Any] = {
        "k_effective": 0.9,
        "fertile_class": "thorium",
    }
    values.update(overrides)
    return SubcriticalBlanket(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_valid_blanket_and_multiplication() -> None:
    """A valid blanket constructs and derives its multiplication."""
    blanket = synthetic_blanket()
    assert blanket.multiplication() == pytest.approx(1.0 / (1.0 - 0.9))


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"k_effective": 0.0}, "k_effective"),
        ({"k_effective": 1.0}, "k_effective"),
        ({"k_effective": 1.2}, "k_effective"),
        ({"k_effective": -0.5}, "k_effective"),
        ({"k_effective": math.nan}, "k_effective"),
        ({"fertile_class": "plutonium"}, "fertile_class"),
    ],
)
def test_invalid_blanket_is_rejected(overrides: dict[str, Any], fragment: str) -> None:
    """Each blanket violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_blanket(**overrides)


def test_all_fertile_classes_construct() -> None:
    """Each documented fertile class constructs."""
    for fertile in ("depleted_uranium", "natural_uranium", "thorium"):
        assert synthetic_blanket(fertile_class=fertile).fertile_class == fertile


def test_valid_source_constructs() -> None:
    """A valid neutron source constructs unchanged."""
    assert NeutronSource(source_rate_per_s=1.0e18).source_rate_per_s == 1.0e18


def test_invalid_source_is_rejected() -> None:
    """Non-positive source rates are rejected."""
    with pytest.raises(DeviceConfigurationError, match="source_rate_per_s"):
        NeutronSource(source_rate_per_s=0.0)
    with pytest.raises(DeviceConfigurationError, match="source_rate_per_s"):
        NeutronSource(source_rate_per_s=math.inf)
