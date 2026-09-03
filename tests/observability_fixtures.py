# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — shared diagnostic and clock test fixtures

"""Shared fixtures for the diagnostic plan and clock semantics tests.

The catalogue bindings, signal inventories, clocks, frames, relations and
channel builders used by more than one surface live here so that each test
module states only what is particular to its own surface.

All plans in this module are synthetic fixtures; none describes any real
diagnostic, measurement, or facility.
"""

from __future__ import annotations

from typing import Any

from scpn_fusion_fission_hybrid_core.observability import (
    CATALOGUE_BINDING,
    ClockDomain,
    ClockKind,
    ClockModel,
    ClockRelation,
    ClockTopology,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    FrameTransformation,
    ReferenceFrame,
    SemanticCarrier,
    SignalDeclaration,
    SignalRole,
    TransformationKind,
)

NONCYCLIC_BINDINGS = {
    "calibration": "synthetic calibration set",
    "clock_epoch": "clk_shot",
    "coordinate_frame": "frm_blanket_zones",
    "provenance": "synthetic fixture",
    "quality": "synthetic quality flags",
    "uncertainty": "declared bounds",
    "units": "SI units declared per field",
    "validity": "synthetic validity window",
}


NUMERICAL_BINDINGS = {
    "initial_condition": "synthetic initial state",
    "model_revision": "model revision identifier",
    "provenance": "synthetic fixture",
    "simulation_clock": "clk_sim",
    "solver_validity": "declared solver validity envelope",
}


REFERENCE_FRAMES = (
    ReferenceFrame(
        identifier="frm_blanket_zones",
        kind=FrameKind.BLANKET_ZONE,
        description="declared blanket zone index frame",
    ),
    ReferenceFrame(
        identifier="frm_vessel",
        kind=FrameKind.MACHINE_CYLINDRICAL,
        description="vessel cylindrical frame",
    ),
)


CLOCK_RELATIONS = (
    ClockRelation(
        child_identifier="clk_shot",
        parent_identifier="clk_facility",
        max_offset_s=1.0e-6,
        uncertainty_s=1.0e-7,
        method=(
            "synthetic declaration: trigger timestamped against the "
            "facility oscillator; no correlation evidence claimed"
        ),
        mapping_state="unmapped",
        evidence_claimed=False,
    ),
)


SIGNALS_CH_BLANKET_THERMAL_SET = (
    SignalDeclaration(
        identifier="sig_blanket_temperature",
        quantity="temperature",
        unit="K",
        role=SignalRole.CARRIER,
        description="synthetic blanket temperature response",
    ),
    SignalDeclaration(
        identifier="sig_thermal_power",
        quantity="power",
        unit="W",
        role=SignalRole.AUXILIARY,
        description="synthetic blanket thermal power",
    ),
)


SIGNALS_CH_NEUTRON_FLUX_SET = (
    SignalDeclaration(
        identifier="sig_monitor_position",
        quantity="length",
        unit="m",
        role=SignalRole.AUXILIARY,
        description="declared monitor position",
    ),
    SignalDeclaration(
        identifier="sig_neutron_flux",
        quantity="particle_flux",
        unit="m^-2/s",
        role=SignalRole.CARRIER,
        description="synthetic blanket neutron flux",
    ),
)


SIGNALS_CH_SYNTHETIC_OSCILLATOR = (
    SignalDeclaration(
        identifier="sig_phase",
        quantity="phase",
        unit="rad",
        role=SignalRole.CARRIER,
        description="model-owned synthetic oscillator phase",
    ),
)


REFERENCE_TRANSFORMATIONS: tuple[FrameTransformation, ...] = (
    FrameTransformation(
        source_identifier="frm_blanket_zones",
        target_identifier="frm_vessel",
        kind=TransformationKind.PROJECTION,
        equilibrium_dependent=False,
        method=(
            "synthetic declaration: mapping between the declared frames; "
            "no mapping evidence claimed"
        ),
        evidence_claimed=False,
    ),
)


CLOCK_TOPOLOGY = ClockTopology(
    domains=(
        ClockDomain(
            identifier="dom_facility",
            root_clock_identifier="clk_facility",
            member_clock_identifiers=("clk_facility", "clk_shot"),
            scope="facility master timing and the shot trigger bound to it",
        ),
    ),
    reference_domain_identifier="dom_facility",
)


def clock_facility() -> ClockModel:
    """Build the synthetic facility master clock."""
    return ClockModel(
        identifier="clk_facility",
        kind=ClockKind.FACILITY_MONOTONIC,
        epoch="facility master oscillator zero",
        resolution_s=1.0e-8,
        uncertainty_s=5.0e-9,
    )


def clock_shot() -> ClockModel:
    """Build the synthetic source-epoch clock."""
    return ClockModel(
        identifier="clk_shot",
        kind=ClockKind.SHOT_EVENT_EPOCH,
        epoch="source turn-on t0",
        resolution_s=1.0e-6,
        uncertainty_s=1.0e-6,
    )


def clock_simulation() -> ClockModel:
    """Build the synthetic simulation clock."""
    return ClockModel(
        identifier="clk_sim",
        kind=ClockKind.SIMULATION,
        epoch="solver step zero",
        resolution_s=1.0e-9,
        uncertainty_s=0.0,
    )


def channel_thermal() -> DiagnosticChannelPlan:
    """Build the synthetic blanket thermal-response channel."""
    return DiagnosticChannelPlan(
        identifier="ch_blanket_thermal_set",
        candidate_id="hybrid.source_blanket_response",
        carrier=SemanticCarrier.BOUNDED_FEATURE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e1,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=3600.0,
        element_count=1,
        evidence_bindings=dict(NONCYCLIC_BINDINGS),
        signals=SIGNALS_CH_BLANKET_THERMAL_SET,
        synthetic=True,
    )


def channel_neutron_flux() -> DiagnosticChannelPlan:
    """Build the synthetic blanket neutron-flux monitor channel."""
    return DiagnosticChannelPlan(
        identifier="ch_neutron_flux_set",
        candidate_id="hybrid.source_blanket_response",
        carrier=SemanticCarrier.BOUNDED_FEATURE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e4,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=3600.0,
        element_count=8,
        evidence_bindings=dict(NONCYCLIC_BINDINGS),
        signals=SIGNALS_CH_NEUTRON_FLUX_SET,
        synthetic=True,
    )


def channel_oscillator() -> DiagnosticChannelPlan:
    """Build the synthetic model-oscillator channel."""
    return DiagnosticChannelPlan(
        identifier="ch_synthetic_oscillator",
        candidate_id="model.synthetic_oscillator_coordinate",
        carrier=SemanticCarrier.NUMERICAL_PHASE,
        clock_identifier="clk_sim",
        sample_rate_hz=1.0e4,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=100.0,
        element_count=1,
        evidence_bindings=dict(NUMERICAL_BINDINGS),
        signals=SIGNALS_CH_SYNTHETIC_OSCILLATOR,
        synthetic=True,
    )


def synthetic_plan() -> DiagnosticPlan:
    """Build a fully valid synthetic diagnostic plan."""
    return DiagnosticPlan(
        identifier="hybrid_reference_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock_shot(), clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel_thermal(),
            channel_neutron_flux(),
            channel_oscillator(),
        ),
        deferrals=(),
    )


def noncyclic_channel(**overrides: Any) -> DiagnosticChannelPlan:
    """Build the noncyclic blanket channel with keyword overrides applied."""
    values: dict[str, Any] = {
        "identifier": "ch_neutron_flux_set",
        "candidate_id": "hybrid.source_blanket_response",
        "carrier": SemanticCarrier.BOUNDED_FEATURE,
        "clock_identifier": "clk_shot",
        "sample_rate_hz": 1.0e4,
        "max_signal_frequency_hz": 0.0,
        "timing_uncertainty_s": None,
        "acquisition_start_s": 0.0,
        "acquisition_duration_s": 3600.0,
        "element_count": 8,
        "evidence_bindings": dict(NONCYCLIC_BINDINGS),
        "signals": SIGNALS_CH_NEUTRON_FLUX_SET,
        "synthetic": True,
    }
    values.update(overrides)
    return DiagnosticChannelPlan(**values)


def plan_with(**overrides: Any) -> DiagnosticPlan:
    """Rebuild the synthetic plan with keyword overrides applied."""
    plan = synthetic_plan()
    values: dict[str, Any] = {
        "identifier": plan.identifier,
        "binding": plan.binding,
        "clocks": plan.clocks,
        "frames": plan.frames,
        "clock_relations": plan.clock_relations,
        "frame_transformations": plan.frame_transformations,
        "clock_topology": plan.clock_topology,
        "channels": plan.channels,
        "deferrals": plan.deferrals,
    }
    values.update(overrides)
    return DiagnosticPlan(**values)


def signal_declaration(**overrides: Any) -> SignalDeclaration:
    """Build an auxiliary signal with keyword overrides applied."""
    values: dict[str, Any] = {
        "identifier": "sig_zz_extra",
        "quantity": "current",
        "unit": "A",
        "role": SignalRole.AUXILIARY,
        "description": "synthetic auxiliary signal",
    }
    values.update(overrides)
    return SignalDeclaration(**values)
