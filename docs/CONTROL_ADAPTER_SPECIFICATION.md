<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — CONTROL adapter specification
-->

# CONTROL adapter specification

**Adapter identifier:** `scpn-fusion-fission-hybrid-core.control-adapter`  
**Contract version:** `0.1.0-spec` (specification only — **no implementation
exists**)  
**Consumer:** `SCPN-CONTROL` plugin protocol

This document is the device-owned contract through which a future hybrid
adapter would supply coupling truth to the SCPN control plane. Publishing
this specification creates no capability and no claim: an implementation
may appear only with the replay fixtures and evidence the reactor family
standard requires for `control_research_ready`, and it enters CONTROL only
through CONTROL's installed public contract with real-surface tests.

## Authority model (non-negotiable semantics)

1. The adapter **supplies declarations and observations; it never
   actuates**. It exposes no verb that writes to plant hardware.
2. `SCPN-CONTROL` alone admits observations and forms `ControlAction`
   values. The adapter cannot construct, forward, or replay a
   `ControlAction`.
3. SPO semantic output consumed alongside adapter data is `review_only`
   (`actionable = false`); the adapter must not re-label it.
4. Independent machine protection retains the final veto on every plant
   path. Subcriticality assurance of the blanket is nuclear-safety
   territory: the adapter declares margins as observations and neither
   implements nor substitutes for any criticality-safety function.
5. Every adapter payload carries provenance (source, clock identity,
   contract version); CONTROL rejects payloads without it.

## Contract surfaces

### 1. Observation schema (device → CONTROL)

Declared per diagnostic channel:

- channel identifier and physical quantity with SI unit — including
  source-rate channels (referenced to the designated source core's
  declarations), blanket flux and multiplication monitors,
  subcriticality-margin accounting channels, energy-multiplication
  bookkeeping channels, and blanket thermal channels with exact
  definitions;
- coordinate convention (source-relative and blanket-zone labels) and
  spatial layout (scalar, zone array, or profile);
- sampling clock identity and timestamp semantics (source and
  blanket-response time bases declared separately);
- uncertainty representation (declared per channel; absent uncertainty is
  an explicit `unquantified` marker, never an implied zero);
- validity and quality flags with fail-closed semantics.

### 2. State schema (device → CONTROL)

- lifecycle phase (`blanket_acceptance`, `source_ramp`,
  `coupled_operation`, `source_shutdown`, `terminated`) with monotonic
  transition semantics and device-truth event records for
  multiplication-margin erosion and source-blanket misalignment;
- configuration identity: the `fusion_fission_hybrid` registry
  configuration, the declared source class and blanket-concept revision,
  and the configuration policy revision that produced the run;
- device availability state for control research (simulation, replay, HIL;
  live plant states are out of scope for this contract version).

### 3. Actuator-capability declaration (device → CONTROL)

For each actuator class (source-side programming referenced through the
source core's own adapter contract, blanket configuration systems,
coolant-loop declarations):

- declared capability envelope (bounds, slew limits, latency class) as
  device truth for CONTROL's admission checks — the hybrid adapter
  declares coupling envelopes; source actuation authority remains with
  the source core's contract and is never duplicated here;
- explicit marker `direct_actuation: false`.

### 4. Safety-envelope declaration (device → CONTROL and protection review)

- machine-readable operational envelope (source-rate bounds within
  declared coupling limits, multiplication-margin floors, blanket
  thermal bounds with applicability domains);
- declared device-level hazard semantics for margin erosion and thermal
  excursions;
- statement of the independent machine-protection and nuclear-safety
  boundaries this envelope is subordinate to.

### 5. Replay fixtures contract (evidence)

An implementation must ship replay fixtures that exercise every schema
above through CONTROL's real admission path: nominal coupled runs,
margin-erosion sequences, boundary-of-envelope cases, invalid-payload
rejections, and clock-mismatch rejections. Fixtures are versioned with the
adapter and their digests recorded; HIL evidence is additionally required
before `control_research_ready` may be declared.

## Versioning rules

- `0.x` specification versions may change with a recorded revision note in
  this file and a manifest update in the same commit.
- From the first implemented `1.0.0`, changes follow semantic
  compatibility: breaking schema changes require a major version, a
  translation path or governed deprecation, and re-run producer/consumer
  evidence on both sides.
- The manifest (`reactor-domain.json` → `control_adapter`) always records
  the exact contract version; validator and drift checks keep the two
  files in agreement.
