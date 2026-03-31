#!/usr/bin/env python3
"""
sim/system_weaver.py — System Weaving + First Principles Audit
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Clean rebuild of concepts from Inversion repo:
  - system_weaver.py (component types, constraint validation, weaving)
  - first_principles_audit.py (parameter spec, physical validation)

System weaving: take heterogeneous components (water, energy, data,
knowledge) and find configurations where they reinforce each other.
Same principle as ecological coupling in field_system.py.

First principles audit: every parameter must state its physical
meaning, units, source, and valid range. If it can't, it's not
a parameter — it's an assumption.

USAGE:
    python -m sim.system_weaver
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum


# =============================================================================
# COMPONENT TYPES
# =============================================================================

class ComponentType(Enum):
    WATER_SYSTEM = "water_system"
    ENERGY_SYSTEM = "energy_system"
    DATA_SYSTEM = "data_system"
    KNOWLEDGE_SYSTEM = "knowledge_system"
    FOOD_SYSTEM = "food_system"
    SUPPLY_CHAIN = "supply_chain"
    COMMUNICATION = "communication"
    SHELTER = "shelter"


@dataclass
class SystemComponent:
    """A component that can be woven into a larger system."""
    name: str
    component_type: ComponentType
    inputs: List[str]               # what it needs to function
    outputs: List[str]              # what it produces
    failure_modes: List[str]        # how it breaks
    dependencies: List[str]         # other components it depends on
    salvage_value: float = 0.5      # 0-1 recoverable on failure
    infrastructure_weight: float = 0.5  # 0=no infra, 1=heavy infra
    knowledge_requirement: str = "documented"  # documented / oral / embodied

    def resilience_score(self) -> float:
        """How resilient is this component? Lower deps + lower infra = higher."""
        dep_penalty = len(self.dependencies) * 0.1
        infra_penalty = self.infrastructure_weight * 0.3
        return max(0, 1.0 - dep_penalty - infra_penalty)


# =============================================================================
# CONSTRAINT — first principles validation
# =============================================================================

@dataclass
class PhysicalConstraint:
    """An invariant that must hold for the system to be valid."""
    name: str
    description: str
    check_fn_desc: str          # description of what the check does
    domain: str                 # which physical law
    violation_severity: str     # "fatal", "degraded", "warning"

    def check(self, system_state: Dict) -> Tuple[bool, str]:
        """Check if constraint holds. Override or use generic checks."""
        # Generic energy conservation check
        if self.domain == "energy_conservation":
            ein = system_state.get("energy_in", 0)
            eout = system_state.get("energy_out", 0)
            eloss = system_state.get("energy_loss", 0)
            balance = abs(ein - eout - eloss)
            ok = balance < ein * 0.01 if ein > 0 else True
            return ok, f"balance={balance:.3f}" if not ok else "OK"

        # Generic mass conservation
        if self.domain == "mass_conservation":
            min_val = system_state.get("mass_in", 0)
            mout = system_state.get("mass_out", 0)
            mloss = system_state.get("mass_loss", 0)
            balance = abs(min_val - mout - mloss)
            ok = balance < min_val * 0.01 if min_val > 0 else True
            return ok, f"balance={balance:.3f}" if not ok else "OK"

        # Generic: no negative resources
        if self.domain == "non_negative":
            for key, val in system_state.items():
                if isinstance(val, (int, float)) and val < 0:
                    return False, f"{key}={val} is negative"
            return True, "OK"

        return True, "no check defined"


CORE_CONSTRAINTS = [
    PhysicalConstraint("Energy conservation", "Energy in = energy out + losses",
                       "Sum inputs, compare to outputs + dissipation",
                       "energy_conservation", "fatal"),
    PhysicalConstraint("Mass conservation", "Mass in = mass out + waste",
                       "Sum material inputs vs outputs",
                       "mass_conservation", "fatal"),
    PhysicalConstraint("Non-negative resources", "No resource can go below zero",
                       "Check all resource levels >= 0",
                       "non_negative", "fatal"),
    PhysicalConstraint("Carrying capacity", "Population cannot exceed resource support",
                       "Population * per-capita need <= available supply",
                       "carrying_capacity", "degraded"),
    PhysicalConstraint("Knowledge transmission", "Loss rate must not exceed transmission rate indefinitely",
                       "Net knowledge decay leads to irrecoverable loss",
                       "knowledge_decay", "warning"),
]


# =============================================================================
# PARAMETER SPEC — forcing explicit documentation
# =============================================================================

@dataclass
class ParameterSpec:
    """
    Every parameter must state its physical meaning.
    If you can't fill these fields, it's not a parameter — it's an assumption.
    """
    name: str
    default_value: float
    units: str = ""
    physical_meaning: str = ""
    source: str = ""                # where this number comes from
    valid_range: Tuple[float, float] = (0.0, float('inf'))
    uncertainty_pct: float = 0.0    # how much we don't know

    def is_valid(self, value: float) -> bool:
        return self.valid_range[0] <= value <= self.valid_range[1]

    def audit(self) -> Dict[str, str]:
        """Audit this parameter. Flag missing documentation."""
        issues = []
        if not self.units:
            issues.append("no units specified")
        if not self.physical_meaning:
            issues.append("no physical meaning documented")
        if not self.source:
            issues.append("no source documented")
        if self.uncertainty_pct > 50:
            issues.append(f"high uncertainty ({self.uncertainty_pct}%)")
        return {
            "name": self.name,
            "status": "OK" if not issues else "AUDIT FAIL",
            "issues": issues,
        }


# =============================================================================
# SYSTEM WEAVER — find configurations where components reinforce
# =============================================================================

class SystemWeaver:
    """
    Weave heterogeneous components into reinforcing configurations.

    The weaver looks for:
    1. Output-to-input matches (one component's output feeds another's input)
    2. Shared dependencies (components that depend on the same thing)
    3. Complementary failure modes (if A fails, B covers)
    4. Coupling amplification (like ecological coupling in field_system.py)
    """

    def __init__(self):
        self.components: Dict[str, SystemComponent] = {}
        self.constraints: List[PhysicalConstraint] = list(CORE_CONSTRAINTS)

    def add(self, component: SystemComponent):
        self.components[component.name] = component

    def find_connections(self) -> List[Dict]:
        """Find output-to-input connections between components."""
        connections = []
        for name_a, comp_a in self.components.items():
            for name_b, comp_b in self.components.items():
                if name_a == name_b:
                    continue
                shared = set(comp_a.outputs) & set(comp_b.inputs)
                if shared:
                    connections.append({
                        "from": name_a, "to": name_b,
                        "shared": sorted(shared),
                        "type": "output_to_input",
                    })
        return connections

    def find_redundancies(self) -> List[Dict]:
        """Find components that can cover each other's failures."""
        redundancies = []
        for name_a, comp_a in self.components.items():
            for name_b, comp_b in self.components.items():
                if name_a >= name_b:
                    continue
                shared_outputs = set(comp_a.outputs) & set(comp_b.outputs)
                if shared_outputs:
                    redundancies.append({
                        "components": [name_a, name_b],
                        "shared_outputs": sorted(shared_outputs),
                        "type": "redundancy",
                    })
        return redundancies

    def coupling_score(self) -> float:
        """
        How coupled is this system? Higher = more reinforcement.
        Like ecological coupling coefficient k in field_system.py.
        """
        connections = self.find_connections()
        n = len(self.components)
        max_possible = n * (n - 1)
        if max_possible == 0:
            return 0.0
        return len(connections) / max_possible

    def system_resilience(self) -> float:
        """Average resilience across all components."""
        if not self.components:
            return 0.0
        return sum(c.resilience_score() for c in self.components.values()) / len(self.components)

    def weave_report(self) -> Dict:
        """Full analysis of the woven system."""
        connections = self.find_connections()
        redundancies = self.find_redundancies()

        # Dependency analysis
        all_deps = set()
        for c in self.components.values():
            all_deps.update(c.dependencies)
        unmet_deps = all_deps - set(self.components.keys())

        # Knowledge risk
        embodied = [c.name for c in self.components.values()
                    if c.knowledge_requirement == "embodied"]

        return {
            "components": len(self.components),
            "connections": len(connections),
            "redundancies": len(redundancies),
            "coupling_score": round(self.coupling_score(), 3),
            "system_resilience": round(self.system_resilience(), 3),
            "unmet_dependencies": sorted(unmet_deps),
            "embodied_knowledge_risk": embodied,
            "connection_details": connections,
            "redundancy_details": redundancies,
        }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  SYSTEM WEAVER + FIRST PRINCIPLES AUDIT")
    print("=" * 60)

    weaver = SystemWeaver()

    # Build a village-scale system
    weaver.add(SystemComponent(
        "well_water", ComponentType.WATER_SYSTEM,
        inputs=["electricity", "aquifer"],
        outputs=["drinking_water", "irrigation_water", "temperature_data"],
        failure_modes=["pump_failure", "aquifer_depletion", "contamination"],
        dependencies=["electricity"], salvage_value=0.7,
        infrastructure_weight=0.4, knowledge_requirement="oral",
    ))
    weaver.add(SystemComponent(
        "solar_panel", ComponentType.ENERGY_SYSTEM,
        inputs=["sunlight"],
        outputs=["electricity"],
        failure_modes=["panel_degradation", "inverter_failure", "weather"],
        dependencies=[], salvage_value=0.7,
        infrastructure_weight=0.3, knowledge_requirement="documented",
    ))
    weaver.add(SystemComponent(
        "geothermal_transducer", ComponentType.ENERGY_SYSTEM,
        inputs=["thermal_gradient", "seismic_vibration"],
        outputs=["electricity", "temperature_data", "pressure_data"],
        failure_modes=["crystal_fracture"],
        dependencies=[], salvage_value=0.8,
        infrastructure_weight=0.2, knowledge_requirement="documented",
    ))
    weaver.add(SystemComponent(
        "lora_mesh", ComponentType.COMMUNICATION,
        inputs=["electricity"],
        outputs=["data_relay", "coordination"],
        failure_modes=["node_failure", "interference"],
        dependencies=["electricity"], salvage_value=0.6,
        infrastructure_weight=0.2, knowledge_requirement="documented",
    ))
    weaver.add(SystemComponent(
        "food_garden", ComponentType.FOOD_SYSTEM,
        inputs=["irrigation_water", "sunlight", "soil_knowledge"],
        outputs=["food", "soil_health_data"],
        failure_modes=["drought", "pest", "soil_depletion"],
        dependencies=["irrigation_water"], salvage_value=0.3,
        infrastructure_weight=0.1, knowledge_requirement="embodied",
    ))
    weaver.add(SystemComponent(
        "elder_knowledge", ComponentType.KNOWLEDGE_SYSTEM,
        inputs=["apprenticeship_time", "community_trust"],
        outputs=["soil_knowledge", "water_management", "weather_prediction"],
        failure_modes=["death_of_holder", "community_fragmentation"],
        dependencies=[], salvage_value=0.0,
        infrastructure_weight=0.0, knowledge_requirement="embodied",
    ))

    report = weaver.weave_report()

    print(f"\n  SYSTEM: {report['components']} components")
    print(f"  Connections: {report['connections']} (coupling={report['coupling_score']})")
    print(f"  Redundancies: {report['redundancies']}")
    print(f"  Resilience: {report['system_resilience']}")

    print(f"\n  CONNECTIONS (output feeds input):")
    for c in report['connection_details']:
        print(f"    {c['from']} -> {c['to']}: {', '.join(c['shared'])}")

    print(f"\n  REDUNDANCIES (shared outputs):")
    for r in report['redundancy_details']:
        print(f"    {' + '.join(r['components'])}: {', '.join(r['shared_outputs'])}")

    if report['unmet_dependencies']:
        print(f"\n  UNMET DEPENDENCIES:")
        for d in report['unmet_dependencies']:
            print(f"    {d}")

    if report['embodied_knowledge_risk']:
        print(f"\n  EMBODIED KNOWLEDGE RISK (dies with holder):")
        for name in report['embodied_knowledge_risk']:
            print(f"    {name}")

    # Parameter audit
    print(f"\n  PARAMETER AUDIT:")
    test_params = [
        ParameterSpec("seebeck_pyrite", -820e-6, "V/K",
                      "Seebeck coefficient of natural pyrite",
                      "Published literature", (-1e-3, 0), 10),
        ParameterSpec("aquifer_recharge_rate", 0.05, "",
                      "", "", (0, 1), 60),
        ParameterSpec("knowledge_half_life", 15, "years",
                      "Time for half of embodied knowledge to be lost",
                      "Corridor observation (coupling.py)", (1, 100), 30),
    ]
    for p in test_params:
        audit = p.audit()
        status = audit['status']
        issues = "; ".join(audit['issues']) if audit['issues'] else "all fields documented"
        print(f"    {p.name:<30s} [{status}] {issues}")

    print(f"\n{'='*60}\n")
