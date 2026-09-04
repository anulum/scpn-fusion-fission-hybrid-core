# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — device geometry model

"""Validated radial build of a hybrid's plasma, blanket and reflector.

The configuration carries no dimension at all — it declares a blanket's
multiplication factor and fertile class and a neutron source rate — so
every length of the device lives here.

The build follows the shape the filed calculational model uses: a plasma
column on the axis, a vacuum gap, and then a stack of concentric zones,
each named for what it is made of. The zones are declared as
**thicknesses** and their outer radii are derived, which is the direction
that keeps a build consistent: a thickness is positive or it is refused,
whereas a stack of independently declared radii can be given in the wrong
order and still look valid.

**The filed model is radial only.** It is a one-dimensional transport
calculation, so it prints no length, and the axial length here is
declared rather than sourced. The model records say so; a reader who
takes the printed radii as anchors should not take the length for one.

Validation is fail-closed, serialisation is canonical, and the SHA-256
digest identifies the exact geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_fusion_fission_hybrid_core.errors import DeviceGeometryError
from scpn_fusion_fission_hybrid_core.parameters import require_positive

ZONE_THICKNESS_FIELDS: Final = (
    "vacuum_gap_cm",
    "first_wall_thickness_cm",
    "coolant_thickness_cm",
    "inner_structure_thickness_cm",
    "salt_thickness_cm",
    "outer_structure_thickness_cm",
    "reflector_thickness_cm",
    "backing_structure_thickness_cm",
)
GEOMETRY_FIELDS: Final = (
    "plasma_radius_cm",
    *ZONE_THICKNESS_FIELDS,
    "length_cm",
)

#: Metres per centimetre; the filed calculational model tabulates its
#: radial build in centimetres, so this family declares its lengths there.
CM_PER_M: Final = 1.0e-2


def _positive(name: str, value: float) -> float:
    """Apply the shared positivity rule under the geometry error type.

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
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DeviceGeometry:
    """Validated hybrid radial build (centimetres in the names).

    Parameters
    ----------
    plasma_radius_cm
        Radius of the plasma column that carries the neutron source.
    vacuum_gap_cm
        Radial gap between the plasma edge and the first wall. It is a
        gap and not a body: the filed model's vacuum zone is empty space.
    first_wall_thickness_cm
        Thickness of the structural wall facing the plasma.
    coolant_thickness_cm
        Thickness of the coolant channel behind it.
    inner_structure_thickness_cm
        Thickness of the structure between the coolant and the blanket.
    salt_thickness_cm
        Thickness of the molten-salt blanket zone, which is where the
        breeding and most of the heating happen.
    outer_structure_thickness_cm
        Thickness of the structure behind the blanket.
    reflector_thickness_cm
        Thickness of the reflector behind that.
    backing_structure_thickness_cm
        Thickness of the structure closing the stack.
    length_cm
        Axial length of every body. **Declared, not sourced**: the filed
        calculational model is one-dimensional and prints no length.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    plasma_radius_cm: float
    vacuum_gap_cm: float
    first_wall_thickness_cm: float
    coolant_thickness_cm: float
    inner_structure_thickness_cm: float
    salt_thickness_cm: float
    outer_structure_thickness_cm: float
    reflector_thickness_cm: float
    backing_structure_thickness_cm: float
    length_cm: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in GEOMETRY_FIELDS:
            _positive(name, getattr(self, name))

    @property
    def zone_outer_radii_cm(self) -> tuple[float, ...]:
        """Outer radius of each zone, in the order they are stacked.

        Returns
        -------
        tuple of float
            One radius per entry of :data:`ZONE_THICKNESS_FIELDS`, each
            the previous radius plus that zone's thickness, starting from
            the plasma radius.
        """
        radii: list[float] = []
        radius = self.plasma_radius_cm
        for name in ZONE_THICKNESS_FIELDS:
            radius += getattr(self, name)
            radii.append(radius)
        return tuple(radii)

    @property
    def outer_radius_cm(self) -> float:
        """Outer radius of the whole build."""
        return self.zone_outer_radii_cm[-1]

    def to_record(self) -> dict[str, float]:
        """Project the geometry to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in GEOMETRY_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the geometry canonically.

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
        """Identify the exact geometry.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Decoded object.
    field
        Field name.

    Returns
    -------
    float
        The value as a float.

    Raises
    ------
    DeviceGeometryError
        If the field is absent or is not a real number.
    """
    if field not in record:
        raise DeviceGeometryError(f"{field}: required")
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeviceGeometryError(f"{field}: must be a real number, got {value!r}")
    return float(value)


def geometry_from_record(record: dict[str, Any]) -> DeviceGeometry:
    """Build a geometry from a decoded record, refusing unknown fields.

    Parameters
    ----------
    record
        Decoded object carrying exactly :data:`GEOMETRY_FIELDS`.

    Returns
    -------
    DeviceGeometry
        The validated geometry.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, unknown, or violates a
        model invariant.
    """
    unknown = sorted(set(record) - set(GEOMETRY_FIELDS))
    if unknown:
        raise DeviceGeometryError(f"geometry: unknown fields {unknown!r}")
    return DeviceGeometry(**{name: _number(record, name) for name in GEOMETRY_FIELDS})
