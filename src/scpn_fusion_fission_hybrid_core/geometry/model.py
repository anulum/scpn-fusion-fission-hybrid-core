# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — tier-G1 device model

"""Tier-G1 tessellated model of a hybrid's radial build.

Eight bodies in a fixed order: the plasma column that carries the neutron
source, then every material zone of the blanket stack outward from the
first wall to the structure that closes it. Each is a cylinder or an
annular tube about ``z``, so this tier needs no primitive the shared
library does not already have.

**The vacuum is a gap and not a body.** The filed calculational model
counts it as a zone because a transport calculation must, but empty space
is not a solid, and drawing it as one would put a body where a reader
expects a void.

The body set follows what the filed source tabulates rather than the
three-body sketch the plan carried: a first wall, a coolant channel and
three separate structural shells are not decoration, they are where a
third of the neutron absorption happens in the source's own balance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import pairwise
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    cylinder_solid,
    require_segments,
)

from scpn_fusion_fission_hybrid_core.configuration import DeviceConfiguration
from scpn_fusion_fission_hybrid_core.errors import DeviceGeometryError
from scpn_fusion_fission_hybrid_core.geometry.device import CM_PER_M, DeviceGeometry

MODEL_SCHEMA: Final = "scpn.fusion-fission-hybrid-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the axis of the plasma column and of the blanket stack",
    "origin": "z = 0 at the midplane of the build",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a synthetic configuration and geometry",
    (
        "the filed calculational model is one-dimensional and prints radii "
        "only; the axial length is declared here and is not sourced, and the "
        "end caps of the cylinders are an artefact of the primitive"
    ),
    (
        "the vacuum zone of that model is a gap and carries no body, because "
        "empty space is not a solid"
    ),
    (
        "the zones are drawn at their declared thicknesses; no coolant "
        "channel, manifold, penetration, support or fuel-handling route is "
        "modelled, and a body named for a material carries no material"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field, criticality or neutronic quantity is carried",
    "nothing here is a nuclear-safety, criticality-safety or licensing statement",
    "no value describes or validates any real machine",
)

ROLE_PLASMA: Final = "plasma"
ROLE_STRUCTURE: Final = "structure"
ROLE_COOLANT: Final = "coolant"
ROLE_BLANKET: Final = "blanket"
ROLE_REFLECTOR: Final = "reflector"
MATERIAL_PLASMA: Final = "plasma"
MATERIAL_STRUCTURAL_STEEL: Final = "structural_steel"
MATERIAL_COOLANT_WATER: Final = "coolant_water"
MATERIAL_MOLTEN_SALT: Final = "molten_salt"
MATERIAL_GRAPHITE: Final = "graphite"

BODY_PLASMA_COLUMN: Final = "plasma_column"
BODY_FIRST_WALL: Final = "first_wall"
BODY_COOLANT_CHANNEL: Final = "coolant_channel"
BODY_INNER_STRUCTURE: Final = "inner_structure"
BODY_MOLTEN_SALT_BLANKET: Final = "molten_salt_blanket"
BODY_OUTER_STRUCTURE: Final = "outer_structure"
BODY_REFLECTOR: Final = "reflector"
BODY_BACKING_STRUCTURE: Final = "backing_structure"
BODY_NAMES: Final = (
    BODY_PLASMA_COLUMN,
    BODY_FIRST_WALL,
    BODY_COOLANT_CHANNEL,
    BODY_INNER_STRUCTURE,
    BODY_MOLTEN_SALT_BLANKET,
    BODY_OUTER_STRUCTURE,
    BODY_REFLECTOR,
    BODY_BACKING_STRUCTURE,
)

#: Role and material of each annular zone, in the order they are stacked
#: outward from the first wall. The plasma column is not here: it is a
#: solid cylinder and the only body that is not an annulus.
ZONE_BODIES: Final = (
    (BODY_FIRST_WALL, ROLE_STRUCTURE, MATERIAL_STRUCTURAL_STEEL),
    (BODY_COOLANT_CHANNEL, ROLE_COOLANT, MATERIAL_COOLANT_WATER),
    (BODY_INNER_STRUCTURE, ROLE_STRUCTURE, MATERIAL_STRUCTURAL_STEEL),
    (BODY_MOLTEN_SALT_BLANKET, ROLE_BLANKET, MATERIAL_MOLTEN_SALT),
    (BODY_OUTER_STRUCTURE, ROLE_STRUCTURE, MATERIAL_STRUCTURAL_STEEL),
    (BODY_REFLECTOR, ROLE_REFLECTOR, MATERIAL_GRAPHITE),
    (BODY_BACKING_STRUCTURE, ROLE_STRUCTURE, MATERIAL_STRUCTURAL_STEEL),
)


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    geometry_digest_sha256
        Digest of the geometry the model was built from.
    segments
        Circumferential segment count every body was tessellated at.
    meshes
        The eight bodies in the fixed order of :data:`BODY_NAMES`.

    Raises
    ------
    DeviceGeometryError
        If the body names or their order differ from :data:`BODY_NAMES`.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body set and its order.

        Raises
        ------
        DeviceGeometryError
            If the body names or their order differ from
            :data:`BODY_NAMES`.
        """
        names = tuple(mesh.name for mesh in self.meshes)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"meshes: bodies must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "segments": self.segments,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def body_radii_m(geometry: DeviceGeometry) -> tuple[tuple[float, float], ...]:
    """Return the inner and outer radius of each annular zone, in metres.

    The first pair starts at the outer edge of the vacuum gap, because the
    gap carries no body; each following pair starts where the previous
    one ended.

    Parameters
    ----------
    geometry
        Validated device geometry.

    Returns
    -------
    tuple
        One ``(inner, outer)`` pair per entry of :data:`ZONE_BODIES`.
    """
    radii = [radius * CM_PER_M for radius in geometry.zone_outer_radii_cm]
    return tuple(pairwise(radii))


def build_device_model(
    configuration: DeviceConfiguration, geometry: DeviceGeometry, segments: int
) -> DeviceModel3D:
    """Tessellate the eight bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated hybrid configuration. It carries no dimension, so it
        contributes only its digest and the identity of the design.
    geometry
        Validated radial build.
    segments
        Circumferential segments for every body; at least 8, multiple
        of 8.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid; the library's refusal is
        re-raised under the device error type with its message.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    half = geometry.length_cm * CM_PER_M / 2.0
    meshes = [
        TriangleMesh(
            name=BODY_PLASMA_COLUMN,
            role=ROLE_PLASMA,
            material_identifier=MATERIAL_PLASMA,
            vertices=(
                built := cylinder_solid(
                    geometry.plasma_radius_cm * CM_PER_M, -half, half, segments
                )
            )[0],
            faces=built[1],
        )
    ]
    for (name, role, material), (inner, outer) in zip(
        ZONE_BODIES, body_radii_m(geometry), strict=True
    ):
        vertices, faces = annular_tube(inner, outer, -half, half, segments)
        meshes.append(
            TriangleMesh(
                name=name,
                role=role,
                material_identifier=material,
                vertices=vertices,
                faces=faces,
            )
        )
    return DeviceModel3D(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        segments=segments,
        meshes=tuple(meshes),
    )
