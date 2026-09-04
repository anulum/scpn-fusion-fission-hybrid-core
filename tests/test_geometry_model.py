# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — tier-G1 device model tests

"""Every branch of the tier-G1 model, and the printed stack it reproduces."""

from __future__ import annotations

import hashlib
import json
import math

import pytest

from geometry_fixtures import (
    TABLE_C1_OUTER_RADII_CM,
    anchor_geometry,
    inscribed_polygon_ratio,
    reference_geometry,
    synthetic_configuration,
)
from scpn_fusion_fission_hybrid_core.errors import DeviceGeometryError
from scpn_fusion_fission_hybrid_core.geometry import (
    BODY_NAMES,
    CM_PER_M,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    ZONE_BODIES,
    DeviceModel3D,
    body_radii_m,
    build_device_model,
)

REFERENCE_SEGMENTS = 64


def built(segments: int = REFERENCE_SEGMENTS) -> DeviceModel3D:
    """Build the anchored model at a segment count."""
    return build_device_model(synthetic_configuration(), anchor_geometry(), segments)


@pytest.mark.parametrize("segments", [0, 7, 12, -8])
def test_an_invalid_segment_count_is_refused_under_the_device_error(
    segments: int,
) -> None:
    """The library's rule is enforced, and its message is carried through."""
    with pytest.raises(DeviceGeometryError, match="segments"):
        build_device_model(synthetic_configuration(), anchor_geometry(), segments)


def test_the_body_set_and_its_order_are_fixed() -> None:
    """Eight bodies: the plasma column and one per material zone."""
    assert tuple(mesh.name for mesh in built().meshes) == BODY_NAMES
    assert len(BODY_NAMES) == len(ZONE_BODIES) + 1


def test_the_vacuum_zone_carries_no_body() -> None:
    """Empty space is not a solid, so the gap is a gap.

    The filed model counts the vacuum as a zone because a transport
    calculation must. The geometry does not, and the first annulus
    therefore begins at the outer edge of that gap rather than at the
    plasma edge.
    """
    assert "vacuum" not in " ".join(BODY_NAMES)
    first_inner, _ = body_radii_m(anchor_geometry())[0]
    assert first_inner == pytest.approx(TABLE_C1_OUTER_RADII_CM[0] * CM_PER_M)


def test_every_printed_outer_radius_is_recovered_from_the_built_bodies() -> None:
    """The anchor, stated on the bodies rather than on the declaration.

    Each annulus is built between two radii, and reading the outermost
    vertex of each body back out reproduces every outer radius Table C1
    prints. This is the stronger form of the check in the geometry suite:
    there the radii came from the geometry object, here from the
    tessellation itself.
    """
    model = built(512)
    recovered = [
        max(math.hypot(vertex[0], vertex[1]) for vertex in mesh.vertices)
        for mesh in model.meshes[1:]
    ]
    for value, printed in zip(recovered, TABLE_C1_OUTER_RADII_CM[1:], strict=True):
        assert value == pytest.approx(printed * CM_PER_M, rel=1e-12)


def test_the_plasma_column_carries_the_printed_plasma_radius() -> None:
    """Zone 1 of the table is the only body that is not an annulus."""
    column = built().meshes[0]
    radius = max(math.hypot(vertex[0], vertex[1]) for vertex in column.vertices)
    assert radius == pytest.approx(anchor_geometry().plasma_radius_cm * CM_PER_M)


@pytest.mark.parametrize("segments", [8, 64, 256])
def test_the_column_volume_is_the_analytic_volume_times_the_polygon_ratio(
    segments: int,
) -> None:
    """The tessellation loses exactly the inscribed polygon and nothing else.

    Asserted within a relative tolerance rather than as an equality: a
    mesh volume is a sum over many triangles and the closed form is three
    multiplications, so they part in the last places.
    """
    geometry = anchor_geometry()
    radius = geometry.plasma_radius_cm * CM_PER_M
    length = geometry.length_cm * CM_PER_M
    analytic = math.pi * radius * radius * length
    column = built(segments).meshes[0]
    assert math.isclose(
        column.signed_volume_m3() / analytic,
        inscribed_polygon_ratio(segments),
        rel_tol=1e-13,
    )


def test_the_zone_volumes_sum_to_the_whole_build_less_the_vacuum() -> None:
    """The stack is a partition: the annuli tile the space between radii.

    Their volumes add up to the annulus from the vacuum's outer edge to
    the build's outer radius, which is what a partition means and what a
    gap or an overlap would break.
    """
    geometry = anchor_geometry()
    model = built(512)
    inner = TABLE_C1_OUTER_RADII_CM[0] * CM_PER_M
    outer = geometry.outer_radius_cm * CM_PER_M
    length = geometry.length_cm * CM_PER_M
    analytic = math.pi * (outer * outer - inner * inner) * length
    total = sum(mesh.signed_volume_m3() for mesh in model.meshes[1:])
    assert math.isclose(total / analytic, inscribed_polygon_ratio(512), rel_tol=1e-12)


def test_a_thinner_zone_further_out_can_enclose_more_than_a_thicker_one() -> None:
    """Thickness does not order an annular stack by volume, and radius wins.

    The printed salt zone is 42 cm thick and the reflector 40, so the salt
    looks like the larger body. It is not: an annulus grows as
    ``r_out^2 - r_in^2``, and the reflector sits further out. Measured on
    the printed radii the reflector encloses about 18 % more.

    This test exists because the first version of it asserted the
    opposite, from thickness alone, and failed.
    """
    volumes = {mesh.name: mesh.signed_volume_m3() for mesh in built().meshes[1:]}
    assert volumes["reflector"] > volumes["molten_salt_blanket"]
    assert volumes["reflector"] / volumes["molten_salt_blanket"] == pytest.approx(
        1.183, abs=0.005
    )
    assert max(volumes, key=lambda name: volumes[name]) == "reflector"


def test_a_model_built_from_the_wrong_bodies_is_refused() -> None:
    """The container validates its own body set, not only the builder."""
    model = built()
    with pytest.raises(DeviceGeometryError, match="bodies must be exactly"):
        DeviceModel3D(
            configuration_digest_sha256=model.configuration_digest_sha256,
            geometry_digest_sha256=model.geometry_digest_sha256,
            segments=model.segments,
            meshes=model.meshes[::-1],
        )


def test_the_record_carries_the_schema_units_and_non_claims() -> None:
    """The projection states what the model is and what it is not."""
    record = built().to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["units"] == dict(MODEL_UNITS)
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)
    assert record["segments"] == REFERENCE_SEGMENTS


def test_the_canonical_bytes_are_canonical_and_the_digest_identifies_them() -> None:
    """One trailing newline, idempotent re-canonicalisation, matching digest."""
    model = built()
    data = model.canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    again = json.dumps(
        json.loads(data), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert (again + "\n").encode("utf-8") == data
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_the_digest_moves_with_the_geometry_and_with_the_segment_count() -> None:
    """Both inputs of the build reach the identity of the record."""
    base = built()
    other = build_device_model(
        synthetic_configuration(), reference_geometry(), REFERENCE_SEGMENTS
    )
    assert base.digest_sha256() != other.digest_sha256()
    assert base.digest_sha256() != built(REFERENCE_SEGMENTS * 2).digest_sha256()


def test_the_digest_moves_with_the_configuration() -> None:
    """A different blanket declaration is a different design."""
    other = build_device_model(
        synthetic_configuration(k_effective=0.8), anchor_geometry(), REFERENCE_SEGMENTS
    )
    assert other.digest_sha256() != built().digest_sha256()
