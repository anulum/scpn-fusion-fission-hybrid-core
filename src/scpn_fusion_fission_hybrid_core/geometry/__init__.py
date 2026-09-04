# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — device geometry package

"""Radial build and the two geometry tiers of the fusion-fission-hybrid family.

The plasma column that carries the neutron source, and the stack of
concentric material zones the filed calculational model tabulates around
it, as a tessellated model and as exact B-rep solids. Design record:
ADR 0006.
"""

from __future__ import annotations

from scpn_fusion_fission_hybrid_core.geometry.cad import (
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DeviceModelCAD,
    build_device_cad,
)
from scpn_fusion_fission_hybrid_core.geometry.device import (
    CM_PER_M,
    GEOMETRY_FIELDS,
    ZONE_THICKNESS_FIELDS,
    DeviceGeometry,
    geometry_from_record,
)
from scpn_fusion_fission_hybrid_core.geometry.model import (
    BODY_NAMES,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    ZONE_BODIES,
    DeviceModel3D,
    body_radii_m,
    build_device_model,
)

__all__ = [
    "BODY_NAMES",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CAD_MODEL_UNITS",
    "CM_PER_M",
    "DEFAULT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_LINEAR_DEFLECTION_M",
    "DEFAULT_REFERENCE_MESH_SEGMENTS",
    "GEOMETRY_FIELDS",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS",
    "ZONE_BODIES",
    "ZONE_THICKNESS_FIELDS",
    "DeviceGeometry",
    "DeviceModel3D",
    "DeviceModelCAD",
    "body_radii_m",
    "build_device_cad",
    "build_device_model",
    "geometry_from_record",
]
