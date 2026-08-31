<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — Architecture summary
-->

# Architecture summary

`SCPN-FUSION-FISSION-HYBRID-CORE` is the device-family owner for
fusion–fission hybrid systems inside the SCPN Reactor Systems Research
Group. The repository holds two implemented capabilities at
`computational_prototype` — the device configuration model (ADR 0002)
and the diagnostic and clock semantics model (ADR 0003), both in
`src/scpn_fusion_fission_hybrid_core/` — alongside the coupling
boundary, its ecosystem contracts, and the validation tooling that
enforces both.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns fusion–fission coupling
truth — source-to-blanket neutronics coupling contracts, subcritical
multiplication and margin accounting declarations (effective
multiplication strictly below unity as a declared boundary),
energy-multiplication bookkeeping, source-following lifecycle semantics
with margin-erosion hazard records, coupled-system diagnostic and clock
declarations, actuator-response boundaries that never duplicate source
authority, safety-envelope declarations subordinate to independent
nuclear-safety authority, and the device-owned CONTROL adapter
specification — with no nuclear-safety, criticality-safety, or licensing
claim of any kind. Source physics belongs to the designated source cores;
solver mathematics to `SCPN-FUSION-CORE`; typed semantics to
`SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control actions are
formed only by `SCPN-CONTROL`; independent machine protection keeps the
final veto; portfolio presentation belongs to `SCPN-STUDIO`, towards which
this project is `not_federated`.
