<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Fusion Fission Hybrid Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-FUSION-FISSION-HYBRID-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`SubcriticalBlanket`,
  `NeutronSource`, `DeviceConfiguration`) rejecting non-finite values,
  non-positive extents, an unknown fertile class, and any multiplication
  factor outside the strictly subcritical interval `(0, 1)` — the hard
  invariant of a driven hybrid blanket — with every rejection branch
  tested.
- The subcritical multiplication `M = 1 / (1 - k_eff)` (cf. Bethe,
  Phys. Today 32 (1979) 44) as a documented derived quantity, with an
  advisory finding for `k_eff > 0.98` (inside the documented margin to
  criticality), reported and never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- Nothing here is a nuclear-safety, criticality-safety, or licensing
  statement; the estimates are advisory bookkeeping checks, not
  neutronics, breeding, or energy-balance results; no benchmark,
  dataset, solver, controller, or experimental correlation exists in
  this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The nullable `timing_uncertainty_s` member, declared `null` on every
  channel because no event-relative candidate is applicable here; a
  non-null value is refused. This keeps the channel shape identical across
  the portfolio under envelope 1.1.0.
- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, and incomplete candidate coverage — every rejection
  branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: a blanket thermal-response set and a neutron-flux
  monitor set (noncyclic against the source epoch), and the
  model-owned synthetic oscillator (simulation clock).
- A documented advisory check with its source stated in the code:
  sampling far above the second-scale delayed-neutron and thermal
  response of a subcritical blanket is flagged (Bethe 1979); findings
  are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No criticality instrumentation, nuclear-safety monitoring, or
  reactivity measurement capability is claimed or implied; independent
  nuclear-safety authority is unaffected by any declaration here.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_fusion_fission_hybrid_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; no `timing_marker` (no
  event-relative candidate is applicable); numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record:
`docs/adr/0005-level0-device-physics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The four published figures of merit of a fusion-fission hybrid: the
  thermal power ratio (equation 1), the hybrid electrical efficiency
  (equation 2), the off-line and on-line capacity ratios (equations 6
  and 7), and the number of fission reactors supported (equation 4).
- Their agreement where the source states one: equation 7 against the
  form of equation 5, over a sweep of driver and blanket values. The
  agreement is asserted within a relative tolerance and not as an
  equality, because measurement over 6372 parameter points showed 317 of
  them disagreeing in the last places — the two forms group the same
  factors differently, and floating-point multiplication is not
  associative.
- Fail-closed refusal of every declared input outside its documented
  interval, each naming its field, both at the relation and at the
  declaration. Nothing is clamped. A conversion ratio of one or more is
  refused rather than reduced, because a fission reactor that needs no
  fissile makeup supports no hybrid.
- The record's two multiplications reported separately and derived from
  each other in neither direction: the declared blanket **energy**
  multiplication, and the **neutron** multiplication `1 / (1 - k_eff)`
  the configuration's own blanket computes. A test moves one and shows
  the other stand still.
- Canonical serialisation with a SHA-256 digest, its idempotence under
  re-canonicalisation, and its movement under a changed configuration.

Anchors — six numbers ORNL/PPA-79/3 prints, each recovered **from a
built record or a built relation** rather than stored beside one:

| Printed | Where | Recovered |
|---|---|---|
| `1.33` | denominator of equation 17 | exactly, as the same IEEE double |
| `R_o = 68` | equation 19 | 68.15 |
| `Q' ~ 1.4` for electrical self-sufficiency | page 26 | 1.396 |
| thorium supports 3–5× the uranium blankets | page 10, first noteworthy point | 4.70 fresh, 4.03 exposed |
| a larger blanket multiplication reaches its ceiling at a lower `Q'` | page 10, second noteworthy point | asserted as the identity `Q'B/(1+Q'B)` |
| ~3 % fissile buildup roughly halves the reactor number | page 10, third noteworthy point | 2.08 uranium, 2.42 thorium |

The filed copy is a scan whose OCR text layer mangles digits — it renders
the 17.0 of Table 1 as `]7.0` and the 5 of Table C4 as `J`. Every value
above was read off the rendered page image instead.

No parameter set describes any real machine, and nothing in the record
is a criticality-safety, nuclear-safety, licensing, safeguards or
proliferation-resistance statement.

## Device 3D model

Evidence record of the `device_3d_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Eight bodies in a fixed order — the plasma column and one per material
  zone of the radial build — each a cylinder or an annular tube about `z`
  from the shared kernel library.
- **The anchor, twice over.** Table C1 of the filed report prints both the
  zone thicknesses and the outer radii they produce. The geometry is
  declared from the thicknesses alone, so all eight printed outer radii
  are computed; every one comes back as the same IEEE double, asserted as
  an equality with no tolerance. The stronger form of the same check reads
  the outermost vertex of each built body back out and recovers the same
  eight radii from the tessellation itself.
- The vacuum zone carrying no body, and the first annulus therefore
  beginning at the outer edge of that gap rather than at the plasma edge.
- The tessellation losing exactly the inscribed polygon and nothing else:
  the column volume over its closed form is `(n / 2 pi) sin(2 pi / n)` at
  8, 64 and 256 segments, and the seven annuli together tile the space
  between the gap and the outer radius to the same ratio.
- A geometric fact the first version of its test got backwards: a thinner
  zone further out can enclose more than a thicker one further in. The
  printed reflector is 40 cm against the salt's 42 and encloses about
  18 % more, because an annulus grows as `r_out^2 - r_in^2`.
- Fail-closed refusal of every non-positive or non-finite field and of an
  invalid segment count, each naming its field; a parser that refuses a
  missing, unknown or mistyped field, booleans included.
- The body set and its order validated on the container as well as in the
  builder.
- Canonical serialisation with a SHA-256 digest that moves with the
  geometry, the segment count and the configuration.

## Device CAD model

Evidence record of the `device_cad_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The same eight bodies as exact B-rep solids through the shared library's
  `cad` group, each checked fail-closed by the library's evidence kernel
  against its analytic closed forms and against its tier-G1 twin, and
  exported as normalised STEP bytes with a digest.
- **Which deflection binds, measured for this family rather than copied.**
  At the declared 1e-4 m and 0.02 rad the angular criterion binds: the
  eight bodies span radii from one metre to two and a third and every
  deficit agrees to about seven significant figures.
- A coarser angular deflection of 0.1 rad is **refused**, and not on the
  deficit bound but on the comparison against the tier-G1 reference,
  naming the coolant channel — a five-millimetre annulus at a radius of a
  metre and a half is what a coarse mesher breaks first.
- A finer linear deflection of 1e-5 m is accepted but **narrows** the
  margin, from about five times to about one and a half: it does improve
  the faceting here, unlike in the tokamak family, but not as fast as it
  tightens the bound `2 d / r`. Finer is not safer, and that is asserted.
- Every body inside its declared bound, the narrowest margin at the
  outermost body and still more than four times.
- Fail-closed refusal of a manifest of the wrong schema or body count and
  of bodies out of order, on the container itself.
- STEP bytes present, their digest matching them, and two different builds
  producing different bytes.
- Canonical serialisation with a SHA-256 digest, and the model bound to
  the configuration and geometry digests it was built from.

Determinism of the STEP bytes is claimed within one pinned back-end
environment only, never across back-end versions. No body carries the
material it is named for, nothing here is a nuclear-safety,
criticality-safety or licensing statement, and no value describes any
real machine.
