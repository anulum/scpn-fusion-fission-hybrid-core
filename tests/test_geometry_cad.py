# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — tier-G2 device model tests

"""Every branch of the tier-G2 model, and what its faceting is limited by.

The builds are cached: each costs about three seconds, and rebuilding one
per test buys no evidence a single build does not already carry.
"""

from __future__ import annotations

import functools
import hashlib
import json

import pytest

from geometry_fixtures import (
    anchor_geometry,
    reference_geometry,
    synthetic_configuration,
)
from scpn_fusion_fission_hybrid_core.errors import DeviceGeometryError
from scpn_fusion_fission_hybrid_core.geometry import (
    BODY_NAMES,
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

#: Relative agreement the bodies' faceting deficits hold to at the
#: declared deflections. They are not bit-equal: measured across the eight
#: bodies, the spread is 2.9e-7 on the anchored build and 5.4e-8 on the
#: synthetic one, so this sits an order above the larger of the two.
DEFICIT_AGREEMENT = 3e-6


@functools.cache
def anchor_model() -> DeviceModelCAD:
    """Build and cache the Table C1 B-rep model."""
    return build_device_cad(synthetic_configuration(), anchor_geometry())


@functools.cache
def reference_model() -> DeviceModelCAD:
    """Build and cache the synthetic reference B-rep model."""
    return build_device_cad(synthetic_configuration(), reference_geometry())


def deficits(model: DeviceModelCAD) -> list[float]:
    """Return each body's relative faceted-volume deficit."""
    return [
        body.to_record()["faceted_volume_relative_deficit"] for body in model.bodies
    ]


def bounds(model: DeviceModelCAD) -> list[float]:
    """Return each body's declared faceted-volume deficit bound."""
    return [body.to_record()["faceted_volume_deficit_bound"] for body in model.bodies]


def test_the_body_set_and_its_order_are_fixed() -> None:
    """The same eight bodies as tier G1, in the same order."""
    assert tuple(body.name for body in anchor_model().bodies) == BODY_NAMES


def test_every_body_stays_inside_its_declared_bound() -> None:
    """The evidence kernel checked each body, and each passed with margin.

    The narrowest margin is at the backing structure, the outermost and
    therefore largest-radius body, whose bound is the tightest. Measured,
    it is still five times.
    """
    model = anchor_model()
    margins = [
        bound / deficit
        for deficit, bound in zip(deficits(model), bounds(model), strict=True)
    ]
    assert min(margins) > 4.0
    assert margins[-1] == min(margins)


def test_the_faceting_deficit_does_not_depend_on_the_radius_at_these_deflections() -> (
    None
):
    """At the declared deflections one angular step is used everywhere.

    The eight bodies span radii from one metre to two and a third, yet
    every deficit agrees to about nine significant figures. That is the
    signature of an angular criterion: the mesher divides each circle into
    the same number of segments whatever its radius.
    """
    every = deficits(anchor_model()) + deficits(reference_model())
    for value in every[1:]:
        assert value == pytest.approx(every[0], rel=DEFICIT_AGREEMENT)
    assert len(set(every)) > 1


def test_a_finer_linear_deflection_narrows_the_margin_rather_than_widening_it() -> None:
    """Finer is not safer: the bound tightens faster than the faceting improves.

    The declared bound is ``2 d / r``. Making ``d`` ten times finer divides
    it by ten. The faceting does improve here — unlike in the tokamak
    family, where it did not move at all — but not by as much, so the
    narrowest margin falls from about five times to about one and a half.

    Measured rather than reasoned: at 1e-4 the deficits are uniform at
    1.663e-5, and at 1e-5 they spread from 1.331e-5 down to 3.501e-6 as the
    linear criterion starts to bind on the outer bodies.
    """
    finer = build_device_cad(
        synthetic_configuration(),
        anchor_geometry(),
        linear_deflection_m=DEFAULT_LINEAR_DEFLECTION_M / 10.0,
    )
    coarse_margin = min(
        b / d
        for d, b in zip(deficits(anchor_model()), bounds(anchor_model()), strict=True)
    )
    fine_margin = min(
        b / d for d, b in zip(deficits(finer), bounds(finer), strict=True)
    )
    assert fine_margin < coarse_margin
    assert fine_margin > 1.0
    assert max(deficits(finer)) < max(deficits(anchor_model()))


def test_a_coarser_angular_deflection_is_refused_on_the_thinnest_zone() -> None:
    """The half-centimetre coolant channel is what a coarse mesher breaks first.

    At 0.1 rad the refusal is not the deficit bound at all but the
    comparison against the tier-G1 reference, and it names the coolant
    channel: a five-millimetre annulus at a radius of one and a half
    metres has almost no radial extent to absorb a coarse chord.
    """
    with pytest.raises(DeviceGeometryError, match="coolant_channel"):
        build_device_cad(
            synthetic_configuration(), anchor_geometry(), angular_deflection_rad=0.1
        )


def test_a_manifest_of_the_wrong_shape_is_refused() -> None:
    """The container validates the manifest it was handed, not only the build."""
    model = anchor_model()
    for broken, match in (
        ({**model.assembly_manifest, "schema": "wrong"}, "assembly_manifest.schema"),
        ({**model.assembly_manifest, "body_count": 3}, "body_count"),
    ):
        with pytest.raises(DeviceGeometryError, match=match):
            DeviceModelCAD(
                configuration_digest_sha256=model.configuration_digest_sha256,
                geometry_digest_sha256=model.geometry_digest_sha256,
                reference_mesh_segments=model.reference_mesh_segments,
                linear_deflection_m=model.linear_deflection_m,
                angular_deflection_rad=model.angular_deflection_rad,
                backend_versions=model.backend_versions,
                assembly_manifest=broken,
                step_sha256=model.step_sha256,
                bodies=model.bodies,
                step_data=model.step_data,
                faceted_meshes=model.faceted_meshes,
            )


def test_bodies_out_of_order_are_refused() -> None:
    """The fixed order is enforced on the container as well as the builder."""
    model = anchor_model()
    with pytest.raises(DeviceGeometryError, match="must be exactly"):
        DeviceModelCAD(
            configuration_digest_sha256=model.configuration_digest_sha256,
            geometry_digest_sha256=model.geometry_digest_sha256,
            reference_mesh_segments=model.reference_mesh_segments,
            linear_deflection_m=model.linear_deflection_m,
            angular_deflection_rad=model.angular_deflection_rad,
            backend_versions=model.backend_versions,
            assembly_manifest=model.assembly_manifest,
            step_sha256=model.step_sha256,
            bodies=model.bodies[::-1],
            step_data=model.step_data,
            faceted_meshes=model.faceted_meshes,
        )


def test_the_step_export_is_present_and_its_digest_matches_its_bytes() -> None:
    """The digest names the exact bytes the model carries."""
    model = anchor_model()
    assert model.step_data.startswith(b"ISO-10303-21;")
    assert model.step_sha256 == hashlib.sha256(model.step_data).hexdigest()


def test_two_builds_produce_different_step_bytes() -> None:
    """The export carries the design, not a template."""
    assert anchor_model().step_sha256 != reference_model().step_sha256


def test_the_record_carries_the_schema_units_and_non_claims() -> None:
    """The projection states what the model is and what it is not."""
    record = anchor_model().to_record()
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
    assert record["units"] == dict(CAD_MODEL_UNITS)
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert record["reference_mesh_segments"] == DEFAULT_REFERENCE_MESH_SEGMENTS
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)
    assert record["backend_versions"]


def test_the_canonical_bytes_are_canonical_and_the_digest_identifies_them() -> None:
    """One trailing newline, idempotent re-canonicalisation, matching digest."""
    model = anchor_model()
    data = model.canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    again = json.dumps(
        json.loads(data), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert (again + "\n").encode("utf-8") == data
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_both_tiers_are_bound_to_the_same_inputs() -> None:
    """The model names the configuration and the geometry it was built from."""
    model = anchor_model()
    assert model.configuration_digest_sha256 == (
        synthetic_configuration().digest_sha256()
    )
    assert model.geometry_digest_sha256 == anchor_geometry().digest_sha256()
