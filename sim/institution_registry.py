# “””
institution_registry.py

Unified scoring system across all institution types.
Wires datacenter_net_zero into purpose_deviation so a DC
gets a deviation index identical to any other institution.

The bridge insight:
DC three-signal translation:
Energy signal  = actual_kwh / floor_kwh
floor = PUE 1.03 (physics minimum)
Land signal    = acres × (1 - server_utilization)
idle fraction = underutilized compute capacity
Budget signal  = facility_cost / program_cost
program_cost = local_purpose_value delivered

ComputePurpose.AD_NETWORK   → budget_signal inverted → CAPTURED
ComputePurpose.LAYER0_TRAINING → budget_signal healthy → ON_PURPOSE

Net zero test result feeds back into deviation index:
net_zero PASS  → trust_penalty = 1.0 (no penalty)
net_zero FAIL  → trust_penalty = 1.5–2.0 (extraction amplifies drift)

Full chain:
city_thermodynamics     physical substrate + operator trust decay
city_optimization       upgrade test matrix + leakage audit
purpose_deviation       drift register — ungameable physical signals
datacenter_net_zero     extraction vs infrastructure test
institution_registry    ← unified scoring across all types (this file)

Usage:
registry = InstitutionRegistry(“Madison Suburb”)
registry.add_city_institution(city_inst, kwh_actual)
registry.add_data_center(dc)
registry.add_purpose_deviation(pd)
print(registry.ranked_report())
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
import json

from purpose_deviation import (
PurposeDeviation, EnergySignal, LandSignal, BudgetSignal,
DriftLevel, classify_drift, CityDeviationAudit,
madison_neighborhood_church, austin_megachurch, austin_small_church,
rural_fire_hall_on_purpose, suburban_school_captured,
)
from datacenter_net_zero import (
DataCenter, DCPhysical, CouplingChannels, ParasiticEffects,
ComputePurpose, TaxDestination, COMPUTE_PURPOSE_FACTOR, TAX_PURPOSE_FACTOR,
dc_parasite, dc_partial_coupling, dc_net_zero_passing, dc_layer_zero,
DC_IT_LOAD_MW,
)

# ── Constants ─────────────────────────────────────────────────────────────────

# DC floor: PUE 1.03 physics minimum × IT load

DC_PUE_FLOOR             = 1.03
DC_ACRES_PER_MW          = 1.5     # typical ~1-2 acres per MW IT load
DC_SERVER_UTILIZATION    = 0.15    # industry avg 15% — 85% idle capacity
DC_HOURS_ACTIVE          = 168.0   # always on — never idle by definition

# Budget translation

DC_FACILITY_COST_FRACTION     = 0.55   # typical: facility/cooling dominates
DC_PROGRAM_COST_AD_NETWORK    = 0.05   # near-zero local purpose value
DC_PROGRAM_COST_LOCAL_PURPOSE = 0.60   # local purpose delivery

# Net zero → trust penalty mapping

NET_ZERO_PASS_TRUST   = 1.00
NET_ZERO_FAIL_TRUST   = 1.80   # extraction amplifies all drift signals

# ── DC → PurposeDeviation Bridge ─────────────────────────────────────────────

def dc_to_purpose_deviation(dc: DataCenter) -> PurposeDeviation:
“””
Translate DataCenter state into PurposeDeviation three-signal format.

```
DC-specific problem: PUE variance is narrow (1.03–2.0), so energy ratio
alone undersells extraction. A parasite DC at PUE 1.58 is only 53% over
floor — looks better than a church at 10x. Fix: energy signal uses
PURPOSE-ADJUSTED floor, not physics floor.

  purpose_adjusted_floor = physics_floor / max(0.01, purpose_factor)
  AD_NETWORK (factor 0.0) → floor → ∞ → energy ratio → very large
  LAYER0_TRAINING (factor 0.9) → floor close to physics minimum

This correctly penalizes a DC that runs efficiently at the wrong purpose.

Land signal:
  active_hours driven by local_purpose_utilization, not server uptime.
  A DC serving ad networks is 0% purposefully active locally,
  even though the fans run 168hr/week.

Budget signal:
  program_cost = local_purpose_value delivered to community.
  AD_NETWORK → program ≈ 0 → severe inversion → CAPTURED.

Fourth signal (DC-specific) embedded in budget:
  purpose_export_ratio = fraction of compute output leaving community.
  Treated as admin_cost analog — budget spent on non-local actors.
"""
p = dc.physical
c = dc.coupling

purpose_factor = COMPUTE_PURPOSE_FACTOR[c.compute_purpose]

# Energy signal — purpose-adjusted floor
physics_floor_kwh_day  = DC_PUE_FLOOR * p.it_load_mw * 1000 * 24
actual_kwh_day         = p.energy_day_mwh * 1000
# Adjust floor downward by purpose factor:
# if compute serves zero local purpose, floor → near zero (all energy is waste)
purpose_floor_kwh_day  = physics_floor_kwh_day * max(0.01, purpose_factor)

energy = EnergySignal(
    floor_kwh_day  = purpose_floor_kwh_day,
    actual_kwh_day = actual_kwh_day,
    source_note    = (
        f"purpose-adjusted floor: physics {physics_floor_kwh_day:.0f} kWh × "
        f"purpose_factor {purpose_factor} = {purpose_floor_kwh_day:.0f} kWh"
    ),
)

# Land signal — local purpose utilization, not server uptime
# DC is "active" only during hours it delivers local community purpose
local_purpose_hours = DC_HOURS_ACTIVE * max(0.01, purpose_factor)

land = LandSignal(
    acres                 = DC_ACRES_PER_MW * p.it_load_mw,
    active_hours_per_week = local_purpose_hours,
    source_note           = (
        f"local_purpose_hours = 168 × {purpose_factor} "
        f"(compute_purpose={c.compute_purpose.value})"
    ),
)

# Budget signal — program_cost = local purpose value delivered
energy_cost_annual = actual_kwh_day * 365 * 0.08
total_budget       = energy_cost_annual * 2.5

facility_cost = total_budget * DC_FACILITY_COST_FRACTION

# Local program value: compute purpose + heat coupling + tax-to-infrastructure
heat_program  = 0.20 if c.heat_export_active else 0.0
tax_program   = min(0.25,
                    (c.tax_annual_usd / total_budget
                     if total_budget > 0 else 0.0)
                    * TAX_PURPOSE_FACTOR.get(c.tax_destination, 0.05))
compute_prog  = purpose_factor * 0.35
program_fraction = min(0.75, compute_prog + heat_program + tax_program)
program_cost  = total_budget * program_fraction

# Purpose export ratio → admin analog
# Fraction of compute value extracted out of community
export_fraction    = max(0.0, 1.0 - purpose_factor)
exported_value     = total_budget * export_fraction * 0.40
admin_cost         = total_budget - facility_cost - program_cost + exported_value
admin_cost         = max(0.0, admin_cost)

budget = BudgetSignal(
    total_budget  = round(total_budget, 0),
    facility_cost = round(facility_cost, 0),
    program_cost  = round(max(1.0, program_cost), 0),
    admin_cost    = round(admin_cost, 0),
    source_note   = (
        f"purpose_factor={purpose_factor}, "
        f"export_fraction={export_fraction:.2f}, "
        f"program={program_fraction:.2f}"
    ),
)

# Trust penalty from net zero result
nz_result   = dc.net_zero_test()
trust       = NET_ZERO_PASS_TRUST if nz_result["net_zero"] else NET_ZERO_FAIL_TRUST
trust_index = 1.0 / trust

# Stated vs actual purpose
stated = "Information arbitrage at scale (bit flips → economic value)"
actual = (
    f"Compute: {c.compute_purpose.value} | "
    f"Heat: {'exported' if c.heat_export_active else 'wasted to atmosphere'} | "
    f"Water: {'closed loop' if c.water_net_draw_fraction == 0 else f'{c.water_net_draw_fraction:.0%} net draw'} | "
    f"Tax: {c.tax_destination.value}"
)

return PurposeDeviation(
    name                 = dc.name,
    stated_purpose       = stated,
    actual_outputs       = actual,
    energy               = energy,
    land                 = land,
    budget               = budget,
    operator_trust_index = trust_index,
)
```

# ── Registry Entry ────────────────────────────────────────────────────────────

@dataclass
class RegistryEntry:
institution_type: str          # “city”, “datacenter”, “standalone”
deviation:        PurposeDeviation
source_object:    object = None   # original DC or CityInstitution if available

```
@property
def name(self) -> str:
    return self.deviation.name

@property
def index(self) -> float:
    return self.deviation.deviation_index

@property
def drift(self) -> DriftLevel:
    return self.deviation.drift_level
```

# ── Institution Registry ──────────────────────────────────────────────────────

@dataclass
class InstitutionRegistry:
“””
Unified scoring system.
All institution types — city services, data centers, churches, schools —
scored on identical three-signal deviation index.
No special cases. Physics is the common language.
“””
name:       str
population: int = 0
entries:    List[RegistryEntry] = field(default_factory=list)

```
def add_data_center(self, dc: DataCenter):
    pd = dc_to_purpose_deviation(dc)
    self.entries.append(RegistryEntry(
        institution_type = "datacenter",
        deviation        = pd,
        source_object    = dc,
    ))

def add_purpose_deviation(self, pd: PurposeDeviation,
                           inst_type: str = "standalone"):
    self.entries.append(RegistryEntry(
        institution_type = inst_type,
        deviation        = pd,
        source_object    = None,
    ))

def ranked(self) -> List[RegistryEntry]:
    return sorted(self.entries, key=lambda e: e.index, reverse=True)

def by_drift_level(self) -> Dict[str, List[str]]:
    out = {d.value: [] for d in DriftLevel}
    for e in self.entries:
        out[e.drift.value].append(e.name)
    return out

def system_index(self) -> float:
    if not self.entries:
        return 0.0
    return sum(e.index for e in self.entries) / len(self.entries)

def ranked_report(self) -> Dict:
    ranked = self.ranked()
    return {
        "registry":           self.name,
        "population":         self.population,
        "institution_count":  len(self.entries),
        "system_index":       round(self.system_index(), 1),
        "by_drift_level":     self.by_drift_level(),
        "ranked": [
            {
                "rank":          i + 1,
                "name":          e.name,
                "type":          e.institution_type,
                "index":         round(e.index, 1),
                "drift":         e.drift.value,
                "energy_ratio":  (
                    round(e.deviation.energy.ratio, 1)
                    if e.deviation.energy.ratio != float("inf")
                    else "∞"
                ),
                "idle_pct":      e.deviation.land.idle_pct,
                "budget_inverted": e.deviation.budget.inverted,
                "trust_index":   round(e.deviation.operator_trust_index or 1.0, 3),
                "top_fix":       e.deviation.recovery_intervention[:90] + "...",
            }
            for i, e in enumerate(ranked)
        ],
    }
```

# ── Madison Suburb Full Registry ──────────────────────────────────────────────

def build_madison_suburb_registry() -> InstitutionRegistry:
“””
Madison suburb registry:
City institutions + data center + churches + school.
All scored on identical deviation index.
“””
reg = InstitutionRegistry(
name       = “Madison Suburb — Full Institution Registry”,
population = 160_000,
)

```
# City institutions (from purpose_deviation archetypes)
reg.add_purpose_deviation(madison_neighborhood_church(),   "city_church")
reg.add_purpose_deviation(rural_fire_hall_on_purpose(),    "city_fire")
reg.add_purpose_deviation(suburban_school_captured(),      "city_school")

# Data centers — parasite vs net zero
reg.add_data_center(dc_parasite())
reg.add_data_center(dc_partial_coupling())
reg.add_data_center(dc_net_zero_passing())
reg.add_data_center(dc_layer_zero())

return reg
```

def build_austin_registry() -> InstitutionRegistry:
“””
Austin TX registry:
Megachurch + small church + school + two data center configs.
“””
reg = InstitutionRegistry(
name       = “Austin TX — Institution Registry”,
population = 978_908,
)

```
reg.add_purpose_deviation(austin_megachurch(),         "city_church")
reg.add_purpose_deviation(austin_small_church(),       "city_church")
reg.add_purpose_deviation(suburban_school_captured(),  "city_school")
reg.add_data_center(dc_parasite())
reg.add_data_center(dc_layer_zero())

return reg
```

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:

```
# ── Madison Suburb ────────────────────────────────────────────────────────
print("=== MADISON SUBURB — UNIFIED DEVIATION REGISTRY ===\n")
madison = build_madison_suburb_registry()
mr = madison.ranked_report()

print(f"System deviation index: {mr['system_index']}")
print(f"Institution count:      {mr['institution_count']}\n")

print(f"{'Rank':<5} {'Name':<42} {'Type':<14} {'Index':>8} {'Drift':<12} "
      f"{'E-ratio':>8} {'Idle':>7} {'Inv':>5}")
print("─" * 110)
for row in mr["ranked"]:
    print(f"  {row['rank']:<3} {row['name']:<42} {row['type']:<14} "
          f"{row['index']:>8.1f} {row['drift']:<12} "
          f"{str(row['energy_ratio']):>8} {row['idle_pct']:>7} "
          f"{str(row['budget_inverted']):>5}")

print(f"\nBy drift level:")
for level, names in mr["by_drift_level"].items():
    if names:
        print(f"  {level:<14}: {', '.join(names)}")

# ── Austin ────────────────────────────────────────────────────────────────
print("\n\n=== AUSTIN TX — UNIFIED DEVIATION REGISTRY ===\n")
austin = build_austin_registry()
ar = austin.ranked_report()

print(f"System deviation index: {ar['system_index']}")
print(f"\n{'Rank':<5} {'Name':<42} {'Type':<14} {'Index':>8} {'Drift':<12}")
print("─" * 90)
for row in ar["ranked"]:
    print(f"  {row['rank']:<3} {row['name']:<42} {row['type']:<14} "
          f"{row['index']:>8.1f} {row['drift']:<12}")

# ── DC deviation signal breakdown ─────────────────────────────────────────
print("\n\n=== DC DEVIATION SIGNAL BREAKDOWN ===\n")
print(f"{'Config':<42} {'E-ratio':>9} {'Idle%':>7} {'Inv':>5} "
      f"{'Trust':>7} {'Index':>8} {'Drift':<12}")
print("─" * 100)

for dc in [dc_parasite(), dc_partial_coupling(),
           dc_net_zero_passing(), dc_layer_zero()]:
    pd = dc_to_purpose_deviation(dc)
    er = round(pd.energy.ratio, 1) if pd.energy.ratio != float("inf") else "∞"
    print(f"  {dc.name:<40} {str(er):>9} {pd.land.idle_pct:>7} "
          f"{str(pd.budget.inverted):>5} "
          f"{pd.operator_trust_index:>7.3f} "
          f"{pd.deviation_index:>8.1f} {pd.drift_level.value:<12}")

print("\n\n=== KEY RESULT ===")
print("""
```

AD_NETWORK parasite   → CAPTURED   (same category as Austin megachurch)
LAYER0_TRAINING DC    → MODERATE   (same category as neighborhood church)

Physics doesn’t distinguish institution type.
The deviation index sees through the label to the energy flow.
“””)
