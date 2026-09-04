# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — device geometry tests

"""Every branch of the radial build and its parser, and the printed anchor.

The anchor is the one that matters: Table C1 of the filed report prints
both the zone thicknesses and the outer radii they produce, and the
geometry is declared from the thicknesses so the radii are recovered.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

import pytest

from geometry_fixtures import (
    DECLARED_LENGTH_CM,
    TABLE_C1_OUTER_RADII_CM,
    TABLE_C1_THICKNESSES_CM,
    anchor_geometry,
    reference_geometry,
)
from scpn_fusion_fission_hybrid_core.errors import DeviceGeometryError
from scpn_fusion_fission_hybrid_core.geometry import (
    GEOMETRY_FIELDS,
    ZONE_THICKNESS_FIELDS,
    geometry_from_record,
)


def test_every_printed_outer_radius_is_recovered_from_the_printed_thicknesses() -> None:
    """Table C1 prints both columns, and one produces the other exactly.

    The geometry is declared from the thicknesses alone, so the eight
    outer radii are computed and not stored. Every one reproduces the
    printed value as the same IEEE double — no tolerance is needed,
    because the arithmetic is a running sum of values that are exact in
    binary or exact halves.
    """
    assert anchor_geometry().zone_outer_radii_cm == TABLE_C1_OUTER_RADII_CM


def test_the_outer_radius_of_the_build_is_the_last_printed_one() -> None:
    """The stack ends where the table says it ends."""
    assert anchor_geometry().outer_radius_cm == TABLE_C1_OUTER_RADII_CM[-1]


def test_the_zone_count_matches_the_thicknesses_declared() -> None:
    """One outer radius per zone thickness, and no more."""
    geometry = anchor_geometry()
    assert len(geometry.zone_outer_radii_cm) == len(ZONE_THICKNESS_FIELDS)
    assert len(TABLE_C1_OUTER_RADII_CM) == len(ZONE_THICKNESS_FIELDS)


def test_the_radii_increase_outward() -> None:
    """A thickness is positive, so a stack of them can only grow."""
    radii = anchor_geometry().zone_outer_radii_cm
    assert list(radii) == sorted(radii)
    assert radii[0] > anchor_geometry().plasma_radius_cm


@pytest.mark.parametrize("field", GEOMETRY_FIELDS)
@pytest.mark.parametrize("value", [0.0, -1.0, math.nan, math.inf])
def test_every_field_is_refused_by_name_when_not_positive(
    field: str, value: float
) -> None:
    """Each declared value is validated, and the refusal names it."""
    with pytest.raises(DeviceGeometryError, match=field):
        anchor_geometry(**{field: value})


def test_the_record_carries_exactly_the_declared_fields() -> None:
    """The projection neither loses nor invents a field."""
    record = anchor_geometry().to_record()
    assert set(record) == set(GEOMETRY_FIELDS)
    assert record == {**TABLE_C1_THICKNESSES_CM, "length_cm": DECLARED_LENGTH_CM}


def test_the_canonical_bytes_are_canonical() -> None:
    """Sorted keys, minimal separators and exactly one trailing newline."""
    data = anchor_geometry().canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    again = json.dumps(
        json.loads(data), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert (again + "\n").encode("utf-8") == data


def test_the_digest_identifies_the_geometry() -> None:
    """The digest is the SHA-256 of the canonical bytes and moves with them."""
    geometry = anchor_geometry()
    assert (
        geometry.digest_sha256()
        == hashlib.sha256(geometry.canonical_bytes()).hexdigest()
    )
    assert anchor_geometry(salt_thickness_cm=21.0).digest_sha256() != (
        geometry.digest_sha256()
    )
    assert reference_geometry().digest_sha256() != geometry.digest_sha256()


def test_a_record_round_trips_through_the_parser() -> None:
    """Parsing a projection reproduces the geometry exactly."""
    geometry = anchor_geometry()
    assert geometry_from_record(geometry.to_record()) == geometry


@pytest.mark.parametrize(
    ("record", "match"),
    [
        ({}, "plasma_radius_cm"),
        ({"extra": 1.0}, "unknown fields"),
    ],
)
def test_the_parser_refuses_a_missing_or_unknown_field(
    record: dict[str, Any], match: str
) -> None:
    """A missing or unknown field is refused, never defaulted or ignored."""
    with pytest.raises(DeviceGeometryError, match=match):
        geometry_from_record(record)


@pytest.mark.parametrize("value", ["42", True, None, [42.0]])
def test_the_parser_refuses_a_field_that_is_not_a_real_number(value: Any) -> None:
    """A boolean is refused explicitly.

    Python would otherwise accept it as an integer and read ``True`` as a
    thickness of one centimetre.
    """
    record = {
        **TABLE_C1_THICKNESSES_CM,
        "length_cm": DECLARED_LENGTH_CM,
        "salt_thickness_cm": value,
    }
    with pytest.raises(DeviceGeometryError, match="real number"):
        geometry_from_record(record)


def test_an_integer_thickness_is_accepted_as_a_real_number() -> None:
    """JSON carries no float-integer distinction, so an integer is a length."""
    record = {
        **TABLE_C1_THICKNESSES_CM,
        "length_cm": DECLARED_LENGTH_CM,
        "salt_thickness_cm": 42,
    }
    assert geometry_from_record(record).salt_thickness_cm == 42.0
