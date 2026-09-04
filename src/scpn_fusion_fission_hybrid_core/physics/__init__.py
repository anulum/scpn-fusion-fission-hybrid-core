# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — level-0 device physics package

"""Level-0 device physics of the fusion-fission-hybrid family.

The published figures of merit of a hybrid — the thermal power it
produces for the fusion power it consumes, the electrical efficiency
left after driving the plasma, the number of fission reactors the bred
fuel supports, and the capacity ratios of on-line and off-line
operation — evaluated on a declared blanket, driver and fission-reactor
pairing and composed with the neutron source the configuration carries.
Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_fusion_fission_hybrid_core.physics.figures_of_merit import (
    DT_FUSION_ENERGY_MEV,
    DT_NEUTRON_FRACTION,
    FISSION_ENERGY_MEV,
    hybrid_electrical_efficiency,
    offline_capacity_ratio,
    online_capacity_ratio,
    require_conversion_ratio,
    require_fraction,
    require_non_negative,
    supported_fission_reactors,
    thermal_power_ratio,
)
from scpn_fusion_fission_hybrid_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    HybridInputs,
    Level0Physics,
    OperatingPoint,
    level0_physics,
)

__all__ = [
    "DT_FUSION_ENERGY_MEV",
    "DT_NEUTRON_FRACTION",
    "FISSION_ENERGY_MEV",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "HybridInputs",
    "Level0Physics",
    "OperatingPoint",
    "hybrid_electrical_efficiency",
    "level0_physics",
    "offline_capacity_ratio",
    "online_capacity_ratio",
    "require_conversion_ratio",
    "require_fraction",
    "require_non_negative",
    "supported_fission_reactors",
    "thermal_power_ratio",
]
