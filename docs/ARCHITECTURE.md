<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-FUSION-FISSION-HYBRID-CORE` is the device-family owner for
fusion–fission hybrid systems in the SCPN Reactor Systems Research Group
portfolio. The
repository owns one implemented capability — the device configuration model
at `computational_prototype` (`src/scpn_fusion_fission_hybrid_core/`, design record
ADR 0002, evidence record `VALIDATION.md#device-configuration-model`).
Every other section below describes boundaries and contracts. The claim
inventory is empty; capability and claim inventories are generated and
drift-checked.

## The five-surface boundary

1. **Governing physics** — the `fusion_fission_hybrid` configuration
   (fusion source with subcritical blanket, `hybrid` registry family):
   the device-defining physics is the **coupling** — fusion neutrons
   driving fission multiplication, breeding, or transmutation in a
   blanket whose effective multiplication stays strictly below unity, so
   the fission system's power follows the fusion source rather than a
   self-sustained chain. Source physics belongs to the designated source
   device core; the coupling contracts (source spectrum and rate to
   blanket response) are this repository's truth.
2. **Primary driver and energy delivery** — the declared fusion neutron
   source class (referencing its owning device core) plus blanket-side
   configuration: multiplication, breeding, and transmutation blanket
   concepts as declared classes, never as implemented capability.
3. **Plant and shot lifecycle** — source-following lifecycle: blanket
   state acceptance, source ramp within declared coupling envelopes,
   sustained coupled operation with continuous subcriticality-margin
   accounting, and source-led shutdown. Device-level hazard semantics
   cover multiplication-margin erosion, blanket thermal excursions, and
   source-blanket misalignment; subcriticality assurance itself is
   nuclear-safety territory that is declared, never implemented.
4. **Diagnostic, reference-frame, and clock model** — source-rate
   channels referenced to the source core's declarations, blanket flux
   and multiplication monitors, energy-multiplication accounting
   channels, and clock identities spanning source and blanket response
   timescales.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-FUSION-FISSION-HYBRID-CORE (coupling truth: source-blanket
                                 contracts, multiplication accounting,
                                 lifecycle, safety envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  source-class reference (never absorbed)
   ├──────────────► designated source device core (tokamak, mirror, …)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
