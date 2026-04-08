# MODULE: sim/city_optimization.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: domain
# Cross-domain upgrade evaluation and leakage auditing
# “””
city_optimization.py

Cross-domain upgrade evaluation for city thermodynamic systems.
Sits above city_thermodynamics.py.

Core insight: Siloed efficiency metrics lie.
True gain = purpose output / TOTAL energy across ALL coupled layers.

Architecture:
UpgradeTest
├── pre/post energy per affected layer
├── pre/post purpose output (physics units)
├── coupling efficiency pre/post
└── net_system_gain() — the only number that matters

LeakageAudit
├── nominal vs actual vs floor per institution
├── leakage_ratio (actual / floor)
├── leakage_vector classification
└── purpose_drift detection

CityOptimizer
├── run_upgrade(test) → UpgradeResult
├── audit_leakage(city) → LeakageReport
└── madison_baseline() → real-world anchor (pop 269k)

Pass/Fail Rule:
Upgrade passes IFF:
purpose_output_post >= 2x purpose_output_pre
AND total_energy_post <= 0.5x total_energy_pre
across ALL coupled layers.
Most “efficiency” spending fails this test.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json

# ── Constants ─────────────────────────────────────────────────────────────────

PASS_PURPOSE_MULTIPLIER  = 2.0   # need 2x purpose output
PASS_ENERGY_FRACTION     = 0.50  # at <= 50% prior total energy
DIGITAL_OVERHEAD_FACTOR  = 0.20  # SCADA/apps/dashboards add ~15-30%; use 20%
COMFORT_CREEP_FACTOR     = 0.80  # captures 80% of technical savings
SCALE_FRICTION_FACTOR    = 0.15  # coordination overhead on any upgrade

# ── Enums ─────────────────────────────────────────────────────────────────────

class LeakageVector(Enum):
COMPUTE_OVERHEAD  = “compute_overhead”    # SCADA, edtech, data centers ~20%
LIGHTING_DENSITY  = “lighting_density”    # streetlights, building interiors ~25%
MOBILE_METABOLISM = “mobile_metabolism”   # trucks, cars, buses ~30%
HVAC_COMFORT      = “hvac_comfort”        # AC/heat beyond survival floor ~15%
ADMIN_FRICTION    = “admin_friction”      # offices, meetings, HR ~10%

class PurposeDrift(Enum):
ON_PURPOSE   = “on_purpose”
MILD_DRIFT   = “mild_drift”      # <5x over floor
MODERATE     = “moderate_drift”  # 5-50x
SEVERE       = “severe_drift”    # 50-500x — institution serving itself
CAPTURED     = “captured”        # >500x — purpose is now scale maintenance

# ── Layer Energy Delta ─────────────────────────────────────────────────────────

@dataclass
class LayerDelta:
“”“Energy change in one layer from an upgrade.”””
layer_name:     str
energy_pre:     float   # kWh/day
energy_post:    float
purpose_pre:    float   # physics units (liters, wounds, incidents)
purpose_post:   float
coupling_pre:   float   # 0.0–1.0
coupling_post:  float
notes:          str = “”

```
@property
def energy_delta(self) -> float:
    return self.energy_post - self.energy_pre

@property
def purpose_delta(self) -> float:
    return self.purpose_post - self.purpose_pre

@property
def coupling_delta(self) -> float:
    return self.coupling_post - self.coupling_pre
```

# ── Upgrade Test ──────────────────────────────────────────────────────────────

@dataclass
class UpgradeTest:
“””
Define an upgrade as a set of layer deltas.
Net system gain computed across ALL affected layers.
“””
name:         str
description:  str
layers:       List[LayerDelta] = field(default_factory=list)
hidden_costs: Dict[str, float] = field(default_factory=dict)
# hidden_costs: e.g. {“maintenance_ratchet”: 5.0, “specialist_overhead”: 3.0}

```
def total_energy_pre(self) -> float:
    return sum(l.energy_pre for l in self.layers)

def total_energy_post(self) -> float:
    base = sum(l.energy_post for l in self.layers)
    return base + sum(self.hidden_costs.values())

def total_purpose_pre(self) -> float:
    return sum(l.purpose_pre for l in self.layers)

def total_purpose_post(self) -> float:
    return sum(l.purpose_post for l in self.layers)

def avg_coupling_pre(self) -> float:
    if not self.layers:
        return 0.0
    return sum(l.coupling_pre for l in self.layers) / len(self.layers)

def avg_coupling_post(self) -> float:
    if not self.layers:
        return 0.0
    return sum(l.coupling_post for l in self.layers) / len(self.layers)

def net_system_gain(self) -> float:
    """
    NET SYSTEM GAIN = (Purpose Output / Total Energy In)
                    × (Coupling Efficiency Across Layers)
    Ratio: post/pre. >1.0 = genuine gain. <1.0 = leakage.
    """
    pre_score  = (self.total_purpose_pre()  / max(1.0, self.total_energy_pre()))  * self.avg_coupling_pre()
    post_score = (self.total_purpose_post() / max(1.0, self.total_energy_post())) * self.avg_coupling_post()
    if pre_score == 0:
        return 0.0
    return post_score / pre_score

def passes(self) -> bool:
    """
    Hard rule: 2x purpose at <=50% total energy across coupled layers.
    Most upgrades fail.
    """
    purpose_ok = self.total_purpose_post() >= PASS_PURPOSE_MULTIPLIER * self.total_purpose_pre()
    energy_ok  = self.total_energy_post()  <= PASS_ENERGY_FRACTION    * self.total_energy_pre()
    return purpose_ok and energy_ok

def red_flags(self) -> List[str]:
    flags = []
    for l in self.layers:
        if l.energy_post > l.energy_pre * (1 + DIGITAL_OVERHEAD_FACTOR):
            flags.append(f"{l.layer_name}: digital overhead suspected (+{l.energy_delta:.0f} kWh)")
        if l.coupling_post < l.coupling_pre:
            flags.append(f"{l.layer_name}: coupling degraded ({l.coupling_pre:.2f}→{l.coupling_post:.2f})")
        if l.purpose_post < l.purpose_pre:
            flags.append(f"{l.layer_name}: purpose output fell ({l.purpose_pre:.1f}→{l.purpose_post:.1f})")
    if self.hidden_costs:
        flags.append(f"Hidden costs: {sum(self.hidden_costs.values()):.1f} kWh/day ({list(self.hidden_costs.keys())})")
    return flags

def report(self) -> Dict:
    return {
        "upgrade":           self.name,
        "description":       self.description,
        "energy_pre_total":  round(self.total_energy_pre(), 1),
        "energy_post_total": round(self.total_energy_post(), 1),
        "energy_change_pct": round((self.total_energy_post() / max(1, self.total_energy_pre()) - 1) * 100, 1),
        "purpose_pre_total": round(self.total_purpose_pre(), 1),
        "purpose_post_total":round(self.total_purpose_post(), 1),
        "purpose_change_pct":round((self.total_purpose_post() / max(1, self.total_purpose_pre()) - 1) * 100, 1),
        "coupling_pre":      round(self.avg_coupling_pre(), 3),
        "coupling_post":     round(self.avg_coupling_post(), 3),
        "net_system_gain":   round(self.net_system_gain(), 3),
        "passes_2x_test":    self.passes(),
        "red_flags":         self.red_flags(),
        "layer_detail":      [
            {
                "layer":         l.layer_name,
                "energy_delta":  round(l.energy_delta, 1),
                "purpose_delta": round(l.purpose_delta, 1),
                "coupling_pre":  round(l.coupling_pre, 3),
                "coupling_post": round(l.coupling_post, 3),
                "notes":         l.notes,
            }
            for l in self.layers
        ],
    }
```

# ── Leakage Audit ─────────────────────────────────────────────────────────────

@dataclass
class InstitutionLeakage:
name:           str
floor_kwh:      float
actual_kwh:     float
primary_vector: LeakageVector
purpose_units:  str   # what physics it delivers
purpose_drift:  PurposeDrift
drift_note:     str = “”

```
@property
def leakage_ratio(self) -> float:
    if self.floor_kwh == 0:
        return float("inf") if self.actual_kwh > 0 else 1.0
    return self.actual_kwh / self.floor_kwh

@property
def leakage_pct_over_floor(self) -> str:
    if self.floor_kwh == 0:
        return "∞" if self.actual_kwh > 0 else "0%"
    return f"{((self.actual_kwh / self.floor_kwh) - 1) * 100:.0f}%"

def report(self) -> Dict:
    return {
        "institution":    self.name,
        "floor_kwh":      self.floor_kwh,
        "actual_kwh":     self.actual_kwh,
        "leakage_over_floor": self.leakage_pct_over_floor,
        "primary_vector": self.primary_vector.value,
        "purpose_units":  self.purpose_units,
        "purpose_drift":  self.purpose_drift.value,
        "drift_note":     self.drift_note,
    }
```

# ── Madison Baseline ──────────────────────────────────────────────────────────

def madison_baseline() -> List[InstitutionLeakage]:
“””
Real-world anchor: Madison WI, pop 269k.
Total electricity ~3.5B kWh/yr → ~36 kWh/person/day.
Modern minimum benchmark: ~2.7 kWh/person/day.
Reference unit: per 1000 people/day unless noted.
“””
return [
InstitutionLeakage(
name=“Church”,
floor_kwh=5, actual_kwh=50,
primary_vector=LeakageVector.HVAC_COMFORT,
purpose_units=“coordination-events/day”,
purpose_drift=PurposeDrift.MILD_DRIFT,
drift_note=“AC + paid staff metabolism vs coordination ritual”,
),
InstitutionLeakage(
name=“School”,
floor_kwh=10, actual_kwh=500,
primary_vector=LeakageVector.COMPUTE_OVERHEAD,
purpose_units=“skill-transfers/day”,
purpose_drift=PurposeDrift.SEVERE,
drift_note=“Edtech + transport vs skill transfer — credential mill”,
),
InstitutionLeakage(
name=“City Water”,
floor_kwh=20, actual_kwh=500,
primary_vector=LeakageVector.COMPUTE_OVERHEAD,
purpose_units=“m³ H2O delivered/day”,
purpose_drift=PurposeDrift.MODERATE,
drift_note=“SCADA + over-pumping vs H2O delivery”,
),
InstitutionLeakage(
name=“Sewer”,
floor_kwh=0, actual_kwh=200,
primary_vector=LeakageVector.COMPUTE_OVERHEAD,
purpose_units=“m³ waste exported/day”,
purpose_drift=PurposeDrift.CAPTURED,
drift_note=“Sensors + electric lifts where gravity was sufficient”,
),
InstitutionLeakage(
name=“Electricity Grid”,
floor_kwh=50, actual_kwh=10000,
primary_vector=LeakageVector.LIGHTING_DENSITY,
purpose_units=“kWh useful work delivered/day”,
purpose_drift=PurposeDrift.CAPTURED,
drift_note=“Data centers + lighting density vs work extraction”,
),
InstitutionLeakage(
name=“Roads/Transport”,
floor_kwh=0, actual_kwh=5000,
primary_vector=LeakageVector.MOBILE_METABOLISM,
purpose_units=“person-km/day”,
purpose_drift=PurposeDrift.CAPTURED,
drift_note=“Streetlights + traffic mgmt — asphalt maintenance state”,
),
InstitutionLeakage(
name=“Garbage Collection”,
floor_kwh=0, actual_kwh=500,
primary_vector=LeakageVector.MOBILE_METABOLISM,
purpose_units=“m³ waste dispersed/day”,
purpose_drift=PurposeDrift.CAPTURED,
drift_note=“Collection logistics vs entropy dilution”,
),
InstitutionLeakage(
name=“Fire Department”,
floor_kwh=0, actual_kwh=100,
primary_vector=LeakageVector.MOBILE_METABOLISM,
purpose_units=“fires suppressed/incident”,
purpose_drift=PurposeDrift.MODERATE,
drift_note=“Diesel apparatus vs heat quench”,
),
InstitutionLeakage(
name=“Police”,
floor_kwh=0, actual_kwh=50,
primary_vector=LeakageVector.ADMIN_FRICTION,
purpose_units=“incidents resolved/day”,
purpose_drift=PurposeDrift.SEVERE,
drift_note=“Patrol vehicles + paperwork engine vs kinetic restraint”,
),
]

def leakage_summary(institutions: List[InstitutionLeakage]) -> Dict:
total_floor  = sum(i.floor_kwh for i in institutions)
total_actual = sum(i.actual_kwh for i in institutions)
vector_totals = {}
for v in LeakageVector:
vector_totals[v.value] = sum(
i.actual_kwh for i in institutions if i.primary_vector == v
)
return {
“total_floor_kwh_per_1000”:  total_floor,
“total_actual_kwh_per_1000”: total_actual,
“system_leakage_pct”:        f”{((total_actual / max(1, total_floor)) - 1) * 100:.0f}%” if total_floor > 0 else “∞”,
“kwh_per_person_floor”:      round(total_floor  / 1000, 3),
“kwh_per_person_actual”:     round(total_actual / 1000, 3),
“leakage_by_vector”:         vector_totals,
“vector_ranking”: sorted(
vector_totals.items(), key=lambda x: x[1], reverse=True
),
“institutions”: [i.report() for i in institutions],
}

# ── Preset Upgrade Tests ──────────────────────────────────────────────────────

def test_smart_water_meters() -> UpgradeTest:
return UpgradeTest(
name=“Smart Water Meters”,
description=“10% pumping savings via meter data — siloed view says good”,
layers=[
LayerDelta(“Water”,  energy_pre=100, energy_post=90,
purpose_pre=1000, purpose_post=1000,
coupling_pre=1.0, coupling_post=1.0,
notes=“10% pump savings”),
LayerDelta(“Sewer”,  energy_pre=25, energy_post=40,
purpose_pre=1000, purpose_post=1000,
coupling_pre=1.0, coupling_post=1.0,
notes=“new SCADA integration required”),
LayerDelta(“Admin”,  energy_pre=0, energy_post=15,
purpose_pre=0, purpose_post=0,
coupling_pre=1.0, coupling_post=1.0,
notes=“data analysts, dashboards”),
],
hidden_costs={“maintenance_ratchet”: 5.0},
)

def test_led_streetlights() -> UpgradeTest:
return UpgradeTest(
name=“LED Streetlights”,
description=“20kWh/day roads savings — but coupling effect on foot traffic”,
layers=[
LayerDelta(“Roads”,      energy_pre=50, energy_post=30,
purpose_pre=1000, purpose_post=1000,
coupling_pre=0.80, coupling_post=0.72,
notes=”-20kWh; darker streets reduce foot traffic → more car use”),
LayerDelta(“Electricity”,energy_pre=10, energy_post=15,
purpose_pre=500, purpose_post=500,
coupling_pre=0.90, coupling_post=0.90,
notes=”+5kWh maintenance overhead”),
LayerDelta(“Police”,     energy_pre=10, energy_post=12,
purpose_pre=100, purpose_post=100,
coupling_pre=0.70, coupling_post=0.70,
notes=”+2kWh patrols needed in darker zones”),
],
)

def test_smart_grid() -> UpgradeTest:
return UpgradeTest(
name=“Smart Grid”,
description=“10% grid efficiency — but digital interlocks increase cascade risk”,
layers=[
LayerDelta(“Electricity”,energy_pre=500, energy_post=450,
purpose_pre=1000, purpose_post=1000,
coupling_pre=0.85, coupling_post=0.75,
notes=”-10% efficiency; digital interlocks fail together”),
LayerDelta(“Water”,      energy_pre=200, energy_post=216,
purpose_pre=1000, purpose_post=1000,
coupling_pre=0.90, coupling_post=0.85,
notes=”+8% SCADA load”),
LayerDelta(“Hospital”,   energy_pre=100, energy_post=112,
purpose_pre=200, purpose_post=200,
coupling_pre=0.95, coupling_post=0.88,
notes=”+12% IT integration overhead”),
],
)

def test_ev_police_cars() -> UpgradeTest:
return UpgradeTest(
name=“EV Police Cars”,
description=”-30% fuel but charging downtime degrades response time”,
layers=[
LayerDelta(“Police”,     energy_pre=100, energy_post=70,
purpose_pre=100, purpose_post=80,
coupling_pre=0.80, coupling_post=0.64,
notes=”-30% fuel; response time +20% from charging downtime”),
LayerDelta(“Electricity”,energy_pre=500, energy_post=700,
purpose_pre=1000, purpose_post=1000,
coupling_pre=0.85, coupling_post=0.85,
notes=”+40% charging load”),
LayerDelta(“Roads”,      energy_pre=50, energy_post=57,
purpose_pre=1000, purpose_post=1000,
coupling_pre=0.80, coupling_post=0.80,
notes=”+15% charging station footprint”),
],
)

def test_proven_bucket_brigades() -> UpgradeTest:
“”“Proven winner: reverting to floor tech.”””
return UpgradeTest(
name=“Bucket Brigades (revert from smart hydrants)”,
description=“Floor tech: 0 kWh, direct human-to-water coupling”,
layers=[
LayerDelta(“Fire”,  energy_pre=50, energy_post=0,
purpose_pre=10, purpose_post=20,
coupling_pre=0.45, coupling_post=0.90,
notes=“Direct access to input; no pump failure modes”),
],
)

def test_foot_patrol() -> UpgradeTest:
“”“Proven winner: operator dominant profile at floor.”””
return UpgradeTest(
name=“Foot Patrol (revert from EV cruisers)”,
description=“Operator ceiling 0.80 — skill substitutes for vehicle”,
layers=[
LayerDelta(“Police”, energy_pre=50, energy_post=10,
purpose_pre=100, purpose_post=150,
coupling_pre=0.50, coupling_post=0.85,
notes=”+50% coverage area; -80% energy; community coupling improves”),
],
)

# ── Runner ────────────────────────────────────────────────────────────────────

def run_all_tests() -> List[Dict]:
tests = [
test_smart_water_meters(),
test_led_streetlights(),
test_smart_grid(),
test_ev_police_cars(),
test_proven_bucket_brigades(),
test_foot_patrol(),
]
return [t.report() for t in tests]

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:

```
print("=== MADISON WI LEAKAGE AUDIT ===\n")
baseline = madison_baseline()
print(json.dumps(leakage_summary(baseline), indent=2))

print("\n\n=== UPGRADE TESTS ===\n")
for result in run_all_tests():
    print(f"--- {result['upgrade']} ---")
    print(f"  Energy:   {result['energy_pre_total']} → {result['energy_post_total']} kWh ({result['energy_change_pct']:+.1f}%)")
    print(f"  Purpose:  {result['purpose_pre_total']} → {result['purpose_post_total']} ({result['purpose_change_pct']:+.1f}%)")
    print(f"  Net gain: {result['net_system_gain']:.3f}  |  Passes 2x test: {result['passes_2x_test']}")
    if result["red_flags"]:
        for flag in result["red_flags"]:
            print(f"  ⚑ {flag}")
    print()
```
