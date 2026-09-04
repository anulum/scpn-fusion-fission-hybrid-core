<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — device model contract
-->

# Device model contract

What a consumer of this repository's device models may rely on, written
from the code rather than from a template. Design record:
`docs/adr/0006-device-3d-and-cad-models.md`.

## The two tiers

| Tier | Record | Schema | Built from |
|---|---|---|---|
| G1, tessellated | `DeviceModel3D` | `scpn.fusion-fission-hybrid-3d-model.v1` 1.0.0 | the library's `geometry` group |
| G2, B-rep | `DeviceModelCAD` | `scpn.fusion-fission-hybrid-cad-model.v1` 1.0.0 | the library's `cad` group |

Both are built from the same validated `DeviceConfiguration` and
`DeviceGeometry` and describe the same eight bodies. Tier G2 is optional:
it needs the `cad` extra, and every other capability of this package works
without a B-rep back-end.

## Units and frame

| Quantity | Value |
|---|---|
| length | metre |
| handedness | right |
| axis | `z` along the axis of the plasma column and of the blanket stack |
| origin | `z = 0` at the midplane of the build |

The **records** are in metres. The **declarations** are in centimetres,
because that is the unit the filed calculational model tabulates its
radial build in, and the field names carry it.

## The bodies, in this order

| Name | Role | Material token |
|---|---|---|
| `plasma_column` | `plasma` | `plasma` |
| `first_wall` | `structure` | `structural_steel` |
| `coolant_channel` | `coolant` | `coolant_water` |
| `inner_structure` | `structure` | `structural_steel` |
| `molten_salt_blanket` | `blanket` | `molten_salt` |
| `outer_structure` | `structure` | `structural_steel` |
| `reflector` | `reflector` | `graphite` |
| `backing_structure` | `structure` | `structural_steel` |

The order is fixed and checked at construction on both tiers.

**The vacuum zone carries no body.** The filed model counts it as a zone
because a transport calculation must; empty space is not a solid, so the
first annulus begins at the outer edge of that gap rather than at the
plasma edge.

## Where each dimension comes from

**All of them from the geometry.** This repository's configuration carries
no dimension at all — a blanket's multiplication factor and fertile class,
a source rate, and nothing about size — so unlike every magneto-inertial
family there is nothing to cross-check against and no relation between the
two to refuse.

The geometry declares the plasma radius, eight zone **thicknesses** and an
axial length, and derives the outer radii. That direction is deliberate: a
thickness is positive or it is refused, whereas a stack of independently
declared radii can be given out of order and still look valid. It also
makes the filed table's radius column something the build **recovers**
rather than restates.

**The axial length is declared, not sourced.** The filed calculational
model is one-dimensional and prints no length. A consumer may treat the
radii as anchored on a filed source; it may not treat the length that way.

## Exports and identity

Both records serialise canonically (sorted keys, minimal separators, a
trailing newline, NaN and infinity refused) and carry a SHA-256 digest of
those bytes. Each binds the digests of the configuration and the geometry
it was built from. Tier G2 additionally carries normalised STEP bytes with
their own digest and the versions of the pinned back-ends.

## Declared limits

- **STEP determinism is claimed inside one pinned back-end environment
  only**, never across back-end versions. The record carries the versions.
- The faceting comparison runs at a linear deflection of `1e-4 m` and an
  angular deflection of `0.02 rad`, against an 8-segment tier-G1
  reference. Both are measured for this family, and both directions away
  from them are worse:
  - a **coarser** angular deflection of `0.1 rad` is refused, and not on
    the deficit bound but on the comparison against the tier-G1
    reference, naming the `coolant_channel`. A five-millimetre annulus at
    a radius of a metre and a half has almost no radial extent to absorb
    a coarse chord, so the thinnest zone breaks first.
  - a **finer** linear deflection of `1e-5 m` is accepted but narrows the
    margin from about five times to one and a half: it improves the
    faceting, but not as fast as it tightens the bound `2 d / r`.
- The evidence kernel **refuses** a body that misses its bound, naming the
  body.

## Non-claims

- The zones are drawn at their declared thicknesses. No coolant channel,
  manifold, penetration, support or fuel-handling route is modelled, and
  a body named for a material carries no material.
- No body is an engineering model; no material property, load, field,
  criticality or neutronic quantity or fabrication tolerance is carried.
- Nothing here is a nuclear-safety, criticality-safety or licensing
  statement.
- No value describes or validates any real machine. Where a record
  reproduces a dimension a filed source prints, that is an anchor on the
  geometry and nothing further.
