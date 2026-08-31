# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — device capability package

"""Device capability models of the SCPN fusion-fission-hybrid family.

Public surface of the ``device_configuration_model`` and
``diagnostic_clock_semantics`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, canonical
serialisation with SHA-256 digests, and data-only pins to the SPO
registries. No claim about any real machine or diagnostic is made
anywhere in this package, and nothing here is a nuclear-safety,
criticality-safety, or licensing statement.
"""

from __future__ import annotations

from typing import Final

from scpn_fusion_fission_hybrid_core.configuration import (
    CRITICALITY_MARGIN_KEFF,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_fusion_fission_hybrid_core.errors import (
    DeviceConfigurationError,
    DiagnosticPlanError,
)
from scpn_fusion_fission_hybrid_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    ObservabilityBinding,
    ObservabilityClass,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_fusion_fission_hybrid_core.parameters import (
    FERTILE_CLASSES,
    NeutronSource,
    SubcriticalBlanket,
)
from scpn_fusion_fission_hybrid_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "CATALOGUE_BINDING",
    "CRITICALITY_MARGIN_KEFF",
    "FERTILE_CLASSES",
    "OWNED_CONFIGURATIONS",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "NeutronSource",
    "ObservabilityBinding",
    "ObservabilityClass",
    "PlanEnvelope",
    "RegistryBinding",
    "SemanticCarrier",
    "SubcriticalBlanket",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "plan_from_bytes",
    "plan_from_record",
    "verify_envelope",
]
