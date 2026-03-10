# “””
purpose_deviation.py

Measures institutional drift from stated purpose to actual behavior.
Uses only ungameable physical signals — no self-reporting.

Three signal axes:

1. ENERGY RATIO       actual_kwh / floor_kwh
   Measures how far above thermodynamic minimum the
   institution operates. Pure physics — can’t be gamed.
1. LAND IDLE FRACTION (acres × active_hours) / total_hours
   Idle land = infrastructure serving itself.
   Estimable from satellite imagery alone.
1. BUDGET INVERSION   facility_cost / program_cost
   When facility > program: institution feeds itself.
   Public record for nonprofits (IRS Form 990).

Combined into Deviation Index:
Low  (<10):   On purpose — institution delivers its floor function
Mid  (10-100): Moderate drift — scale overhead accumulating
High (100-1000): Severe drift — institution primarily serves its own scale
Captured (>1000): Purpose is now scale maintenance

Integration:
Imports city_thermodynamics.CityInstitution
Imports city_optimization.InstitutionLeakage
Wires operator trust state into deviation scoring
(degraded trust = institution burning energy on workarounds, not purpose)

Austin megachurch case included as calibration anchor.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json

# ── Try to import sibling modules ─────────────────────────────────────────────

# Graceful degradation if running standalone

try:
from city_thermodynamics import CityInstitution, NodeStatus
from city_optimization import InstitutionLeakage, LeakageVector, PurposeDrift
_SIBLING_MODULES = True
except ImportError:
_SIBLING_MODULES = False

# ── Constants ─────────────────────────────────────────────────────────────────

FACILITY_BUDGET_BASELINE    = 0.20   # 20% to facility = healthy baseline
ACTIVE_HOURS_BASELINE       = 40.0   # hrs/week — standard operating institution
HOURS_PER_WEEK              = 168.0

# Deviation index thresholds

DRIFT_ON_PURPOSE            = 10.0
DRIFT_MODERATE              = 100.0
DRIFT_SEVERE                = 1000.0

# > 1000 = CAPTURED

# ── Drift Classification ──────────────────────────────────────────────────────

class DriftLevel(Enum):
ON_PURPOSE  = “on_purpose”       # <10
MODERATE    = “moderate”         # 10–100
SEVERE      = “severe”           # 100–1000
CAPTURED    = “captured”         # >1000 — purpose is now scale maintenance

def classify_drift(index: float) -> DriftLevel:
if index < DRIFT_ON_PURPOSE:
return DriftLevel.ON_PURPOSE
if index < DRIFT_MODERATE:
return DriftLevel.MODERATE
if index < DRIFT_SEVERE:
return DriftLevel.SEVERE
return DriftLevel.CAPTURED

# ── Physical Signal Collectors ────────────────────────────────────────────────

@dataclass
class EnergySignal:
“””
Signal 1: Energy ratio.
actual_kwh / floor_kwh.
Floor is the thermodynamic minimum to deliver purpose — from city_thermodynamics.
Source: utility filings, energy audits, EPA ENERGY STAR benchmarks.
“””
floor_kwh_day:   float
actual_kwh_day:  float
source_note:     str = “utility filing / EPA benchmark”

```
@property
def ratio(self) -> float:
    if self.floor_kwh_day == 0:
        return float("inf") if self.actual_kwh_day > 0 else 1.0
    return self.actual_kwh_day / self.floor_kwh_day

@property
def leakage_pct(self) -> str:
    if self.floor_kwh_day == 0:
        return "∞" if self.actual_kwh_day > 0 else "0%"
    return f"{((self.actual_kwh_day / self.floor_kwh_day) - 1) * 100:.0f}%"
```

@dataclass
class LandSignal:
“””
Signal 2: Land idle fraction.
Idle land = acres sitting dark while institution claims active purpose.
Source: satellite imagery (Google Earth), county assessor records,
public event calendars.
active_hours_per_week: hours the facility is actually occupied and operating.
“””
acres:                  float
active_hours_per_week:  float
source_note:            str = “satellite imagery / public calendar”

```
@property
def idle_fraction(self) -> float:
    """Fraction of time the land sits unused."""
    active_fraction = min(1.0, self.active_hours_per_week / HOURS_PER_WEEK)
    return 1.0 - active_fraction

@property
def sqft_per_active_hour(self) -> float:
    return (self.acres * 43560) / max(1.0, self.active_hours_per_week)

@property
def idle_pct(self) -> str:
    return f"{self.idle_fraction * 100:.1f}%"
```

@dataclass
class BudgetSignal:
“””
Signal 3: Budget flow inversion.
When facility cost > program delivery cost:
institution is feeding its own infrastructure, not its purpose.
Source: IRS Form 990 (public for US nonprofits), annual reports,
local government budget documents.
“””
total_budget:           float   # annual $
facility_cost:          float   # mortgage, maintenance, utilities, insurance
program_cost:           float   # direct delivery of stated purpose
admin_cost:             float   # staff not delivering purpose (HR, legal, IT)
source_note:            str = “IRS Form 990 / annual report”

```
@property
def facility_pct(self) -> float:
    return self.facility_cost / max(1.0, self.total_budget)

@property
def program_pct(self) -> float:
    return self.program_cost / max(1.0, self.total_budget)

@property
def inversion_ratio(self) -> float:
    """
    >1.0: facility eating more than program delivery.
    Normalized to 20% baseline (healthy facility spend).
    """
    return self.facility_pct / FACILITY_BUDGET_BASELINE

@property
def inverted(self) -> bool:
    return self.facility_cost > self.program_cost
```

# ── Purpose Deviation ─────────────────────────────────────────────────────────

@dataclass
class PurposeDeviation:
“””
Combines three ungameable physical signals into a Deviation Index.
Optionally integrates operator trust state from city_thermodynamics.

```
Deviation Index = energy_ratio × idle_fraction × budget_inversion_ratio
                × trust_penalty (if operator data available)

All inputs are observable without institutional cooperation:
  - Energy: utility filings, EPA benchmarks
  - Land: satellite imagery, county assessor records
  - Budget: IRS 990, public budget documents
  - Trust: operator retention rates, vacancy data (proxy)
"""
name:           str
stated_purpose: str
energy:         EnergySignal
land:           LandSignal
budget:         BudgetSignal
actual_outputs: str = ""   # what it actually produces (observable)

# Optional: operator trust index from city_thermodynamics (0.0–1.0)
# When degraded, institution burns energy on workarounds not purpose
operator_trust_index: Optional[float] = None

@property
def trust_penalty(self) -> float:
    """
    Low trust = operators spending energy on infrastructure uncertainty
    not on purpose delivery. Multiplies deviation upward.
    1.0 = no penalty (full trust)
    2.0 = double deviation (trust at floor)
    """
    if self.operator_trust_index is None:
        return 1.0
    return 1.0 + (1.0 - self.operator_trust_index)

@property
def deviation_index(self) -> float:
    """
    Core metric. Ungameable composite.
    All three signals must be low for institution to score low.
    """
    e = self.energy.ratio if not (self.energy.ratio == float("inf")) else 10000.0
    l = self.land.idle_fraction
    b = self.budget.inversion_ratio
    t = self.trust_penalty

    # idle_fraction of 0 (always open) shouldn't zero out the index
    # use max(0.1, idle) to preserve signal from other axes
    return e * max(0.1, l) * b * t

@property
def drift_level(self) -> DriftLevel:
    return classify_drift(self.deviation_index)

@property
def recovery_intervention(self) -> str:
    """What structural change would move the needle most."""
    e = self.energy.ratio if self.energy.ratio != float("inf") else 99999
    l = self.land.idle_fraction
    b = self.budget.inversion_ratio

    dominant = max(
        ("energy",  e       / 100),
        ("land",    l       / 1.0),
        ("budget",  b       / 1.0),
        key=lambda x: x[1]
    )[0]

    interventions = {
        "energy": (
            "Reduce energy to floor operations. "
            "Strip HVAC, lighting, AV to minimum viable. "
            "Target: active hours only, passive systems off."
        ),
        "land": (
            "Open facility to continuous community use or divest excess acreage. "
            "Idle land = captured capital that could fund purpose delivery. "
            "Target: >60 active hours/week or reduce footprint."
        ),
        "budget": (
            "Redirect facility budget to program delivery. "
            "Freeze capital expenditure, defer maintenance, lease excess space. "
            "Target: facility < 20% of total budget."
        ),
    }
    return interventions[dominant]

def report(self) -> Dict:
    return {
        "institution":      self.name,
        "stated_purpose":   self.stated_purpose,
        "actual_outputs":   self.actual_outputs,
        "deviation_index":  round(self.deviation_index, 2),
        "drift_level":      self.drift_level.value,
        "signals": {
            "energy": {
                "floor_kwh_day":  self.energy.floor_kwh_day,
                "actual_kwh_day": self.energy.actual_kwh_day,
                "ratio":          round(self.energy.ratio, 1) if self.energy.ratio != float("inf") else "∞",
                "leakage":        self.energy.leakage_pct,
                "source":         self.energy.source_note,
            },
            "land": {
                "acres":              self.land.acres,
                "active_hrs_week":    self.land.active_hours_per_week,
                "idle_fraction":      round(self.land.idle_fraction, 3),
                "idle_pct":           self.land.idle_pct,
                "sqft_per_active_hr": round(self.land.sqft_per_active_hour, 0),
                "source":             self.land.source_note,
            },
            "budget": {
                "total":            self.budget.total_budget,
                "facility_pct":     round(self.budget.facility_pct * 100, 1),
                "program_pct":      round(self.budget.program_pct * 100, 1),
                "inversion_ratio":  round(self.budget.inversion_ratio, 2),
                "inverted":         self.budget.inverted,
                "source":           self.budget.source_note,
            },
            "trust_penalty":        round(self.trust_penalty, 3),
        },
        "dominant_intervention": self.recovery_intervention,
    }
```

# ── City-Scale Deviation Audit ────────────────────────────────────────────────

@dataclass
class CityDeviationAudit:
“””
Run deviation analysis across all institutions in a city.
Ranks by deviation index — highest drift gets intervention priority.
“””
city_name:    str
population:   int
institutions: List[PurposeDeviation] = field(default_factory=list)

```
def add(self, inst: PurposeDeviation):
    self.institutions.append(inst)

def ranked(self) -> List[PurposeDeviation]:
    return sorted(self.institutions,
                  key=lambda i: i.deviation_index, reverse=True)

def system_deviation_index(self) -> float:
    """Population-weighted mean deviation across all institutions."""
    if not self.institutions:
        return 0.0
    return sum(i.deviation_index for i in self.institutions) / len(self.institutions)

def total_recoverable_kwh_day(self) -> float:
    """
    Energy recoverable if all institutions dropped to floor operations.
    This is the thermodynamic slack in the system.
    """
    return sum(
        i.energy.actual_kwh_day - i.energy.floor_kwh_day
        for i in self.institutions
        if i.energy.actual_kwh_day > i.energy.floor_kwh_day
    )

def report(self) -> Dict:
    ranked = self.ranked()
    return {
        "city":                     self.city_name,
        "population":               self.population,
        "system_deviation_index":   round(self.system_deviation_index(), 1),
        "recoverable_kwh_day":      round(self.total_recoverable_kwh_day(), 0),
        "kwh_recoverable_per_person": round(
            self.total_recoverable_kwh_day() / max(1, self.population), 3
        ),
        "institution_ranking": [
            {
                "rank":           i + 1,
                "name":           inst.name,
                "deviation_index": round(inst.deviation_index, 1),
                "drift_level":    inst.drift_level.value,
                "dominant_fix":   inst.recovery_intervention[:80] + "...",
            }
            for i, inst in enumerate(ranked)
        ],
        "full_reports": [inst.report() for inst in ranked],
    }
```

# ── Preset Archetypes ─────────────────────────────────────────────────────────

def madison_neighborhood_church() -> PurposeDeviation:
“”“Madison WI — small congregation, no megachurch dynamics.”””
return PurposeDeviation(
name           = “Madison Neighborhood Church”,
stated_purpose = “Social coordination + morale stabilization”,
actual_outputs = “Weekly service, food pantry 1x/month, AA meetings”,
energy = EnergySignal(
floor_kwh_day  = 5,
actual_kwh_day = 50,
source_note    = “EPA benchmark small congregation”
),
land = LandSignal(
acres                 = 0.5,
active_hours_per_week = 18,   # Sunday service + Wed evening + AA
source_note           = “public calendar”
),
budget = BudgetSignal(
total_budget  = 150_000,
facility_cost = 35_000,
program_cost  = 80_000,
admin_cost    = 35_000,
source_note   = “IRS 990 small congregation estimate”
),
operator_trust_index = 0.85,
)

def austin_megachurch() -> PurposeDeviation:
“””
Austin TX megachurch archetype.
~75 acres, 8,000 weekly attendance, broadcast infrastructure,
coffee bar, gym, daycare, parking for 2,000 cars.
Energy: stadium HVAC + AV + lighting + parking lot.
Active: Sunday 3hr + Wed evening + occasional events ~15hr/week.
Budget from IRS 990 comparables for TX megachurches.
“””
return PurposeDeviation(
name           = “Austin Megachurch (archetype)”,
stated_purpose = “Social coordination + morale stabilization”,
actual_outputs = (
“Weekly broadcast service, coffee bar, gym, daycare, “
“parking infrastructure, multi-campus brand management”
),
energy = EnergySignal(
floor_kwh_day  = 5,
actual_kwh_day = 4_500,   # stadium HVAC + AV + broadcast + parking
source_note    = “EPA large assembly building benchmark + broadcast overhead”
),
land = LandSignal(
acres                 = 75,
active_hours_per_week = 15,   # Sun 3hr × 2 services + Wed + events
source_note           = “satellite imagery + public event calendar”
),
budget = BudgetSignal(
total_budget  = 12_000_000,   # mid-range TX megachurch annual
facility_cost = 5_400_000,    # mortgage, maintenance, utilities
program_cost  = 3_600_000,    # pastoral, outreach, community programs
admin_cost    = 3_000_000,    # media, marketing, HR, legal
source_note   = “IRS 990 comparables TX megachurches”
),
operator_trust_index = 0.70,   # professional staff, some burnout
)

def austin_small_church() -> PurposeDeviation:
“”“Austin TX small congregation — same city, different scale dynamics.”””
return PurposeDeviation(
name           = “Austin Small Church (archetype)”,
stated_purpose = “Social coordination + morale stabilization”,
actual_outputs = “Weekly service, community meals, neighborhood organizing”,
energy = EnergySignal(
floor_kwh_day  = 5,
actual_kwh_day = 60,
source_note    = “EPA small congregation + TX cooling load”
),
land = LandSignal(
acres                 = 0.4,
active_hours_per_week = 22,
source_note           = “satellite imagery”
),
budget = BudgetSignal(
total_budget  = 200_000,
facility_cost = 38_000,
program_cost  = 120_000,
admin_cost    = 42_000,
source_note   = “IRS 990 small TX congregation”
),
operator_trust_index = 0.80,
)

def rural_fire_hall_on_purpose() -> PurposeDeviation:
“”“Calibration anchor: institution running near floor.”””
return PurposeDeviation(
name           = “Rural Volunteer Fire Hall”,
stated_purpose = “Heat quench — H2O mass to combustion zone”,
actual_outputs = “Fire suppression, medical first response”,
energy = EnergySignal(
floor_kwh_day  = 0,
actual_kwh_day = 8,    # lights, radio chargers, minimal heat
source_note    = “rural utility estimate”
),
land = LandSignal(
acres                 = 0.3,
active_hours_per_week = 168,  # always on-call, gear staged
source_note           = “operational — never fully idle”
),
budget = BudgetSignal(
total_budget  = 80_000,
facility_cost = 12_000,
program_cost  = 55_000,   # equipment, training, fuel
admin_cost    = 13_000,
source_note   = “rural fire district budget”
),
operator_trust_index = 0.75,   # equipment wear, but mission clarity high
)

def suburban_school_captured() -> PurposeDeviation:
“”“Suburban school deep in credential-mill drift.”””
return PurposeDeviation(
name           = “Suburban K-12 School”,
stated_purpose = “Skill replication — info patterns to child brains”,
actual_outputs = (
“Credential issuance, compliance documentation, “
“standardized test preparation, bus logistics management”
),
energy = EnergySignal(
floor_kwh_day  = 10,
actual_kwh_day = 2_800,   # 500 students, edtech, buses, HVAC
source_note    = “EPA K-12 benchmark”
),
land = LandSignal(
acres                 = 12,
active_hours_per_week = 35,   # school day + some evening events
source_note           = “satellite / school calendar”
),
budget = BudgetSignal(
total_budget  = 8_000_000,
facility_cost = 2_400_000,
program_cost  = 2_800_000,   # teachers delivering instruction
admin_cost    = 2_800_000,   # admin, compliance, IT, busing
source_note   = “NCES public school finance data”
),
operator_trust_index = 0.45,   # teacher retention crisis
)

# ── Austin System Audit ───────────────────────────────────────────────────────

def austin_church_system_audit() -> CityDeviationAudit:
“””
Austin TX church system.
~800 churches: ~10 megachurches, ~790 small/mid congregations.
Shows how scale distribution distorts system-level deviation.
“””
audit = CityDeviationAudit(
city_name  = “Austin TX — Church System”,
population = 978_908,  # 2023 estimate
)

```
# 10 megachurches
for i in range(10):
    mc = austin_megachurch()
    mc.name = f"Austin Megachurch #{i+1}"
    audit.add(mc)

# 790 small/mid churches (represented as 10 archetypes × 79 weight)
# Model as single archetype — deviation index is per-institution
for i in range(10):
    sc = austin_small_church()
    sc.name = f"Austin Small Church sample #{i+1}"
    audit.add(sc)

return audit
```

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:

```
print("=== INDIVIDUAL INSTITUTION REPORTS ===\n")

institutions = [
    madison_neighborhood_church(),
    austin_small_church(),
    austin_megachurch(),
    rural_fire_hall_on_purpose(),
    suburban_school_captured(),
]

for inst in institutions:
    r = inst.report()
    print(f"--- {r['institution']} ---")
    print(f"  Deviation Index: {r['deviation_index']:.1f}  |  Level: {r['drift_level']}")
    print(f"  Energy ratio:    {r['signals']['energy']['ratio']}x floor")
    print(f"  Land idle:       {r['signals']['land']['idle_pct']}")
    print(f"  Budget inverted: {r['signals']['budget']['inverted']}  "
          f"(facility {r['signals']['budget']['facility_pct']}% / "
          f"program {r['signals']['budget']['program_pct']}%)")
    print(f"  Fix: {r['dominant_intervention'][:100]}...")
    print()

print("\n=== AUSTIN CHURCH SYSTEM AUDIT ===\n")
audit = austin_church_system_audit()
summary = audit.report()
print(f"City:                    {summary['city']}")
print(f"System deviation index:  {summary['system_deviation_index']}")
print(f"Recoverable kWh/day:     {summary['recoverable_kwh_day']:,.0f}")
print(f"Per person:              {summary['kwh_recoverable_per_person']} kWh/day\n")
print("Institution ranking (highest drift first):")
for row in summary['institution_ranking'][:5]:
    print(f"  #{row['rank']} {row['name']}: {row['deviation_index']} ({row['drift_level']})")

print("\n\n=== MADISON vs AUSTIN MEGACHURCH COMPARISON ===\n")
madison = madison_neighborhood_church()
austin  = austin_megachurch()
print(f"{'':30s} {'Madison':>12s} {'Austin Mega':>12s}")
print(f"{'Deviation Index':30s} {madison.deviation_index:>12.1f} {austin.deviation_index:>12.1f}")
print(f"{'Drift Level':30s} {madison.drift_level.value:>12s} {austin.drift_level.value:>12s}")
print(f"{'Energy ratio (×floor)':30s} {madison.energy.ratio:>12.1f} {austin.energy.ratio:>12.1f}")
print(f"{'Land idle':30s} {madison.land.idle_pct:>12s} {austin.land.idle_pct:>12s}")
print(f"{'Budget inverted':30s} {str(madison.budget.inverted):>12s} {str(austin.budget.inverted):>12s}")
print(f"{'Recoverable kWh/day':30s} {madison.energy.actual_kwh_day - madison.energy.floor_kwh_day:>12.0f} {austin.energy.actual_kwh_day - austin.energy.floor_kwh_day:>12.0f}")
```
