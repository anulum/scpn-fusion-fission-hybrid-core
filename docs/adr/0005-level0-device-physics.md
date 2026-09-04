<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics as published figures of merit

Status: accepted (2026-09-04). Adds the third implemented capability,
`level0_device_physics`, under the evidence-maturity ceiling rule of
ADR 0002.

## Context

Every other family in this group reaches its level-0 physics through a
device relation: an equilibrium, an implosion, a convergence. A hybrid
has no such relation of its own. Its fusion driver belongs to whichever
family drives it — a mirror, a tokamak, a laser — and its fission
blanket is a neutronics problem that no closed form describes. What is
distinctive about a hybrid is neither of the two halves but the
bookkeeping between them: how much thermal power the blanket adds to the
fusion power, how much of that recirculates to drive the plasma, and how
many fission reactors the bred fuel supports.

That bookkeeping is exactly what M. J. Saltmarsh, W. R. Grimes and
R. T. Santoro publish in ORNL/PPA-79/3 (1979) as four figures of merit.
Each is a ratio of energies and efficiencies, and each is closed.

The repository already carried `1 / (1 - k_eff)` on its blanket. That is
a neutron multiplication. The `M` of the figures of merit is an energy
multiplication — energy deposited in the blanket per source neutron over
the average source-neutron energy — and the two are different
quantities. No filed source relates them, so nothing here does either.

## Decision

Implement the four figures of merit as free functions over declared
inputs, and compose them into a level-0 record beside the neutron source
the configuration already carries.

- **Equation 1**, the thermal power ratio `1/Q' + 1 + f_n (M - 1)`.
- **Equation 2**, the hybrid electrical efficiency, the plant's thermal
  efficiency less the share that recirculates to the driver. It is
  allowed to be negative and is reported rather than refused, because
  the report's own molten-salt case sits at the zero crossing.
- **Equation 6**, the off-line capacity ratio, and through it
  **equation 4**, the number of fission reactors supported.
- **Equation 7**, the on-line capacity ratio, which the report derives
  from equations 1 and 2 and which must agree with the form of
  equation 5. A test asserts that agreement.

The blanket's fissile breeding rate and energy multiplication are
**declared inputs**, never computed. The report tabulates them from
neutronics calculations this repository does not perform and could not
check, and a level-0 module that produced its own would be asserting a
neutronics result it has no basis for.

A conversion ratio of one or more is refused rather than clamped. The
denominator `(1 - C)(1 + alpha)` counts the fissile atoms that must be
supplied per fission; a reactor that needs no makeup supports no hybrid,
and the figure of merit does not describe it.

The declared inputs are validated where they are declared as well as
inside each relation. A record can therefore never be built from a set
that the relations would have refused one at a time, and the rejection
names a field rather than surfacing from inside an expression.

## Anchoring: the report's own derived numbers

The report prints inputs and, separately, numbers it derives from them.
That is the strongest anchor available, because it lets a test show a
printed value is recoverable from a built record rather than merely
stored beside it. Six are recovered:

- The coefficient `1.33` printed in the denominator of equation 17,
  which is `1 + f_n (M - 1)` at the printed `f_n = 0.66` and
  `M = 1.5`. Measured, the two are the same IEEE double, so the test
  asserts an equality rather than a tolerance.
- `R_o = 68` printed in equation 19, recovered to 68.15 from the
  printed `F`, `C`, `alpha` and fusion energy.
- The engineering Q of about 1.4 the report states is required for
  electrical self-sufficiency, recovered as 1.396.
- The first noteworthy point of page 10, that the thorium blankets
  support three to five times what the uranium ones do: 4.70 and 4.03,
  fresh against fresh and exposed against exposed.
- The second, that a hybrid approaches its ultimate reactor number at a
  lower Q' when the blanket multiplication is larger. This one is an
  identity, not an observation: the fraction of the ceiling reached is
  `Q' B / (1 + Q' B)` with `B` the blanket term, so any fixed fraction
  is reached at Q' inversely proportional to `B`. It is asserted as an
  identity.
- The third, that a fissile buildup near 3% of the heavy metal roughly
  halves that number: 2.08 for uranium and 2.42 for thorium.

The filed copy is a scan. Every value used here was read off the
rendered page image, never the OCR text layer, which renders the 17.0 of
Table 1 as `]7.0` and the 5 of Table C4 as `J`.

## Consequences

The capability is registered at `computational_prototype` with its
evidence pointer at `VALIDATION.md#level-0-device-physics`, and the
package carries 100 % statement and branch coverage.

No kernel-library pin. Every relation is addition, multiplication and
division; unlike the magneto-inertial families this physics needs no
transcendental, so it names no library commit.

The record makes no statement about criticality, nuclear safety,
licensing, safeguards or proliferation resistance, and the non-claims
say so. The supported-reactor number is a steady-state power ratio and
is deliberately not rounded to an integer: rounding it would suggest a
fleet-sizing result that carries no availability, outage or fuel-cycle-
lag model.
