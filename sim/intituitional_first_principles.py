# “””
InstitutionalFirstPrinciples.py

Deconstructs institutions to thermodynamic bedrock.
Integrates:

- Four-part drill-down (Purpose / MVR / Thermo / Linkages)
- Operator skill vs equipment substitutability
- Infrastructure trust decay → human capital collapse
- Layer Zero activation model
- Latent node recovery constants (0.5–2yr baseline, pessimistic if trust threshold crossed)

Architecture:
Institution
├── purpose (irreducible)
├── mvr (minimum viable resources: mass, energy, operators)
├── physical_buffer (stored supply days — explicit, not magic)
├── substitutability (operator↑ vs equipment↑, inversely correlated)
├── infrastructure_trust_index (0.0–1.0, decays with environment)
├── operator_state (cognitive load decomposed)
└── layer_zero_interface (survival_window, node_status)
“””

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

# ── Constants ────────────────────────────────────────────────────────────────

TRUST_PHASE_TRANSITION = 0.35   # below this: chronic distrust, not fatigue
MENTORSHIP_DECAY_RATE  = 0.60   # skill transmission multiplier post-transition
RECOVERY_CONSTANT_BASE = 1.0    # years; optimistic (no trust collapse)
RECOVERY_CONSTANT_WARN = 3.5    # years; trust collapsed, pipeline poisoned

# ── Enums ─────────────────────────────────────────────────────────────────────

class SubstitutabilityProfile(Enum):
“””
Inversely correlated axes.
Rural:    operator HIGH, equipment LOW → failure mode: lose the person
Suburban: operator LOW, equipment HIGH → failure mode: lose the machine
“””
RURAL    = (“high_operator”, “low_equipment”)
SUBURBAN = (“low_operator”,  “high_equipment”)
HYBRID   = (“mid_operator”,  “mid_equipment”)

class NodeStatus(Enum):
ACTIVE         = “active”           # Layer Zero crew present, thermo engaged
FACADE         = “facade”           # building standing, crew absent
LATENT         = “latent”           # recoverable, no crew, buffer intact
COLLAPSED      = “collapsed”        # buffer gone, trust gone, pipeline poisoned

# ── Operator State ─────────────────────────────────────────────────────────────

@dataclass
class OperatorState:
“””
Cognitive load decomposed into recoverable vs structural components.
Standard burnout models only track total load — miss the trust variable.
“””
months_in_environment: float = 0.0

```
# Load components (0.0–1.0 each)
load_patient_care:              float = 0.5   # baseline — what they trained for
load_equipment_uncertainty:     float = 0.0   # is this reading accurate?
load_workaround_maintenance:    float = 0.0   # what's the backup mid-procedure?
load_infrastructure_monitoring: float = 0.0   # will the generator hold?

# Trust index: starts high, decays with infrastructure quality
infrastructure_trust_index: float = 1.0

@property
def total_load(self) -> float:
    return (
        self.load_patient_care
        + self.load_equipment_uncertainty
        + self.load_workaround_maintenance
        + self.load_infrastructure_monitoring
    )

@property
def load_is_recoverable(self) -> bool:
    """
    Hard cases → recoverable fatigue (sleep).
    Chronic environmental distrust → structural rewiring.
    Different failure modes.
    """
    return self.infrastructure_trust_index >= TRUST_PHASE_TRANSITION

@property
def skill_transmission_rate(self) -> float:
    """
    Post-transition: operators stop mentoring, actively discourage successors.
    This is where the 0.5–2yr recovery constant becomes optimistic.
    """
    if self.infrastructure_trust_index < TRUST_PHASE_TRANSITION:
        return MENTORSHIP_DECAY_RATE
    return 1.0

@property
def recruitment_advocacy(self) -> float:
    """Below threshold: net negative recruitment signal into pipeline."""
    if self.infrastructure_trust_index < TRUST_PHASE_TRANSITION:
        return 0.0
    return 1.0 - (self.total_load * 0.4)

def update(self, infra_quality: float, months_delta: float = 1.0):
    """
    infra_quality: 0.0 (failing) → 1.0 (maintained)
    Trust decays faster than it recovers — asymmetric.
    """
    decay_rate = (1.0 - infra_quality) * 0.08 * months_delta
    self.infrastructure_trust_index = max(0.0, self.infrastructure_trust_index - decay_rate)
    self.months_in_environment += months_delta

    # Hidden load grows as trust falls
    self.load_equipment_uncertainty     = 0.4 * (1.0 - self.infrastructure_trust_index)
    self.load_workaround_maintenance    = 0.3 * (1.0 - self.infrastructure_trust_index)
    self.load_infrastructure_monitoring = 0.2 * (1.0 - self.infrastructure_trust_index)

def report(self) -> Dict:
    return {
        "months_in_environment":        self.months_in_environment,
        "total_load":                   round(self.total_load, 3),
        "infrastructure_trust_index":   round(self.infrastructure_trust_index, 3),
        "load_recoverable":             self.load_is_recoverable,
        "skill_transmission_rate":      round(self.skill_transmission_rate, 3),
        "recruitment_advocacy":         round(self.recruitment_advocacy, 3),
    }
```

# ── Minimum Viable Resources ──────────────────────────────────────────────────

@dataclass
class MVR:
“””
Absolute floor. Mass, energy, humans. No luxuries.
physical_buffer: stored supply in days — explicit definition.
“””
mass_kg:          float = 0.0
energy_kwh:       float = 0.0
operators_needed: int   = 1
physical_buffer_days: float = 3.0   # days of supply on hand at baseline

# ── Institution ───────────────────────────────────────────────────────────────

@dataclass
class Institution:
“””
Thermodynamic substrate. Utility = f(Layer Zero humans activating it).
Without operators: heated tent burning fuel.
“””
name:    str
purpose: str                         # irreducible — what dies without it
mvr:     MVR
links:   List[str] = field(default_factory=list)   # cross-layer load paths

```
# Substitutability profile
profile: SubstitutabilityProfile = SubstitutabilityProfile.HYBRID

# Operator skill ceiling (how much skill covers equipment gaps)
operator_substitution_ceiling: float = 0.5
# Equipment ceiling (how much equipment covers skill gaps)
equipment_substitution_ceiling: float = 0.5
# Note: in practice these are inversely correlated
# Rural:    operator ~0.85, equipment ~0.15
# Suburban: operator ~0.15, equipment ~0.85

# Thermodynamic efficiency: useful_work / energy_in
# Bureaucratic entropy leak reduces this directly
thermo_efficiency: float = 0.25

# Infrastructure quality: 0.0 failing → 1.0 maintained
infrastructure_quality: float = 1.0

# Operator state tracker
operator_state: OperatorState = field(default_factory=OperatorState)

# ── Survival Window ───────────────────────────────────────────────────────

def survival_window_mod(self, layer_zero_crew_density: int) -> float:
    """
    Returns effective survival window multiplier.
    Crew present + thermo engaged → full buffer + efficiency bonus.
    Crew absent → facade mode, 10% of buffer (physical shell only).
    """
    buffer = self.mvr.physical_buffer_days

    if layer_zero_crew_density >= self.mvr.operators_needed:
        return buffer * (1.0 + self.thermo_efficiency)
    return buffer * 0.1   # facade mode

# ── Node Status ───────────────────────────────────────────────────────────

def node_status(self, layer_zero_crew_density: int) -> NodeStatus:
    trust = self.operator_state.infrastructure_trust_index
    buffer = self.mvr.physical_buffer_days

    if layer_zero_crew_density >= self.mvr.operators_needed:
        return NodeStatus.ACTIVE
    if buffer > 0 and trust >= TRUST_PHASE_TRANSITION:
        return NodeStatus.LATENT
    if buffer <= 0 or trust < TRUST_PHASE_TRANSITION:
        return NodeStatus.COLLAPSED
    return NodeStatus.FACADE

# ── Recovery Estimate ─────────────────────────────────────────────────────

def recovery_years(self) -> float:
    """
    Base: 0.5–2yr (latent node recovery).
    Trust collapse: 3.5yr+ — pipeline poisoned, next generation warned off.
    """
    trust = self.operator_state.infrastructure_trust_index
    if trust < TRUST_PHASE_TRANSITION:
        return RECOVERY_CONSTANT_WARN
    # Scale within 0.5–2.0 based on trust
    return 0.5 + (1.5 * (1.0 - trust))

# ── Tick ──────────────────────────────────────────────────────────────────

def tick(self, months: float = 1.0):
    """Advance time. Infrastructure quality drives operator trust decay."""
    self.operator_state.update(self.infrastructure_quality, months)

# ── Thermo Map ────────────────────────────────────────────────────────────

def thermo_report(self, layer_zero_crew_density: int) -> Dict:
    status = self.node_status(layer_zero_crew_density)
    return {
        "institution":          self.name,
        "purpose":              self.purpose,
        "mvr": {
            "mass_kg":              self.mvr.mass_kg,
            "energy_kwh":           self.mvr.energy_kwh,
            "operators_needed":     self.mvr.operators_needed,
            "physical_buffer_days": self.mvr.physical_buffer_days,
        },
        "substitutability": {
            "profile":              self.profile.name,
            "operator_ceiling":     self.operator_substitution_ceiling,
            "equipment_ceiling":    self.equipment_substitution_ceiling,
            "failure_mode":         (
                "lose the person"  if self.profile == SubstitutabilityProfile.RURAL
                else "lose the machine"
            ),
        },
        "thermo": {
            "efficiency":           self.thermo_efficiency,
            "infrastructure_quality": self.infrastructure_quality,
            "survival_window_days": round(self.survival_window_mod(layer_zero_crew_density), 2),
        },
        "operator":             self.operator_state.report(),
        "node_status":          status.value,
        "recovery_years":       round(self.recovery_years(), 2),
        "cross_layer_links":    self.links,
    }
```

# ── Preset Archetypes ─────────────────────────────────────────────────────────

def rural_clinic(infrastructure_quality: float = 0.5) -> Institution:
inst = Institution(
name    = “Rural Clinic”,
purpose = “wound closure / acute stabilization”,
mvr     = MVR(mass_kg=500, energy_kwh=20, operators_needed=2, physical_buffer_days=7),
links   = [“Water”, “Repair”, “Food”],
profile = SubstitutabilityProfile.RURAL,
operator_substitution_ceiling = 0.85,
equipment_substitution_ceiling = 0.15,
thermo_efficiency = 0.30,          # lower bureaucratic leak than suburban
infrastructure_quality = infrastructure_quality,
)
return inst

def suburban_hospital() -> Institution:
inst = Institution(
name    = “Suburban Hospital”,
purpose = “wound closure / acute stabilization”,
mvr     = MVR(mass_kg=5000, energy_kwh=500, operators_needed=20, physical_buffer_days=14),
links   = [“Water”, “Power”, “Repair”, “Food”, “Logistics”],
profile = SubstitutabilityProfile.SUBURBAN,
operator_substitution_ceiling = 0.15,
equipment_substitution_ceiling = 0.85,
thermo_efficiency = 0.18,          # higher bureaucratic entropy leak
infrastructure_quality = 0.90,
)
return inst

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:
import json

```
print("=== RURAL CLINIC — degraded infrastructure (quality=0.4) ===\n")
rc = rural_clinic(infrastructure_quality=0.4)

# Simulate 18 months in degraded environment
for _ in range(18):
    rc.tick(months=1.0)

print(json.dumps(rc.thermo_report(layer_zero_crew_density=2), indent=2))

print("\n=== SUBURBAN HOSPITAL — maintained infrastructure ===\n")
sh = suburban_hospital()
for _ in range(18):
    sh.tick(months=1.0)

print(json.dumps(sh.thermo_report(layer_zero_crew_density=20), indent=2))

print("\n=== RURAL CLINIC — crew lost (facade mode) ===\n")
rc2 = rural_clinic(infrastructure_quality=0.4)
for _ in range(24):
    rc2.tick(months=1.0)

print(json.dumps(rc2.thermo_report(layer_zero_crew_density=0), indent=2))
print(f"\nRecovery estimate: {rc2.recovery_years():.1f} years")
print(f"Trust threshold crossed: {not rc2.operator_state.load_is_recoverable}")
```
