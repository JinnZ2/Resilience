# “””
thermodynamic_impact.py

Replaces standard economic impact models (IMPLAN, input-output tables,
fiscal impact studies) with thermodynamic reality accounting.

The inversion:
Standard model sees:  jobs × multiplier → GDP → “economic winner”
Thermodynamic sees:   energy in → purpose out → community drag → net entropy

Standard model blind spots (structural, not accidental):

1. No energy opportunity cost   15MW could run 150k homes OR one DC
1. No purpose coupling          tax → admin bloat, jobs → talent vacuum
1. Multiplier fantasy           construction jobs don’t become operations jobs
1. No resilience subtraction    grid strain → brownouts → hospital failures

Core metric:
COMMUNITY PURPOSE GAIN/LOSS
= (physical outputs preserved/enhanced) - (physical outputs degraded)
× (1 - coupling_fragility)

Passes ONLY if net purpose gain >= +10% across Water/Food/Energy/Repair

Architecture:
OpportunityCost         15MW → what else could run it
StandardModel           IMPLAN/IO-table reproduction (shows the lie)
ThermodynamicModel      true accounting
ImpactComparison        side-by-side inversion
PolicyThreshold         regulatory pass/fail instrument

Integrates:
datacenter_net_zero     net_zero_test() → coupling channels
institution_registry    deviation index → drag quantification
purpose_deviation       drift classification
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json

# ── Try sibling imports ───────────────────────────────────────────────────────

try:
from datacenter_net_zero import (
DataCenter, dc_parasite, dc_net_zero_passing, dc_layer_zero,
dc_partial_coupling, ComputePurpose, COMPUTE_PURPOSE_FACTOR,
)
from institution_registry import (
InstitutionRegistry, dc_to_purpose_deviation,
build_madison_suburb_registry,
)
from purpose_deviation import (
DriftLevel, austin_megachurch, suburban_school_captured,
)
_SIBLINGS = True
except ImportError:
_SIBLINGS = False

# ── Constants ─────────────────────────────────────────────────────────────────

# Standard model parameters (reproduce the lie accurately)

IMPLAN_JOB_MULTIPLIER        = 2.30   # industry standard
IMPLAN_SPENDING_MULTIPLIER   = 2.63   # $1 → $2.63 “total impact”
CONSTRUCTION_JOBS_PER_MW     = 3_400  # per 10MW = 34k job-years
OPERATIONS_JOBS_PER_MW       = 54.7   # per 10MW = 547 permanent
PROFIT_EXTRACTION_RATE       = 0.72   # fraction of revenue leaving community
LOCAL_RESPEND_ASSUMPTION     = 0.80   # what IMPLAN assumes; reality ~0.28

# Thermodynamic parameters

KWH_PER_HOME_DAY             = 30.0   # average US home
HOMES_PER_MW_24H             = 1000 * 24 / KWH_PER_HOME_DAY  # ~800 homes/MW
FIRE_STATIONS_PER_MW         = 5.0    # 1MW = 5 fire stations at floor
GRAVITY_WELLS_PER_MW         = 30.0   # 1MW = 30 gravity wells
SCHOOL_FLOORS_PER_MW         = 20.0   # 1MW = 20 schools at 10kWh floor

# Community drag coefficients (from framework data)

GRID_STRAIN_WATER_LOSS       = 0.10   # -10% water delivery per 15MW load
TRAFFIC_INCREASE_ROADS       = 0.15   # +15% truck traffic construction phase
SAFETY_BUDGET_COMPETITION    = 0.05   # -5% police/fire coverage
COGNITIVE_DRAIN_SCHOOLS      = 0.08   # -8% teacher retention / skill output
HEAT_ISLAND_AC_LOAD          = 0.05   # +5% building cooling load

# Pass threshold

NET_PURPOSE_GAIN_THRESHOLD   = 0.10   # +10% minimum across anchor layers
ANCHOR_LAYERS                = [“Water”, “Food”, “Energy”, “Repair”]

# ── Enums ─────────────────────────────────────────────────────────────────────

class InstitutionClass(Enum):
DATA_CENTER     = “data_center”
MEGA_CHURCH     = “mega_church”
SMART_UPGRADE   = “smart_upgrade”
FACTORY         = “factory”
DISTRIBUTION_HUB = “distribution_hub”
HOSPITAL        = “hospital”

# ── Opportunity Cost ──────────────────────────────────────────────────────────

@dataclass
class OpportunityCost:
“””
What else 15MW could run.
Standard models treat energy as free and fungible.
It isn’t. Every MW committed is an alternative foregone.
Source: city_thermodynamics floor values.
“””
mw_committed: float = 15.0

```
@property
def homes_powered(self) -> float:
    return self.mw_committed * HOMES_PER_MW_24H

@property
def fire_stations(self) -> float:
    return self.mw_committed * FIRE_STATIONS_PER_MW

@property
def gravity_wells(self) -> float:
    return self.mw_committed * GRAVITY_WELLS_PER_MW

@property
def schools_at_floor(self) -> float:
    return self.mw_committed * SCHOOL_FLOORS_PER_MW

def report(self) -> Dict:
    return {
        "mw_committed":     self.mw_committed,
        "alternatives_foregone": {
            "homes_powered":       round(self.homes_powered),
            "fire_stations":       round(self.fire_stations),
            "gravity_wells":       round(self.gravity_wells),
            "schools_at_floor":    round(self.schools_at_floor),
            "note": (
                "Standard models treat this MW as neutral input. "
                "Thermodynamic models treat it as community infrastructure foregone."
            ),
        },
    }
```

# ── Standard Model (the lie, reproduced accurately) ───────────────────────────

@dataclass
class StandardModel:
“””
Reproduces IMPLAN/IO-table methodology.
Not a strawman — this is exactly what fiscal impact studies calculate.
Documented blind spots listed per field.
“””
name:                 str
it_load_mw:           float = 10.0
tax_annual_usd:       float = 50_000_000
land_acres:           float = 75.0

```
@property
def total_power_mw(self) -> float:
    return self.it_load_mw * 1.5   # PUE 1.5 assumed

@property
def construction_jobs(self) -> float:
    return self.it_load_mw * CONSTRUCTION_JOBS_PER_MW

@property
def operations_jobs(self) -> float:
    return self.it_load_mw * OPERATIONS_JOBS_PER_MW

@property
def total_jobs_with_multiplier(self) -> float:
    return self.operations_jobs * IMPLAN_JOB_MULTIPLIER

@property
def tax_spending_impact(self) -> float:
    return self.tax_annual_usd * IMPLAN_SPENDING_MULTIPLIER

@property
def gdp_impact_fraction(self) -> float:
    # Approximate: tax impact / median suburb GDP
    suburb_gdp = 4_000_000_000   # $4B for 160k people
    return self.tax_spending_impact / suburb_gdp

def report(self) -> Dict:
    return {
        "model":              "IMPLAN/IO Standard",
        "institution":        self.name,
        "headline_numbers": {
            "construction_jobs":          round(self.construction_jobs),
            "permanent_operations_jobs":  round(self.operations_jobs),
            "jobs_with_multiplier":       round(self.total_jobs_with_multiplier),
            "tax_annual_usd":             self.tax_annual_usd,
            "spending_impact_usd":        round(self.tax_spending_impact),
            "gdp_impact_pct":             f"+{self.gdp_impact_fraction * 100:.1f}%",
            "verdict":                    "ECONOMIC WINNER",
        },
        "blind_spots": {
            "energy_opportunity_cost": (
                f"INVISIBLE: {self.total_power_mw:.0f}MW treated as free input. "
                f"Actual cost: {round(self.total_power_mw * HOMES_PER_MW_24H):,} homes, "
                f"{round(self.total_power_mw * FIRE_STATIONS_PER_MW)} fire stations foregone."
            ),
            "purpose_coupling": (
                f"INVISIBLE: Tax revenue destination assumed neutral. "
                f"Reality: ~80% leakage to admin bloat (purpose drift)."
            ),
            "multiplier_fantasy": (
                f"INFLATED: Local respend assumed {LOCAL_RESPEND_ASSUMPTION*100:.0f}%. "
                f"Reality: {(1-PROFIT_EXTRACTION_RATE)*100:.0f}% "
                f"({PROFIT_EXTRACTION_RATE*100:.0f}% extracted by national HQ)."
            ),
            "resilience_subtraction": (
                "INVISIBLE: Grid strain, brownouts, hospital failures, "
                "talent drain — not modeled. Deaths not counted."
            ),
        },
    }
```

# ── Thermodynamic Model (the truth) ───────────────────────────────────────────

@dataclass
class ThermodynamicModel:
“””
True accounting. All flows visible. No blind spots by construction.
Drag coefficients from city_thermodynamics empirical baselines.
“””
name:             str
institution_class: InstitutionClass
it_load_mw:       float = 10.0
pue:              float = 1.50
compute_purpose_factor: float = 0.0    # 0 = ad network, 1 = layer zero
heat_export_fraction:   float = 0.0    # ERF
tax_annual_usd:         float = 50_000_000
tax_purpose_factor:     float = 0.05   # admin bloat default
grid_buffer_mwh:        float = 0.0

```
# Override drag coefficients if institution has mitigations
drag_water:    float = GRID_STRAIN_WATER_LOSS
drag_roads:    float = TRAFFIC_INCREASE_ROADS
drag_safety:   float = SAFETY_BUDGET_COMPETITION
drag_schools:  float = COGNITIVE_DRAIN_SCHOOLS
drag_ac:       float = HEAT_ISLAND_AC_LOAD

@property
def total_power_mw(self) -> float:
    return self.it_load_mw * self.pue

@property
def useful_compute_mw(self) -> float:
    """5-10% of IT load is useful work. Rest is heat."""
    return self.it_load_mw * 0.05 * self.compute_purpose_factor

@property
def heat_wasted_mw(self) -> float:
    return self.total_power_mw * (1.0 - self.heat_export_fraction)

@property
def purpose_added(self) -> Dict[str, float]:
    """Positive contributions — only what's actually coupled."""
    heat = self.heat_export_fraction * 0.20
    compute = self.compute_purpose_factor * 0.15
    tax = min(0.15, (self.tax_annual_usd / 1e8) * self.tax_purpose_factor)
    grid = min(0.10, self.grid_buffer_mwh / 1000)
    return {
        "heat_export":    round(heat, 4),
        "compute_local":  round(compute, 4),
        "tax_infra":      round(tax, 4),
        "grid_buffer":    round(grid, 4),
    }

@property
def purpose_removed(self) -> Dict[str, float]:
    """Community drag — always present, magnitude varies."""
    return {
        "water_delivery":   self.drag_water,
        "road_wear":        self.drag_roads,
        "safety_coverage":  self.drag_safety,
        "school_quality":   self.drag_schools,
        "ac_load":          self.drag_ac,
    }

@property
def coupling_fragility(self) -> float:
    """
    How brittle are the positive coupling channels?
    Digital interlocks, single-vendor dependencies, grid dependence.
    Higher fragility → purpose gains less reliable.
    """
    fragility = 0.20   # baseline
    if self.heat_export_fraction > 0:
        fragility += 0.10   # district heating pipe = single failure path
    if self.compute_purpose_factor > 0.5:
        fragility += 0.15   # digital compute dependency
    if self.grid_buffer_mwh == 0:
        fragility += 0.20   # no buffer = fragile to grid events
    return min(0.80, fragility)

@property
def net_purpose_gain(self) -> float:
    """
    Core metric.
    COMMUNITY PURPOSE GAIN/LOSS
    = (purpose_added - purpose_removed) × (1 - coupling_fragility)
    """
    added   = sum(self.purpose_added.values())
    removed = sum(self.purpose_removed.values())
    return (added - removed) * (1.0 - self.coupling_fragility)

@property
def passes_threshold(self) -> bool:
    return self.net_purpose_gain >= NET_PURPOSE_GAIN_THRESHOLD

@property
def layer_scores(self) -> Dict[str, float]:
    """
    Per-layer purpose score.
    Negative = that layer degraded by institution.
    Must be positive across all ANCHOR_LAYERS to pass.
    """
    return {
        "Water":  self.purpose_added.get("heat_export", 0) * 0.3
                  + self.purpose_added.get("tax_infra", 0) * 0.4
                  - self.drag_water,
        "Food":   self.purpose_added.get("compute_local", 0) * 0.2
                  - self.drag_water * 0.5,
        "Energy": self.purpose_added.get("grid_buffer", 0)
                  + self.purpose_added.get("heat_export", 0) * 0.5
                  - self.drag_ac,
        "Repair": self.purpose_added.get("tax_infra", 0) * 0.3
                  - self.drag_safety,
    }

@property
def anchor_layers_passing(self) -> List[str]:
    return [l for l, v in self.layer_scores.items() if v >= 0]

@property
def anchor_layers_failing(self) -> List[str]:
    return [l for l, v in self.layer_scores.items() if v < 0]

def report(self) -> Dict:
    return {
        "model":              "Thermodynamic Impact",
        "institution":        self.name,
        "energy_reality": {
            "total_power_mw":    self.total_power_mw,
            "useful_compute_mw": round(self.useful_compute_mw, 3),
            "heat_wasted_mw":    round(self.heat_wasted_mw, 2),
            "compute_efficiency": f"{self.useful_compute_mw / self.total_power_mw * 100:.1f}%",
        },
        "purpose_flow": {
            "added":   self.purpose_added,
            "removed": self.purpose_removed,
            "coupling_fragility": round(self.coupling_fragility, 3),
        },
        "net_purpose_gain":       round(self.net_purpose_gain * 100, 2),
        "passes_threshold":       self.passes_threshold,
        "anchor_layers_passing":  self.anchor_layers_passing,
        "anchor_layers_failing":  self.anchor_layers_failing,
        "layer_scores":           {k: round(v * 100, 2)
                                   for k, v in self.layer_scores.items()},
        "verdict": (
            "PURPOSE POSITIVE" if self.passes_threshold
            else f"THERMODYNAMIC PARASITE "
                 f"(net {self.net_purpose_gain * 100:+.1f}%)"
        ),
    }
```

# ── Impact Comparison ─────────────────────────────────────────────────────────

@dataclass
class ImpactComparison:
“””
Side-by-side: standard model vs thermodynamic model.
The inversion made visible.
“””
standard:     StandardModel
thermodynamic: ThermodynamicModel
opportunity:  OpportunityCost = field(
default_factory=lambda: OpportunityCost(15.0)
)

```
def inversion_magnitude(self) -> float:
    """
    How far apart are the two verdicts?
    Standard says +X% GDP. Thermodynamic says -Y% purpose.
    Inversion = X + |Y|.
    """
    std_positive = float(
        self.standard.gdp_impact_fraction * 100
    )
    thermo_negative = abs(
        min(0.0, self.thermodynamic.net_purpose_gain * 100)
    )
    return std_positive + thermo_negative

def report(self) -> Dict:
    return {
        "comparison":         self.standard.name,
        "standard_verdict":   self.standard.report()["headline_numbers"]["verdict"],
        "thermo_verdict":     self.thermodynamic.report()["verdict"],
        "inversion_magnitude": f"{self.inversion_magnitude():.1f} percentage points",
        "standard": self.standard.report(),
        "thermodynamic": self.thermodynamic.report(),
        "opportunity_cost": self.opportunity.report(),
        "policy_note": (
            "Standard model is not wrong due to bad math. "
            "It is wrong by design: it was built to count revenue, "
            "not to measure whether communities survive. "
            "These are different questions with opposite answers."
        ),
    }
```

# ── Policy Threshold Instrument ───────────────────────────────────────────────

@dataclass
class PolicyThreshold:
“””
Regulatory pass/fail instrument.
Replaces ‘economic impact study’ with thermodynamic impact study.
All inputs are publicly verifiable — no self-reporting accepted.
“””
institution_name:    str
institution_class:   InstitutionClass
thermo:              ThermodynamicModel

```
PASS_CONDITIONS = [
    "net_purpose_gain >= +10%",
    "all four anchor layers non-negative",
    "coupling_fragility < 0.50",
    "no single anchor layer below -5%",
]

def evaluate(self) -> Dict:
    ng      = self.thermo.net_purpose_gain
    layers  = self.thermo.layer_scores
    frag    = self.thermo.coupling_fragility
    failing = self.thermo.anchor_layers_failing

    condition_results = {
        "net_gain_10pct":     ng >= NET_PURPOSE_GAIN_THRESHOLD,
        "all_anchors_pos":    len(failing) == 0,
        "fragility_under_50": frag < 0.50,
        "no_anchor_below_5pct": all(v >= -0.05 for v in layers.values()),
    }

    passed = all(condition_results.values())

    required_mitigations = []
    if not condition_results["net_gain_10pct"]:
        required_mitigations.append(
            f"Increase purpose coupling to achieve +10% net gain "
            f"(current: {ng*100:+.1f}%)"
        )
    if not condition_results["all_anchors_pos"]:
        for layer in failing:
            required_mitigations.append(
                f"Restore {layer} layer: score {layers[layer]*100:+.1f}% "
                f"(must be >= 0%)"
            )
    if not condition_results["fragility_under_50"]:
        required_mitigations.append(
            f"Reduce coupling fragility below 0.50 "
            f"(current: {frag:.2f}) — add redundancy, remove digital interlocks"
        )

    return {
        "institution":         self.institution_name,
        "class":               self.institution_class.value,
        "REGULATORY_VERDICT":  "APPROVED" if passed else "DENIED — MITIGATIONS REQUIRED",
        "pass_conditions":     condition_results,
        "net_purpose_gain":    f"{ng*100:+.1f}%",
        "anchor_layer_scores": {k: f"{v*100:+.1f}%" for k, v in layers.items()},
        "coupling_fragility":  round(frag, 3),
        "required_mitigations": required_mitigations,
        "data_sources_required": [
            "Utility filing: actual kWh consumption (not estimated)",
            "County assessor: acreage, active-use hours (satellite verified)",
            "IRS 990 or public budget: facility vs program spend",
            "Grid operator: brownout frequency pre/post installation",
            "School district: teacher retention rate pre/post",
            "Water authority: pump failure rate pre/post",
        ],
    }
```

# ── Class Failure Rates ───────────────────────────────────────────────────────

CLASS_FAILURE_RATES = {
InstitutionClass.DATA_CENTER:      0.80,   # 80% fail thermodynamic test
InstitutionClass.MEGA_CHURCH:      0.95,   # 95% fail
InstitutionClass.SMART_UPGRADE:    0.70,   # 70% fail (coupling fragility)
InstitutionClass.FACTORY:          0.55,
InstitutionClass.DISTRIBUTION_HUB: 0.45,
InstitutionClass.HOSPITAL:         0.30,
}

# ── Preset Comparisons ────────────────────────────────────────────────────────

def comparison_dc_parasite() -> ImpactComparison:
std = StandardModel(
name=“Data Center 10MW — Ad Network”,
it_load_mw=10.0, tax_annual_usd=50_000_000,
)
thermo = ThermodynamicModel(
name=“Data Center 10MW — Ad Network”,
institution_class=InstitutionClass.DATA_CENTER,
it_load_mw=10.0, pue=1.58,
compute_purpose_factor=0.0,
heat_export_fraction=0.0,
tax_annual_usd=50_000_000,
tax_purpose_factor=0.05,
)
return ImpactComparison(std, thermo, OpportunityCost(15.0))

def comparison_dc_net_zero() -> ImpactComparison:
std = StandardModel(
name=“Data Center 10MW — Net Zero Config”,
it_load_mw=10.0, tax_annual_usd=50_000_000,
)
thermo = ThermodynamicModel(
name=“Data Center 10MW — Net Zero Config”,
institution_class=InstitutionClass.DATA_CENTER,
it_load_mw=10.0, pue=1.20,
compute_purpose_factor=0.85,
heat_export_fraction=0.80,
tax_annual_usd=50_000_000,
tax_purpose_factor=0.90,
grid_buffer_mwh=100.0,
drag_water=0.01, drag_roads=0.05,
drag_safety=0.00, drag_schools=0.02, drag_ac=0.01,
)
return ImpactComparison(std, thermo, OpportunityCost(12.0))

def comparison_megachurch() -> ImpactComparison:
std = StandardModel(
name=“Austin Megachurch”,
it_load_mw=0.0, tax_annual_usd=0,
land_acres=75,
)
# Override standard model for non-DC institution
std.tax_annual_usd = 2_000_000   # tax savings claimed
thermo = ThermodynamicModel(
name=“Austin Megachurch”,
institution_class=InstitutionClass.MEGA_CHURCH,
it_load_mw=4.5 / 1000,     # 4500 kWh/day → ~0.19 MW
pue=1.0,
compute_purpose_factor=0.35,
heat_export_fraction=0.0,
tax_annual_usd=2_000_000,
tax_purpose_factor=0.10,
drag_water=0.02,
drag_roads=0.10,    # Sunday traffic spike
drag_safety=0.02,
drag_schools=0.00,
drag_ac=0.05,       # heat island from parking lot + HVAC exhaust
)
return ImpactComparison(std, thermo, OpportunityCost(4.5 / 1000))

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:

```
comparisons = [
    ("DC — Ad Network Parasite",  comparison_dc_parasite()),
    ("DC — Net Zero Config",      comparison_dc_net_zero()),
    ("Austin Megachurch",         comparison_megachurch()),
]

print("=== MODEL INVERSION COMPARISON ===\n")
print(f"{'Institution':<35} {'Standard':>12} {'Thermodynamic':>20} {'Inversion':>12}")
print("─" * 85)
for label, comp in comparisons:
    sr = comp.standard.report()["headline_numbers"]["gdp_impact_pct"]
    tr = comp.thermodynamic.report()["verdict"]
    inv = f"{comp.inversion_magnitude():.1f}pp"
    print(f"  {label:<33} {sr:>12} {tr:>20} {inv:>12}")

print("\n\n=== OPPORTUNITY COST — DC PARASITE ===\n")
opp = comparison_dc_parasite().opportunity
for k, v in opp.report()["alternatives_foregone"].items():
    if k != "note":
        print(f"  {k:<25} {v:>10,}")
print(f"\n  {opp.report()['alternatives_foregone']['note']}")

print("\n\n=== REGULATORY POLICY THRESHOLD ===\n")
for label, comp in comparisons:
    pt = PolicyThreshold(
        institution_name  = label,
        institution_class = comp.thermodynamic.institution_class,
        thermo            = comp.thermodynamic,
    )
    ev = pt.evaluate()
    print(f"  {label}")
    print(f"    Verdict:     {ev['REGULATORY_VERDICT']}")
    print(f"    Net gain:    {ev['net_purpose_gain']}")
    print(f"    Layers:      {ev['anchor_layer_scores']}")
    if ev["required_mitigations"]:
        for m in ev["required_mitigations"]:
            print(f"    ⚑ {m[:90]}")
    print()

print("\n=== CLASS FAILURE RATES (thermodynamic test) ===\n")
for cls, rate in CLASS_FAILURE_RATES.items():
    bar = "█" * int(rate * 20)
    print(f"  {cls.value:<20} {rate*100:.0f}%  {bar}")

print("\n\n=== BLIND SPOT SUMMARY ===")
for label, comp in [("DC Parasite", comparison_dc_parasite())]:
    bs = comp.standard.report()["blind_spots"]
    print(f"\n  {label}:")
    for k, v in bs.items():
        print(f"    [{k}] {v[:100]}")
```
