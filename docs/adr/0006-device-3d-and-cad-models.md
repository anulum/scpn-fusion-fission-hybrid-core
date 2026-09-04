<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models of the radial build

Status: accepted (2026-09-04). Adds the fourth and fifth implemented
capabilities, `device_3d_model` and `device_cad_model`, under the
evidence-maturity ceiling rule of ADR 0002.

## Context

This repository's configuration carries no dimension. It declares a
blanket's multiplication factor and fertile class and a neutron source
rate, and nothing about size. So a geometry tier here is not a matter of
reading dimensions out of the configuration, as it is for the
magneto-inertial families: every length has to come from somewhere else.

It comes from the filed report. ORNL/PPA-79/3 tabulates the
calculational model of its hybrid in Table C1 as nine concentric zones,
each with a thickness and an outer radius, from a plasma column of one
metre out to a structural shell at 2.365 metres.

## Decision

Model that stack. Eight bodies — the plasma column and one per material
zone — each a cylinder or an annular tube about `z`, all within the
shared kernel library as it stands.

**Declare thicknesses, derive radii.** The table prints both columns, and
the direction matters. A thickness is positive or it is refused; a stack
of independently declared radii can be given out of order and still look
valid. Declaring the thicknesses also turns the table's second column
into an anchor: the eight printed outer radii are *recovered* from the
build rather than restated in it, and they come back as the same IEEE
doubles, so the test asserts an equality and needs no tolerance.

**The vacuum is a gap and carries no body.** The filed model counts it as
a zone because a transport calculation must, but empty space is not a
solid and drawing it as one would put a body where a reader expects a
void. The first annulus therefore begins at the outer edge of that gap.

**The body set follows the source, not the plan's sketch.** The rollout
plan named three bodies — fusion core, blanket annulus, reflector. The
table prints a first wall, a coolant channel and three separate
structural shells besides, and the report's own neutron balance puts
about a third of the absorption in them. Collapsing them would have made
the geometry disagree with the physics of the same document.

**The axial length is declared, not sourced.** The filed model is
one-dimensional and prints no length. The model records say so, so that a
reader who takes the radii as anchors does not take the length for one.

## The faceting deflections, measured for this family

The tier-G2 evidence kernel bounds each body's faceted volume by
`2 d / r`. Which of the two deflections binds depends on the device, and
this group now contains both regimes, so the numbers were measured here
rather than copied from a sibling.

- At the declared 1e-4 m and 0.02 rad, the **angular** criterion binds:
  the eight bodies span radii from one metre to two and a third, and
  every relative deficit agrees to about seven significant figures.
- A **coarser** angular deflection of 0.1 rad is refused — and not on the
  deficit bound but on the comparison against the tier-G1 reference,
  naming the coolant channel. A five-millimetre annulus at a radius of a
  metre and a half has almost no radial extent to absorb a coarse chord,
  so the thinnest zone is what a coarse mesher breaks first.
- A **finer** linear deflection of 1e-5 m is accepted but narrows the
  margin, from about five times to about one and a half. It does improve
  the faceting here — the deficits fall from a uniform 1.663e-5 to a
  spread of 1.331e-5 down to 3.501e-6 as the linear criterion begins to
  bind on the outer bodies — but not as fast as it tightens the bound.
  This is where the family differs from the tokamak one, where the
  deficit did not move at all.

Finer is therefore not safer, and a test asserts that directly.

## Consequences

Both capabilities are registered at `computational_prototype` with their
evidence pointers in `VALIDATION.md`, and the package carries 100 %
statement and branch coverage.

This landing gives the repository its first dependency: the shared kernel
library pinned by commit, with the CAD back-end as an optional extra
naming the same commit. Three workflows gain an install step and the test
workflow the system library the mesher links against.

Nothing here is a nuclear-safety, criticality-safety or licensing
statement, no body carries the material it is named for, and no value
describes any real machine.
