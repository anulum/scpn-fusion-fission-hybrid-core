<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The fusion–fission hybrid is the
portfolio's only `hybrid` configuration: its identity is the coupling of a
fusion neutron source (owned elsewhere) to a subcritical fission blanket.
The boundary must prevent this repository from absorbing source physics on
one side and plant engineering on the other, and must keep nuclear-safety
authority explicitly out of software scope.

## Decision

1. `SCPN-FUSION-FISSION-HYBRID-CORE` owns exactly one registry
   configuration: `fusion_fission_hybrid` (fusion source with subcritical
   blanket).
2. The repository owns coupling truth only: source-to-blanket neutronics
   coupling contracts, blanket multiplication and subcriticality-margin
   accounting declarations, energy-multiplication and fuel-conversion
   bookkeeping contracts, source-following lifecycle semantics,
   coupled-system diagnostic and clock declarations, actuator-response
   model boundaries, the safety-envelope declaration, and the
   device-owned CONTROL adapter specification.
3. Fusion-source physics stays with the designated source device core per
   configuration; ordinary blanket and balance-of-plant utilities are
   out-of-scope plant engineering; subcriticality assurance is
   nuclear-safety territory this repository declares and never
   implements — no nuclear-safety, criticality-safety, or licensing claim
   of any kind is made.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **Folding the hybrid into a source device core** (the source dominates
  operations): rejected — the hybrid's defining question is blanket
  coupling and multiplication accounting, orthogonal to any one source
  family; the map keeps one owner for the coupling.
- **Extending scope to blanket engineering**: rejected — the portfolio
  standard treats downstream plant subsystems as out of scope for
  confinement repositories; only coupling contracts live here.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the hybrid coupling
  and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
