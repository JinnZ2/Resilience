# MODULE: sim/survival_engineering.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: domain
# Shuttle/submarine criticality tiers (T1-T4) applied to institutions
# “””
survival_engineering.py

Capstone module. Shuttle/submarine criticality standards
applied to institutions, governance, economic functions,
and social structures.

The core inversion:
Standard governance asks: “What does this institution do?”
Survival engineering asks: “What fails, in what order,
how fast, with what warning,
and what backs it up?”

Shuttle standard:
Every system has a criticality tier.
Failure modes documented before deployment.
Redundancy specified, not assumed.
No component exists without survival justification.
Instrument reports to physics, not to institution.

Submarine standard:
Pressure hull integrity: non-negotiable.
Atmosphere regeneration: non-negotiable.
Everything else: tradeable against those two.
CO2 scrubber doesn’t self-report. CO2 is measured.

Applied to community:
Tier 1 (pressure hull):  failure = death within hours
Tier 2 (life support):   failure = death within weeks
Tier 3 (mission):        failure = capability loss, recovery possible
Tier 4 (comfort):        everything standard models prioritize

Current allocation: Tier 4 captures most resources.
Tier 1 runs on what’s left.
This module measures that inversion and specifies the correction.

Chain position (capstone — imports all prior modules):
city_thermodynamics     →  physical floors, operator trust
city_optimization       →  upgrade test, leakage
purpose_deviation       →  drift register
datacenter_net_zero     →  extraction test
institution_registry    →  unified scoring
thermodynamic_impact    →  policy instrument
survival_engineering    →  THIS FILE — criticality audit
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json

# ── Sibling imports ───────────────────────────────────────────────────────────

try:
from thermodynamic_impact import (
ThermodynamicModel, PolicyThreshold, InstitutionClass,
CLASS_FAILURE_RATES, NET_PURPOSE_GAIN_THRESHOLD,
comparison_dc_parasite, comparison_dc_net_zero,
)
from institution_registry import (
InstitutionRegistry, dc_to_purpose_deviation,
build_madison_suburb_registry,
)
from purpose_deviation import (
PurposeDeviation, DriftLevel,
austin_megachurch, suburban_school_captured,
rural_fire_hall_on_purpose,
)
from city_thermodynamics import (
build_city_1000, NodeStatus,
)
_SIBLINGS = True
except ImportError:
_SIBLINGS = False

# ── Criticality Tiers ─────────────────────────────────────────────────────────

class CriticalityTier(Enum):
“””
Shuttle/submarine failure consequence classification.
Not severity of the problem — severity of the consequence.
“””
T1_PRESSURE_HULL  = 1   # failure = death within hours, no recovery
T2_LIFE_SUPPORT   = 2   # failure = death within weeks, recovery if caught
T3_MISSION        = 3   # failure = capability loss, community survives
T4_COMFORT        = 4   # everything standard models count as “value”

TIER_LABELS = {
CriticalityTier.T1_PRESSURE_HULL: “PRESSURE HULL  — hours to death”,
CriticalityTier.T2_LIFE_SUPPORT:  “LIFE SUPPORT   — weeks to death”,
CriticalityTier.T3_MISSION:       “MISSION CAP    — capability loss”,
CriticalityTier.T4_COMFORT:       “COMFORT        — non-critical”,
}

# Recovery windows (hours before failure becomes unrecoverable)

RECOVERY_WINDOW_HOURS = {
CriticalityTier.T1_PRESSURE_HULL: 4,
CriticalityTier.T2_LIFE_SUPPORT:  72,
CriticalityTier.T3_MISSION:       720,    # 30 days
CriticalityTier.T4_COMFORT:       8760,   # 1 year
}

# ── Failure Mode ──────────────────────────────────────────────────────────────

@dataclass
class FailureMode:
“””
Documents what breaks, when, and what it takes down.
Shuttle standard: every failure mode documented before deployment.
Current governance standard: failure modes discovered post-collapse.
“””
component:          str
trigger:            str           # what causes failure
time_to_failure:    float         # hours from trigger to failure
cascade_t1h:        List[str]     # what fails in first hour
cascade_t24h:       List[str]     # what fails in first day
cascade_t72h:       List[str]     # what fails in 72 hours (water critical)
cascade_t30d:       List[str]     # 30-day horizon
point_of_no_return: float         # hours — after this, outside intervention required
detection_method:   str           # how failure is detected (instrument vs self-report)
is_self_reporting:  bool = True   # TRUE = dangerous, FALSE = instrument-verified

```
@property
def detection_quality(self) -> str:
    if self.is_self_reporting:
        return "UNSAFE — institution self-reports (CO2 scrubber problem)"
    return "SAFE — physical instrument, independent verification"
```

# ── Redundancy Specification ──────────────────────────────────────────────────

@dataclass
class RedundancySpec:
“””
Shuttle standard: primary + backup + backup-to-backup for Tier 1.
Submarine standard: no single point of failure on life support.
Current standard: cost optimization eliminates redundancy.
“””
system_name:          str
tier:                 CriticalityTier
primary:              str
backup:               Optional[str]   = None
backup_to_backup:     Optional[str]   = None
switchover_time_hrs:  float           = 0.0
backup_duration_hrs:  float           = 0.0   # how long backup sustains

```
@property
def meets_shuttle_standard(self) -> bool:
    if self.tier == CriticalityTier.T1_PRESSURE_HULL:
        return (self.backup is not None
                and self.backup_to_backup is not None
                and self.switchover_time_hrs < 1.0
                and self.backup_duration_hrs >= 72.0)
    if self.tier == CriticalityTier.T2_LIFE_SUPPORT:
        return (self.backup is not None
                and self.switchover_time_hrs < 4.0
                and self.backup_duration_hrs >= 168.0)
    return self.backup is not None

@property
def gap(self) -> str:
    if self.meets_shuttle_standard:
        return "COMPLIANT"
    missing = []
    if self.backup is None:
        missing.append("no backup defined")
    if self.tier == CriticalityTier.T1_PRESSURE_HULL:
        if self.backup_to_backup is None:
            missing.append("no backup-to-backup")
        if self.switchover_time_hrs >= 1.0:
            missing.append(f"switchover {self.switchover_time_hrs}h (need <1h)")
        if self.backup_duration_hrs < 72.0:
            missing.append(f"backup duration {self.backup_duration_hrs}h (need 72h)")
    return "NON-COMPLIANT: " + "; ".join(missing)
```

# ── Survival Critical System ──────────────────────────────────────────────────

@dataclass
class SurvivalCriticalSystem:
“””
One system in the community survival architecture.
Tier + failure modes + redundancy + current vs required state.
The instrument that governance has never built.
“””
name:               str
tier:               CriticalityTier
physics_function:   str           # irreducible — what dies without it
current_state:      str           # observable physical state
floor_kwh_day:      float         # from city_thermodynamics
actual_kwh_day:     float
operators_needed:   int
operators_present:  int
failure_modes:      List[FailureMode]    = field(default_factory=list)
redundancy:         List[RedundancySpec] = field(default_factory=list)
purpose_deviation_index: float           = 0.0   # from purpose_deviation
mortality_pathway:  Optional[str]        = None  # explicit if T1/T2

```
@property
def recovery_window_hours(self) -> float:
    return RECOVERY_WINDOW_HOURS[self.tier]

@property
def operator_gap(self) -> int:
    return max(0, self.operators_needed - self.operators_present)

@property
def energy_ratio(self) -> float:
    if self.floor_kwh_day == 0:
        return float("inf") if self.actual_kwh_day > 0 else 1.0
    return self.actual_kwh_day / self.floor_kwh_day

@property
def redundancy_compliant(self) -> bool:
    if not self.redundancy:
        return self.tier in (CriticalityTier.T3_MISSION,
                             CriticalityTier.T4_COMFORT)
    return all(r.meets_shuttle_standard for r in self.redundancy)

@property
def self_reporting_count(self) -> int:
    return sum(1 for fm in self.failure_modes if fm.is_self_reporting)

def criticality_report(self) -> Dict:
    return {
        "system":             self.name,
        "tier":               TIER_LABELS[self.tier],
        "physics_function":   self.physics_function,
        "current_state":      self.current_state,
        "recovery_window_hrs": self.recovery_window_hours,
        "mortality_pathway":  self.mortality_pathway,
        "operator_status": {
            "needed":    self.operators_needed,
            "present":   self.operators_present,
            "gap":       self.operator_gap,
            "risk":      "CRITICAL" if self.operator_gap > 0
                         and self.tier.value <= 2 else "OK",
        },
        "energy": {
            "floor_kwh_day":  self.floor_kwh_day,
            "actual_kwh_day": self.actual_kwh_day,
            "ratio":          round(self.energy_ratio, 1)
                              if self.energy_ratio != float("inf") else "∞",
        },
        "redundancy_compliant": self.redundancy_compliant,
        "redundancy_gaps": [
            {"system": r.system_name, "gap": r.gap}
            for r in self.redundancy if not r.meets_shuttle_standard
        ],
        "detection_unsafe_count": self.self_reporting_count,
        "purpose_deviation_index": round(self.purpose_deviation_index, 1),
        "failure_cascade": {
            fm.component: {
                "trigger":        fm.trigger,
                "T+1h":           fm.cascade_t1h,
                "T+24h":          fm.cascade_t24h,
                "T+72h":          fm.cascade_t72h,
                "point_no_return": f"{fm.point_of_no_return}h",
                "detection":      fm.detection_quality,
            }
            for fm in self.failure_modes
        },
    }
```

# ── Community Survival Spec ───────────────────────────────────────────────────

@dataclass
class CommunitySurvivalSpec:
“””
Minimum viable survival specification for a community.
Analog: submarine emergency checklist.

```
Purpose: verify Tier 1 and Tier 2 systems are functional
         before any Tier 4 spending is authorized.

Authority: Layer Zero operators, not administrators.
Override:  any Tier 1 failure suspends all Tier 4 spending.
Verification: physical instrument only — no self-reporting.
"""
community_name: str
population:     int
systems:        List[SurvivalCriticalSystem] = field(default_factory=list)

def add(self, system: SurvivalCriticalSystem):
    self.systems.append(system)

def tier_1_systems(self) -> List[SurvivalCriticalSystem]:
    return [s for s in self.systems
            if s.tier == CriticalityTier.T1_PRESSURE_HULL]

def tier_2_systems(self) -> List[SurvivalCriticalSystem]:
    return [s for s in self.systems
            if s.tier == CriticalityTier.T2_LIFE_SUPPORT]

def critical_failures(self) -> List[SurvivalCriticalSystem]:
    """Tier 1/2 systems with operator gaps or redundancy failures."""
    return [
        s for s in self.systems
        if s.tier.value <= 2
        and (s.operator_gap > 0 or not s.redundancy_compliant)
    ]

def self_reporting_violations(self) -> List[Tuple[str, int]]:
    """Systems where failure detection relies on self-reporting."""
    return [
        (s.name, s.self_reporting_count)
        for s in self.systems
        if s.tier.value <= 2 and s.self_reporting_count > 0
    ]

def tier4_budget_at_risk(self, total_budget: float) -> float:
    """
    Budget that should be suspended pending Tier 1/2 compliance.
    Submarine rule: fix the hull before painting the mess hall.
    """
    critical_gap_count = len(self.critical_failures())
    if critical_gap_count == 0:
        return 0.0
    # Each critical gap suspends proportional Tier 4 allocation
    return total_budget * min(1.0, critical_gap_count * 0.15)

def survival_checklist(self) -> Dict:
    """
    The instrument that governance has never built.
    Run before budget allocation, not after crisis.
    """
    t1_ok = all(
        s.operator_gap == 0 and s.redundancy_compliant
        for s in self.tier_1_systems()
    )
    t2_ok = all(
        s.operator_gap == 0
        for s in self.tier_2_systems()
    )
    self_report_violations = self.self_reporting_violations()

    return {
        "community":          self.community_name,
        "population":         self.population,
        "TIER_1_SECURE":      t1_ok,
        "TIER_2_SECURE":      t2_ok,
        "PROCEED_TO_TIER4":   t1_ok and t2_ok,
        "critical_failures":  [s.name for s in self.critical_failures()],
        "self_report_violations": self_report_violations,
        "mortality_pathways_active": [
            s.mortality_pathway for s in self.systems
            if s.mortality_pathway and s.operator_gap > 0
        ],
        "shuttle_standard_note": (
            "No Tier 1 system may be underfunded while Tier 4 spending continues. "
            "Instrument verification required. Self-reporting not accepted."
        ),
    }

def deviation_from_shuttle_standard(self) -> Dict:
    """
    What is currently built vs what shuttle standard requires.
    The gap is the measurement of institutional capture.
    """
    required = {}
    actual   = {}
    gaps     = {}

    for s in self.systems:
        tier_label = s.tier.name
        if tier_label not in required:
            required[tier_label] = []
            actual[tier_label]   = []
            gaps[tier_label]     = []

        req = {
            "system":         s.name,
            "redundancy":     "PRIMARY + BACKUP + B2B" if s.tier.value == 1
                              else "PRIMARY + BACKUP",
            "detection":      "INSTRUMENT — physical signal, independent",
            "operator_floor": s.operators_needed,
            "energy_floor":   s.floor_kwh_day,
        }
        act = {
            "system":         s.name,
            "redundancy":     "COMPLIANT" if s.redundancy_compliant
                              else "NON-COMPLIANT",
            "detection":      f"{s.self_reporting_count} self-reporting failure modes",
            "operators_present": s.operators_present,
            "energy_actual":  s.actual_kwh_day,
        }
        gap = {
            "system":         s.name,
            "redundancy_gap": not s.redundancy_compliant,
            "detection_gap":  s.self_reporting_count > 0,
            "operator_gap":   s.operator_gap,
            "energy_inversion": round(s.energy_ratio, 1)
                                if s.energy_ratio != float("inf") else "∞",
        }
        required[tier_label].append(req)
        actual[tier_label].append(act)
        gaps[tier_label].append(gap)

    return {
        "required_shuttle_standard": required,
        "actual_current_state":      actual,
        "gaps":                      gaps,
    }

def full_report(self) -> Dict:
    return {
        "survival_checklist":         self.survival_checklist(),
        "system_reports":             [s.criticality_report()
                                       for s in self.systems],
        "deviation_from_standard":    self.deviation_from_shuttle_standard(),
    }
```

# ── Preset: Madison Suburb Survival Spec ──────────────────────────────────────

def build_madison_survival_spec() -> CommunitySurvivalSpec:
spec = CommunitySurvivalSpec(
community_name = “Madison Suburb”,
population     = 160_000,
)

```
# ── T1: Water ─────────────────────────────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Municipal Water",
    tier             = CriticalityTier.T1_PRESSURE_HULL,
    physics_function = "H2O mass transfer aquifer → body (3-day survival limit)",
    current_state    = "SCADA-controlled, single grid dependency",
    floor_kwh_day    = 20,
    actual_kwh_day   = 500,
    operators_needed = 3,
    operators_present= 3,
    purpose_deviation_index = 52.0,
    mortality_pathway = (
        "Grid brownout → pump failure → no water T+3h → "
        "dialysis failure T+6h → hospital sterilization failure T+12h → "
        "nursing home dehydration T+48h"
    ),
    failure_modes = [
        FailureMode(
            component         = "SCADA control system",
            trigger           = "grid voltage sag >5%",
            time_to_failure   = 0.1,
            cascade_t1h       = ["pump shutoff", "pressure loss"],
            cascade_t24h      = ["hospital water failure", "fire suppression offline"],
            cascade_t72h      = ["dehydration casualties begin",
                                 "sanitation failure"],
            cascade_t30d      = ["waterborne disease", "population displacement"],
            point_of_no_return= 72.0,
            detection_method  = "SCADA self-reports to utility (NOT independent)",
            is_self_reporting = True,
        ),
    ],
    redundancy = [
        RedundancySpec(
            system_name      = "Municipal Water Primary",
            tier             = CriticalityTier.T1_PRESSURE_HULL,
            primary          = "Electric pumps, SCADA",
            backup           = "Diesel generator backup (present)",
            backup_to_backup = None,   # MISSING
            switchover_time_hrs = 0.5,
            backup_duration_hrs = 48,  # INSUFFICIENT (need 72)
        ),
    ],
))

# ── T1: Sewer ─────────────────────────────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Sanitation / Sewer",
    tier             = CriticalityTier.T1_PRESSURE_HULL,
    physics_function = "Pathogen export — prevents cholera/typhoid cascade",
    current_state    = "Lift stations grid-dependent",
    floor_kwh_day    = 0,
    actual_kwh_day   = 200,
    operators_needed = 2,
    operators_present= 2,
    purpose_deviation_index = 0.0,   # gravity floor = 0
    mortality_pathway = (
        "Lift station failure → sewage backup T+4h → "
        "ground contamination T+24h → water supply contamination T+72h → "
        "cholera/typhoid outbreak T+14d"
    ),
    failure_modes = [
        FailureMode(
            component         = "Lift stations",
            trigger           = "grid outage >2h",
            time_to_failure   = 2.0,
            cascade_t1h       = ["sewage backup in low areas"],
            cascade_t24h      = ["ground saturation", "odor/disease vector"],
            cascade_t72h      = ["aquifer contamination risk"],
            cascade_t30d      = ["epidemic potential"],
            point_of_no_return= 168.0,
            detection_method  = "Float sensors — independent physical signal",
            is_self_reporting = False,
        ),
    ],
    redundancy = [
        RedundancySpec(
            system_name      = "Sewer Lift Stations",
            tier             = CriticalityTier.T1_PRESSURE_HULL,
            primary          = "Grid power",
            backup           = "Portable generators (staged)",
            backup_to_backup = "Gravity bypass valves (partial coverage)",
            switchover_time_hrs = 2.0,   # SLOW for T1
            backup_duration_hrs = 72.0,
        ),
    ],
))

# ── T1: Trauma Response ───────────────────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Trauma Response",
    tier             = CriticalityTier.T1_PRESSURE_HULL,
    physics_function = "Mechanical force on tissue → hemorrhage stopped "
                       "(minutes to irreversible)",
    current_state    = "Centralized ER, EMS grid-dependent dispatch",
    floor_kwh_day    = 20,
    actual_kwh_day   = 2_800,
    operators_needed = 8,
    operators_present= 6,   # understaffed
    purpose_deviation_index = 515.0,
    mortality_pathway = (
        "EMS dispatch failure → response time +8min → "
        "hemorrhage irreversible at T+6min → "
        "cardiac arrest survival rate halves per 10min delay"
    ),
    failure_modes = [
        FailureMode(
            component         = "EMS dispatch (centralized)",
            trigger           = "grid/comms failure",
            time_to_failure   = 0.05,
            cascade_t1h       = ["no ambulance routing", "delayed trauma response"],
            cascade_t24h      = ["preventable deaths accumulate"],
            cascade_t72h      = ["surgical backlog", "infection from untreated wounds"],
            cascade_t30d      = ["chronic condition decompensation"],
            point_of_no_return= 0.1,   # minutes for hemorrhage
            detection_method  = "CAD system self-reports (NOT independent)",
            is_self_reporting = True,
        ),
    ],
    redundancy = [
        RedundancySpec(
            system_name      = "EMS Dispatch",
            tier             = CriticalityTier.T1_PRESSURE_HULL,
            primary          = "CAD dispatch center",
            backup           = "Manual dispatch protocol (exists on paper)",
            backup_to_backup = None,   # MISSING
            switchover_time_hrs = 1.0,
            backup_duration_hrs = 24.0,  # INSUFFICIENT
        ),
    ],
))

# ── T2: Thermal Regulation ────────────────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Thermal Regulation (heating)",
    tier             = CriticalityTier.T2_LIFE_SUPPORT,
    physics_function = "Body temp maintenance — hypothermia at <10°C ambient "
                       "(Upper Midwest: -30°C possible)",
    current_state    = "Natural gas primary, grid-dependent controls",
    floor_kwh_day    = 50,
    actual_kwh_day   = 3_000,
    operators_needed = 4,
    operators_present= 4,
    purpose_deviation_index = 28.0,
    mortality_pathway = (
        "Gas supply interruption in January → "
        "indoor temp -10°C within 6h → "
        "hypothermia vulnerable populations T+12h → "
        "nursing home/infant deaths T+24h"
    ),
    failure_modes = [
        FailureMode(
            component         = "Natural gas supply",
            trigger           = "pipeline pressure loss OR grid failure "
                                "(electronic ignition)",
            time_to_failure   = 6.0,
            cascade_t1h       = ["boiler shutoff", "temp drop begins"],
            cascade_t24h      = ["vulnerable population at risk"],
            cascade_t72h      = ["pipe freeze cascade", "water system failure"],
            cascade_t30d      = ["structural damage from freeze"],
            point_of_no_return= 48.0,
            detection_method  = "Thermostat / gas pressure gauge — physical",
            is_self_reporting = False,
        ),
    ],
    redundancy = [
        RedundancySpec(
            system_name      = "Building Heat",
            tier             = CriticalityTier.T2_LIFE_SUPPORT,
            primary          = "Natural gas boiler",
            backup           = "Electric resistance (grid-dependent — fails same event)",
            backup_to_backup = None,
            switchover_time_hrs = 0.0,
            backup_duration_hrs = 0.0,   # CRITICAL: backup fails with primary
        ),
    ],
))

# ── T2: Medication Cold Chain ─────────────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Medication Cold Chain",
    tier             = CriticalityTier.T2_LIFE_SUPPORT,
    physics_function = "Refrigeration maintains drug efficacy "
                       "(insulin, biologics, vaccines)",
    current_state    = "Grid-dependent, no community-level backup",
    floor_kwh_day    = 5,
    actual_kwh_day   = 80,
    operators_needed = 2,
    operators_present= 2,
    purpose_deviation_index = 12.0,
    mortality_pathway = (
        "Grid brownout >4h → insulin degrades → "
        "diabetic crisis T+24h → "
        "immunocompromised decompensation T+48h"
    ),
    failure_modes = [
        FailureMode(
            component         = "Pharmacy/hospital refrigeration",
            trigger           = "grid voltage sag from DC/megachurch load spike",
            time_to_failure   = 4.0,
            cascade_t1h       = ["temp excursion begins", "no alarm in most pharmacies"],
            cascade_t24h      = ["insulin potency loss"],
            cascade_t72h      = ["diabetic emergencies"],
            cascade_t30d      = ["supply chain depletion"],
            point_of_no_return= 24.0,
            detection_method  = "Temperature logger — physical BUT "
                                "rarely monitored continuously",
            is_self_reporting = True,   # monitoring is intermittent
        ),
    ],
    redundancy = [
        RedundancySpec(
            system_name      = "Medication Refrigeration",
            tier             = CriticalityTier.T2_LIFE_SUPPORT,
            primary          = "Grid power to pharmacy",
            backup           = None,   # MISSING in most pharmacies
            backup_to_backup = None,
            switchover_time_hrs = 0.0,
            backup_duration_hrs = 0.0,
        ),
    ],
))

# ── T3: Skill Transmission ────────────────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Skill Transmission (schools)",
    tier             = CriticalityTier.T3_MISSION,
    physics_function = "Info patterns to child brains — "
                       "next generation operator capability",
    current_state    = "Credential mill, 280x energy floor, "
                       "teacher retention crisis",
    floor_kwh_day    = 10,
    actual_kwh_day   = 2_800,
    operators_needed = 50,
    operators_present= 38,   # ~24% vacancy rate
    purpose_deviation_index = 515.4,
    mortality_pathway = None,   # T3 — delayed, not immediate
    failure_modes = [
        FailureMode(
            component         = "Teacher pipeline",
            trigger           = "infrastructure trust < 0.35 "
                                "(from institutional_first_principles)",
            time_to_failure   = 8760.0,  # 1 year to measurable output loss
            cascade_t1h       = [],
            cascade_t24h      = [],
            cascade_t72h      = [],
            cascade_t30d      = ["substitute teacher saturation"],
            point_of_no_return= 26280.0,  # 3 years (trust collapse recovery)
            detection_method  = "Retention rate — public record",
            is_self_reporting = False,
        ),
    ],
    redundancy = [
        RedundancySpec(
            system_name      = "Skill Transmission",
            tier             = CriticalityTier.T3_MISSION,
            primary          = "Formal school system",
            backup           = "Community apprenticeship (atrophied)",
            backup_to_backup = None,
            switchover_time_hrs = 8760.0,
            backup_duration_hrs = 43800.0,
        ),
    ],
))

# ── T4: Data Center (parasite config) ─────────────────────────────────────
spec.add(SurvivalCriticalSystem(
    name             = "Data Center — Ad Network",
    tier             = CriticalityTier.T4_COMFORT,
    physics_function = "NONE at community level — "
                       "serves external economic actors",
    current_state    = "15MW draw, ERF=0, compute exits community",
    floor_kwh_day    = 0,    # zero community floor — not needed for survival
    actual_kwh_day   = 360_000,  # 15MW × 24h
    operators_needed = 10,
    operators_present= 547,  # overoperates at T4 while T1 is understaffed
    purpose_deviation_index = 603.2,
    mortality_pathway = (
        "INDIRECT: grid load spike → T1 water pump brownout → "
        "medication cold chain failure → nursing home deaths. "
        "Not attributed to DC in any current model."
    ),
    failure_modes = [],
    redundancy     = [],
))

return spec
```

# ── What Can Be Built ─────────────────────────────────────────────────────────

@dataclass
class ShuttleStandardSpec:
“””
Specification for what must be built to meet survival engineering standard.
Not comprehensive plan — minimum viable survival architecture.
Analog: submarine emergency equipment list.
“””
community_name: str
population:     int

```
REQUIRED_T1 = [
    {
        "system":       "Water — gravity backup",
        "specification":"Elevated reservoir OR gravity-fed tank, "
                        "72h supply at floor consumption, "
                        "independent of grid",
        "floor_kwh":    0,
        "cost_anchor":  "gravity well: $25k–$80k each",
        "quantity":     "1 per 500 people minimum",
    },
    {
        "system":       "Sewer — gravity bypass",
        "specification":"Gravity bypass valves at all lift stations, "
                        "allows flow without power, "
                        "partial coverage acceptable",
        "floor_kwh":    0,
        "cost_anchor":  "$5k–$15k per lift station",
        "quantity":     "100% of lift stations",
    },
    {
        "system":       "Trauma — distributed first response",
        "specification":"Trained first responders within 4-min walk "
                        "of any point in community, "
                        "no grid dependency for initial response",
        "floor_kwh":    0,
        "cost_anchor":  "training: $2k/person",
        "quantity":     "1 per 200 people",
    },
    {
        "system":       "Communications — non-grid",
        "specification":"CB/LoRa mesh/HAM network covering full geography, "
                        "battery-powered, independent of cellular",
        "floor_kwh":    0.5,
        "cost_anchor":  "$200–$500 per node",
        "quantity":     "1 node per km² minimum",
    },
]

REQUIRED_T2 = [
    {
        "system":       "Thermal — passive backup",
        "specification":"Community warming centers, wood/propane capable, "
                        "72h thermal buffer without grid, "
                        "within 1km of all residents",
        "floor_kwh":    5,
        "cost_anchor":  "$50k–$200k per center",
        "quantity":     "1 per 2,000 people",
    },
    {
        "system":       "Medication cold chain",
        "specification":"Insulated cold storage + 72h battery backup "
                        "at every pharmacy and clinic, "
                        "continuous temperature logging with independent alarm",
        "floor_kwh":    2,
        "cost_anchor":  "$5k–$15k per facility",
        "quantity":     "100% of medication storage facilities",
    },
    {
        "system":       "Food buffer",
        "specification":"72h caloric supply accessible without vehicles "
                        "or grid, distributed not centralized",
        "floor_kwh":    0,
        "cost_anchor":  "$50/person buffer stock",
        "quantity":     "community-distributed, not warehouse",
    },
]

VERIFICATION_STANDARD = {
    "method":      "physical instrument — no self-reporting",
    "frequency":   "continuous T1, weekly T2, monthly T3",
    "authority":   "Layer Zero operators, not administrators",
    "override":    "T1 failure suspends all T4 spending immediately",
    "audit":       "independent — instrument data, not institutional report",
}

def report(self) -> Dict:
    return {
        "community":          self.community_name,
        "population":         self.population,
        "required_T1":        self.REQUIRED_T1,
        "required_T2":        self.REQUIRED_T2,
        "verification":       self.VERIFICATION_STANDARD,
        "governance_rule": (
            "Budget allocation sequence: "
            "T1 fully funded → T2 fully funded → T3 → T4. "
            "Current sequence is inverted. "
            "T4 (data centers, megachurches, admin) "
            "funded first, T1 runs on remainder."
        ),
    }
```

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:

```
print("=" * 80)
print("SURVIVAL ENGINEERING AUDIT — MADISON SUBURB")
print("Shuttle/Submarine Criticality Standards")
print("=" * 80)

spec = build_madison_survival_spec()
checklist = spec.survival_checklist()

print(f"\n{'TIER 1 SECURE':<30} {str(checklist['TIER_1_SECURE']):>10}")
print(f"{'TIER 2 SECURE':<30} {str(checklist['TIER_2_SECURE']):>10}")
print(f"{'PROCEED TO TIER 4':<30} {str(checklist['PROCEED_TO_TIER4']):>10}")

if checklist["critical_failures"]:
    print(f"\nCRITICAL FAILURES:")
    for f in checklist["critical_failures"]:
        print(f"  ✗ {f}")

if checklist["mortality_pathways_active"]:
    print(f"\nACTIVE MORTALITY PATHWAYS (operator gap present):")
    for p in checklist["mortality_pathways_active"]:
        print(f"  ⚠ {p[:100]}...")

if checklist["self_report_violations"]:
    print(f"\nSELF-REPORTING VIOLATIONS (CO2 scrubber problem):")
    for name, count in checklist["self_report_violations"]:
        print(f"  {name}: {count} self-reporting failure modes")

print(f"\n\n{'─'*80}")
print("SYSTEM CRITICALITY TABLE")
print(f"{'─'*80}")
print(f"  {'System':<28} {'Tier':<12} {'Ops Gap':>8} {'Redund':>8} "
      f"{'E-ratio':>8} {'Deviation':>10}")
print(f"  {'─'*27} {'─'*11} {'─'*8} {'─'*8} {'─'*8} {'─'*10}")

for s in spec.systems:
    er = (round(s.energy_ratio, 1)
          if s.energy_ratio != float("inf") else "∞")
    rc = "✓" if s.redundancy_compliant else "✗"
    og = f"+{s.operator_gap}" if s.operator_gap > 0 else "OK"
    tier_short = s.tier.name.replace("T1_PRESSURE_HULL", "T1-HULL")\
                            .replace("T2_LIFE_SUPPORT",  "T2-LIFE")\
                            .replace("T3_MISSION",       "T3-MISS")\
                            .replace("T4_COMFORT",       "T4-COMF")
    print(f"  {s.name:<28} {tier_short:<12} {og:>8} {rc:>8} "
          f"{str(er):>8} {s.purpose_deviation_index:>10.1f}")

print(f"\n\n{'─'*80}")
print("WHAT MUST BE BUILT — SHUTTLE STANDARD MINIMUM")
print(f"{'─'*80}")
build_spec = ShuttleStandardSpec("Madison Suburb", 160_000)
bs = build_spec.report()

print("\nTIER 1 REQUIRED:")
for item in bs["required_T1"]:
    print(f"  {item['system']}")
    print(f"    Spec:     {item['specification'][:80]}")
    print(f"    Cost:     {item['cost_anchor']}")
    print(f"    Quantity: {item['quantity']}")

print("\nTIER 2 REQUIRED:")
for item in bs["required_T2"]:
    print(f"  {item['system']}")
    print(f"    Spec:     {item['specification'][:80]}")
    print(f"    Cost:     {item['cost_anchor']}")

print(f"\nVERIFICATION STANDARD:")
for k, v in bs["verification"].items():
    print(f"  {k:<12} {v}")

print(f"\nGOVERNANCE RULE:")
print(f"  {bs['governance_rule']}")

print(f"\n\n{'─'*80}")
print("DEVIATION SUMMARY — CURRENT vs SHUTTLE STANDARD")
print(f"{'─'*80}")
dev = spec.deviation_from_shuttle_standard()
for tier, gaps in dev["gaps"].items():
    critical = [g for g in gaps
                if g["redundancy_gap"] or g["operator_gap"] > 0
                or g["detection_gap"]]
    if critical:
        print(f"\n  {tier}:")
        for g in critical:
            issues = []
            if g["redundancy_gap"]:
                issues.append("redundancy non-compliant")
            if g["operator_gap"] > 0:
                issues.append(f"operator gap: +{g['operator_gap']}")
            if g["detection_gap"]:
                issues.append("self-reporting violation")
            print(f"    {g['system']}: {', '.join(issues)}")
```
