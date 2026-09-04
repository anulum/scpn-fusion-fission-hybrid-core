# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — level-0 physics record

"""Level-0 physics record of one validated hybrid configuration.

The record evaluates the figures of merit of
:mod:`scpn_fusion_fission_hybrid_core.physics.figures_of_merit` on a
declared blanket, driver and fission-reactor pairing, and composes them
with the neutron source the configuration already carries.

Two multiplications appear in the record and they are not the same
quantity. The blanket **energy** multiplication is a declared input of
the figures of merit; the blanket **neutron** multiplication is
``1 / (1 - k_eff)``, which the configuration's own blanket computes.
Both are reported, side by side, and neither is derived from the other.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_fusion_fission_hybrid_core.configuration import DeviceConfiguration
from scpn_fusion_fission_hybrid_core.parameters import require_positive
from scpn_fusion_fission_hybrid_core.physics.figures_of_merit import (
    DT_FUSION_ENERGY_MEV,
    DT_NEUTRON_FRACTION,
    FISSION_ENERGY_MEV,
    hybrid_electrical_efficiency,
    offline_capacity_ratio,
    online_capacity_ratio,
    require_conversion_ratio,
    require_fraction,
    require_non_negative,
    supported_fission_reactors,
    thermal_power_ratio,
)

LEVEL0_SCHEMA: Final = "scpn.fusion-fission-hybrid-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of published hybrid figures of merit on a "
        "declared blanket, driver and fission-reactor pairing"
    ),
    (
        "every relation is a ratio of energies and efficiencies; no neutron "
        "transport, criticality, burnup or fuel-cycle calculation is performed"
    ),
    (
        "the blanket's fissile breeding rate and energy multiplication are "
        "declared inputs taken from a filed source's table, never computed here"
    ),
    (
        "the blanket's energy multiplication and its neutron multiplication "
        "are distinct quantities; neither is derived from the other"
    ),
    (
        "the supported-reactor number is a steady-state power ratio, not an "
        "integer, and carries no availability, outage or fuel-cycle-lag model"
    ),
    (
        "nothing here is a criticality-safety, nuclear-safety, licensing, "
        "safeguards or proliferation-resistance statement"
    ),
    (
        "no value describes or validates any real machine; an anchor reproduces "
        "a number the filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class HybridInputs:
    """Declared inputs the figures of merit are evaluated at.

    Parameters
    ----------
    breeding_rate
        Fissile breeding rate ``F`` of the blanket in atoms per source
        neutron; strictly positive.
    energy_multiplication
        Blanket energy multiplication ``M`` — energy deposited in the
        blanket per source neutron over the average source-neutron
        energy; strictly positive.
    engineering_q
        Engineering Q of the fusion driver, ``P_F / P_in``; strictly
        positive.
    conversion_ratio
        Conversion ratio ``C`` of the fission reactors burning the bred
        fuel, in ``[0, 1)``.
    capture_fission_ratio
        Capture-to-fission ratio ``alpha`` of those reactors; not
        negative.
    thermal_efficiency
        Thermal-to-electric conversion efficiency ``eta_H``, in
        ``(0, 1]``.
    neutron_fraction
        Fraction of the fusion power carried by neutrons, in ``(0, 1]``.
    fusion_energy_mev
        Energy released per fusion reaction; strictly positive.
    fission_energy_mev
        Energy released per fission; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any declared input leaves its documented interval. The inputs
        are validated here as well as inside each figure of merit, so a
        record can never be built from a set that the relations would
        have refused one at a time.
    """

    breeding_rate: float
    energy_multiplication: float
    engineering_q: float
    conversion_ratio: float
    capture_fission_ratio: float
    thermal_efficiency: float
    neutron_fraction: float = DT_NEUTRON_FRACTION
    fusion_energy_mev: float = DT_FUSION_ENERGY_MEV
    fission_energy_mev: float = FISSION_ENERGY_MEV

    def __post_init__(self) -> None:
        """Validate every declared input.

        Raises
        ------
        DeviceConfigurationError
            If any declared input leaves its documented interval.
        """
        require_positive("breeding_rate", self.breeding_rate)
        require_positive("energy_multiplication", self.energy_multiplication)
        require_positive("engineering_q", self.engineering_q)
        require_conversion_ratio("conversion_ratio", self.conversion_ratio)
        require_non_negative("capture_fission_ratio", self.capture_fission_ratio)
        require_fraction("thermal_efficiency", self.thermal_efficiency)
        require_fraction("neutron_fraction", self.neutron_fraction)
        require_positive("fusion_energy_mev", self.fusion_energy_mev)
        require_positive("fission_energy_mev", self.fission_energy_mev)


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """The composed operating point of one validated configuration.

    Parameters
    ----------
    fissile_production_per_s
        Fissile atoms bred per second: the declared breeding rate times
        the configuration's declared source rate.
    thermal_power_ratio
        Total hybrid thermal power over its fusion power.
    recirculating_power_fraction
        Share of that thermal power the driver consumes, ``(1/Q')``
        divided by the ratio above. It is what separates the hybrid's
        electrical efficiency from the plant's thermal efficiency.
    hybrid_electrical_efficiency
        Overall electrical efficiency; negative when the driver consumes
        more than the plant generates.
    offline_capacity_ratio
        Fission power the bred fuel supports over the fusion power.
    online_capacity_ratio
        The same for a hybrid that also generates electricity, which is
        smaller by the recirculating share.
    supported_fission_reactors
        Reactors one hybrid of equal thermal power supports at the
        declared ``Q'``.
    ultimate_supported_fission_reactors
        The ceiling that number approaches as ``Q'`` grows without bound,
        set by the blanket and the reactor pairing alone.
    supported_fraction_of_ultimate
        The first divided by the second: how close the declared ``Q'``
        brings the hybrid to its own ceiling.
    blanket_neutron_multiplication
        ``1 / (1 - k_eff)`` from the configuration's blanket. Reported
        beside the energy multiplication, and independent of it.
    """

    fissile_production_per_s: float
    thermal_power_ratio: float
    recirculating_power_fraction: float
    hybrid_electrical_efficiency: float
    offline_capacity_ratio: float
    online_capacity_ratio: float
    supported_fission_reactors: float
    ultimate_supported_fission_reactors: float
    supported_fraction_of_ultimate: float
    blanket_neutron_multiplication: float

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "fissile_production_per_s": self.fissile_production_per_s,
            "thermal_power_ratio": self.thermal_power_ratio,
            "recirculating_power_fraction": self.recirculating_power_fraction,
            "hybrid_electrical_efficiency": self.hybrid_electrical_efficiency,
            "offline_capacity_ratio": self.offline_capacity_ratio,
            "online_capacity_ratio": self.online_capacity_ratio,
            "supported_fission_reactors": self.supported_fission_reactors,
            "ultimate_supported_fission_reactors": (
                self.ultimate_supported_fission_reactors
            ),
            "supported_fraction_of_ultimate": self.supported_fraction_of_ultimate,
            "blanket_neutron_multiplication": self.blanket_neutron_multiplication,
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def level0_physics(
    configuration: DeviceConfiguration, inputs: HybridInputs
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated fusion-fission-hybrid configuration. It supplies the
        neutron source rate and the blanket's neutron multiplication.
    inputs
        Declared blanket, driver and fission-reactor pairing.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared input leaves its documented interval; the refusals
        name the field.
    """
    offline = offline_capacity_ratio(
        inputs.breeding_rate,
        inputs.conversion_ratio,
        inputs.capture_fission_ratio,
        inputs.fission_energy_mev,
        inputs.fusion_energy_mev,
    )
    ratio = thermal_power_ratio(
        inputs.engineering_q, inputs.neutron_fraction, inputs.energy_multiplication
    )
    supported = supported_fission_reactors(
        offline,
        inputs.engineering_q,
        inputs.neutron_fraction,
        inputs.energy_multiplication,
    )
    # The ceiling is the same ratio with the driver term removed, which is
    # what 1/Q' tends to as Q' grows without bound. Evaluating it that way
    # rather than at some large Q' keeps it exact.
    ultimate = offline / (
        1.0 + inputs.neutron_fraction * (inputs.energy_multiplication - 1.0)
    )
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        operating_point=OperatingPoint(
            fissile_production_per_s=(
                inputs.breeding_rate * configuration.source.source_rate_per_s
            ),
            thermal_power_ratio=ratio,
            recirculating_power_fraction=(1.0 / inputs.engineering_q) / ratio,
            hybrid_electrical_efficiency=hybrid_electrical_efficiency(
                inputs.thermal_efficiency,
                inputs.engineering_q,
                inputs.neutron_fraction,
                inputs.energy_multiplication,
            ),
            offline_capacity_ratio=offline,
            online_capacity_ratio=online_capacity_ratio(
                offline,
                inputs.thermal_efficiency,
                inputs.engineering_q,
                inputs.neutron_fraction,
                inputs.energy_multiplication,
            ),
            supported_fission_reactors=supported,
            ultimate_supported_fission_reactors=ultimate,
            supported_fraction_of_ultimate=supported / ultimate,
            blanket_neutron_multiplication=configuration.blanket.multiplication(),
        ),
    )
