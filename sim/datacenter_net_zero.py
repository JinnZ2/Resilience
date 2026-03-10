# “””
datacenter_net_zero.py

Data center as thermodynamic institution.
Tests whether a data center achieves net zero community impact
or functions as a pure extraction parasite.

Core claim:
Data center is net zero IFF it functions as missing Layer Zero
infrastructure: heat pump + water cycle + decision accelerator.
Pure compute extraction = thermodynamic parasite.

Architecture:
DataCenter
├── physical (PUE, WUE, IT load)
├── five coupling channels (heat / water / compute / grid / tax)
└── net_zero_test() → CommunityImpact

Community
├── baseline (institutions from city_thermodynamics)
├── pre/post energy + purpose accounting
└── resilience_delta()

NetZeroTest
├── MUST ACHIEVE: purpose_post >= purpose_pre
│               energy_post  <= energy_pre
├── failure_modes (99% real DCs)
└── passing_config (example)

Efficiency reality:
DC useful work / total energy in = 5-10%
90%+ lost to heat irreversibly
Waste heat IS the dominant output — must be redirected or it’s pure loss

Integration: imports city_thermodynamics, city_optimization, purpose_deviation
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json

# ── Try sibling imports ───────────────────────────────────────────────────────

try:
from city_thermodynamics import CityInstitution, City, build_city_1000, EnergyMode
from city_optimization import InstitutionLeakage, leakage_summary
from purpose_deviation import PurposeDeviation, EnergySignal, LandSignal, BudgetSignal
_SIBLINGS = True
except ImportError:
_SIBLINGS = False

# ── Constants ─────────────────────────────────────────────────────────────────

PUE_PHYSICS_FLOOR    = 1.03   # theoretical minimum (cooling + distribution)
PUE_BEST_PRACTICE    = 1.20   # hyperscaler best case
PUE_INDUSTRY_AVG     = 1.58   # real-world average
WUE_CLOSED_LOOP      = 0.0    # no net water draw (achieved with air/closed systems)
WUE_INDUSTRY_AVG     = 1.80   # L/kWh industry average
ERF_PARASITE         = 0.0    # all heat to atmosphere
ERF_NET_ZERO_MIN     = 0.50   # minimum to offset community heating load
ERF_EXCELLENT        = 0.80   # replaces gas boilers entirely

# Community baseline (Madison suburb, 160k people)

COMMUNITY_POPULATION         = 160_000
COMMUNITY_KWH_PER_PERSON_DAY = 25.0
COMMUNITY_ENERGY_DAY_MWH     = COMMUNITY_POPULATION * COMMUNITY_KWH_PER_PERSON_DAY / 1000  # 4000 MWh/day

# Data center reference: 10MW IT load

DC_IT_LOAD_MW        = 10.0

# Net zero hard test

NET_ZERO_PURPOSE_FLOOR = 1.00   # purpose_post / purpose_pre >= 1.0
NET_ZERO_ENERGY_CEIL   = 1.00   # energy_post  / energy_pre  <= 1.0

# ── Enums ─────────────────────────────────────────────────────────────────────

class ComputePurpose(Enum):
“”“What the compute actually does — determines local purpose contribution.”””
AD_NETWORK          = “ad_network”           # zero local purpose
FINANCIAL_HFT       = “financial_hft”        # zero local purpose
CRYPTO_MINING       = “crypto_mining”        # negative (pure heat)
TRAFFIC_OPTIMIZATION = “traffic_optimization” # replaces 1k signals, saves energy
PRECISION_AG        = “precision_ag”         # doubles rural food output
LAYER0_TRAINING     = “layer0_training”      # teaches 10k pump repairs/yr
GRID_MANAGEMENT     = “grid_management”      # stabilizes regional grid
MEDICAL_TRIAGE      = “medical_triage”       # extends rural clinic reach
MIXED_LOCAL         = “mixed_local”          # partial local benefit

# Local purpose multiplier: how much of compute output serves community

COMPUTE_PURPOSE_FACTOR = {
ComputePurpose.AD_NETWORK:           0.00,
ComputePurpose.FINANCIAL_HFT:        0.00,
ComputePurpose.CRYPTO_MINING:       -0.05,   # heat island, grid strain, no output
ComputePurpose.TRAFFIC_OPTIMIZATION: 0.85,
ComputePurpose.PRECISION_AG:         0.80,
ComputePurpose.LAYER0_TRAINING:      0.90,
ComputePurpose.GRID_MANAGEMENT:      0.95,
ComputePurpose.MEDICAL_TRIAGE:       0.75,
ComputePurpose.MIXED_LOCAL:          0.40,
}

class TaxDestination(Enum):
ADMIN_BLOAT         = “admin_bloat”          # purpose drift — feeds bureaucracy
GRAVITY_WELLS       = “gravity_wells”        # Water purpose +100%
FIRE_STATIONS       = “fire_stations”        # Fire purpose, floor tech
SCHOOL_RETROFIT     = “school_retrofit”      # School to 10kWh/day floor
INFRASTRUCTURE_MIX  = “infrastructure_mix”   # split across actual needs

TAX_PURPOSE_FACTOR = {
TaxDestination.ADMIN_BLOAT:        0.05,
TaxDestination.GRAVITY_WELLS:      0.90,
TaxDestination.FIRE_STATIONS:      0.85,
TaxDestination.SCHOOL_RETROFIT:    0.75,
TaxDestination.INFRASTRUCTURE_MIX: 0.65,
}

# ── Physical Parameters ───────────────────────────────────────────────────────

@dataclass
class DCPhysical:
“””
Raw thermodynamic parameters.
PUE: Power Usage Effectiveness = total_facility / it_load
WUE: Water Usage Effectiveness = L/kWh IT load
ERF: Energy Reuse Factor = heat exported / heat generated
“””
it_load_mw:     float = DC_IT_LOAD_MW
pue:            float = PUE_INDUSTRY_AVG
wue:            float = WUE_INDUSTRY_AVG
erf:            float = ERF_PARASITE

```
@property
def total_power_mw(self) -> float:
    return self.it_load_mw * self.pue

@property
def overhead_mw(self) -> float:
    """Power consumed by cooling, network, lighting — not compute."""
    return self.total_power_mw - self.it_load_mw

@property
def energy_day_mwh(self) -> float:
    return self.total_power_mw * 24

@property
def heat_generated_mw(self) -> float:
    """All IT power becomes heat. Physics floor."""
    return self.total_power_mw   # 100% conversion to waste heat

@property
def heat_exported_mw(self) -> float:
    """Fraction captured for district heating."""
    return self.heat_generated_mw * self.erf

@property
def heat_wasted_mw(self) -> float:
    """Heat exhausted to atmosphere — pure thermodynamic loss."""
    return self.heat_generated_mw * (1.0 - self.erf)

@property
def water_day_liters(self) -> float:
    return self.wue * self.it_load_mw * 1000 * 24   # L/kWh × kWh/day

@property
def compute_efficiency(self) -> float:
    """Useful computation / total energy. Physics reality: 5-10%."""
    return self.it_load_mw / self.total_power_mw * 0.10   # 10% of IT is useful work

def report(self) -> Dict:
    return {
        "it_load_mw":           self.it_load_mw,
        "total_power_mw":       round(self.total_power_mw, 2),
        "overhead_mw":          round(self.overhead_mw, 2),
        "pue":                  self.pue,
        "wue":                  self.wue,
        "erf":                  self.erf,
        "energy_day_mwh":       round(self.energy_day_mwh, 1),
        "heat_generated_mw":    round(self.heat_generated_mw, 2),
        "heat_exported_mw":     round(self.heat_exported_mw, 2),
        "heat_wasted_mw":       round(self.heat_wasted_mw, 2),
        "water_day_liters":     round(self.water_day_liters, 0),
        "compute_efficiency":   f"{self.compute_efficiency * 100:.1f}%",
    }
```

# ── Coupling Channels ─────────────────────────────────────────────────────────

@dataclass
class CouplingChannels:
“””
Five channels through which DC can deliver community purpose.
Each has a realized_fraction (0.0–1.0) — how much potential is captured.
Default = parasite configuration (all zero).
“””
# 1. Heat export → district heating
heat_export_active:         bool  = False
heat_homes_served:          int   = 0       # homes on district heat loop
heat_replaces_gas_mw:       float = 0.0     # equivalent gas displaced

```
# 2. Water cooling → aquifer recharge or agriculture
water_recharge_active:      bool  = False
water_acres_irrigated:      float = 0.0
water_net_draw_fraction:    float = 1.0     # 1.0 = full draw, 0.0 = closed loop

# 3. Compute → local purpose
compute_purpose:            ComputePurpose = ComputePurpose.AD_NETWORK
compute_energy_saved_mwh:   float = 0.0     # energy saved elsewhere by compute

# 4. Grid stabilization
grid_battery_mwh:           float = 0.0     # installed buffer capacity
grid_black_start:           bool  = False

# 5. Tax → direct infrastructure
tax_annual_usd:             float = 0.0
tax_destination:            TaxDestination = TaxDestination.ADMIN_BLOAT

@property
def compute_purpose_factor(self) -> float:
    return COMPUTE_PURPOSE_FACTOR[self.compute_purpose]

@property
def tax_purpose_factor(self) -> float:
    return TAX_PURPOSE_FACTOR[self.tax_destination]

@property
def tax_daily_infrastructure_usd(self) -> float:
    return (self.tax_annual_usd * self.tax_purpose_factor) / 365
```

# ── Negative Coupling (parasitic effects) ─────────────────────────────────────

@dataclass
class ParasiticEffects:
“””
Negative couplings — always present to some degree.
Real data centers generate all of these.
Quantified as fractional degradation of community purpose.
“””
grid_strain_water_pump_loss:  float = 0.10   # -10% H2O delivery
heat_island_ac_increase:      float = 0.05   # +5% building AC load
property_tax_capture_safety:  float = 0.02   # -2% fire/police response
talent_drain_school:          float = 0.05   # -5% skill output

```
@property
def total_community_purpose_loss(self) -> float:
    return (self.grid_strain_water_pump_loss
            + self.heat_island_ac_increase
            + self.property_tax_capture_safety
            + self.talent_drain_school)

@property
def total_energy_increase(self) -> float:
    """Additional community energy from AC increase."""
    return self.heat_island_ac_increase
```

# ── Data Center ───────────────────────────────────────────────────────────────

@dataclass
class DataCenter:
“””
Data center as thermodynamic institution.
Net zero test: does it deliver >= community purpose it displaces?
“””
name:      str
physical:  DCPhysical           = field(default_factory=DCPhysical)
coupling:  CouplingChannels     = field(default_factory=CouplingChannels)
parasitic: ParasiticEffects     = field(default_factory=ParasiticEffects)

```
# Community context
community_energy_day_mwh:   float = COMMUNITY_ENERGY_DAY_MWH
community_population:       int   = COMMUNITY_POPULATION

@property
def dc_fraction_of_community(self) -> float:
    return self.physical.energy_day_mwh / self.community_energy_day_mwh

# ── Purpose accounting ────────────────────────────────────────────────────

def purpose_added(self) -> Dict[str, float]:
    """
    Positive purpose contributions from each coupling channel.
    Normalized to fraction of community baseline.
    """
    heat_contribution = (
        self.physical.heat_exported_mw / self.physical.total_power_mw
        if self.coupling.heat_export_active else 0.0
    )
    water_contribution = (
        (1.0 - self.coupling.water_net_draw_fraction) * 0.15
        if self.coupling.water_recharge_active else 0.0
    )
    compute_contribution = (
        self.coupling.compute_purpose_factor
        * (self.coupling.compute_energy_saved_mwh / self.community_energy_day_mwh)
    )
    grid_contribution = (
        min(0.10, self.coupling.grid_battery_mwh / (self.community_energy_day_mwh * 0.1))
        if self.coupling.grid_battery_mwh > 0 else 0.0
    )
    tax_contribution = (
        min(0.15, self.coupling.tax_daily_infrastructure_usd / 500_000)
    )
    return {
        "heat_export":     round(heat_contribution, 4),
        "water_recharge":  round(water_contribution, 4),
        "compute_purpose": round(compute_contribution, 4),
        "grid_stability":  round(grid_contribution, 4),
        "tax_infrastructure": round(tax_contribution, 4),
    }

def purpose_removed(self) -> Dict[str, float]:
    """Negative purpose from parasitic effects."""
    return {
        "grid_strain_water":    self.parasitic.grid_strain_water_pump_loss,
        "heat_island_ac":       self.parasitic.heat_island_ac_increase,
        "tax_capture_safety":   self.parasitic.property_tax_capture_safety,
        "talent_drain_school":  self.parasitic.talent_drain_school,
    }

def net_purpose_delta(self) -> float:
    """
    Net fractional change in community purpose.
    Positive = community better off. Negative = parasite.
    """
    added   = sum(self.purpose_added().values())
    removed = sum(self.purpose_removed().values())
    return added - removed

def net_energy_delta_mwh(self) -> float:
    """
    Net community energy change.
    DC draw + AC increase - compute savings - heat displacement.
    """
    dc_draw     = self.physical.energy_day_mwh
    ac_increase = self.community_energy_day_mwh * self.parasitic.heat_island_ac_increase
    compute_saved = self.coupling.compute_energy_saved_mwh
    heat_displaced = self.physical.heat_exported_mw * 24 * 0.9  # gas COP ~0.9 displaced
    return dc_draw + ac_increase - compute_saved - heat_displaced

# ── Net Zero Test ─────────────────────────────────────────────────────────

def net_zero_test(self) -> Dict:
    """
    Hard test. Both conditions must hold:
      purpose_post >= purpose_pre  (net_purpose_delta >= 0)
      energy_post  <= energy_pre   (net_energy_delta <= 0)
    """
    purpose_delta = self.net_purpose_delta()
    energy_delta  = self.net_energy_delta_mwh()

    purpose_pass = purpose_delta >= 0.0
    energy_pass  = energy_delta  <= 0.0
    net_zero     = purpose_pass and energy_pass

    # Failure mode classification
    if not net_zero:
        if self.coupling.compute_purpose == ComputePurpose.AD_NETWORK:
            failure = "compute_extraction — zero local purpose"
        elif self.physical.erf == 0.0:
            failure = "heat_parasite — 100% waste heat to atmosphere"
        elif self.coupling.tax_destination == TaxDestination.ADMIN_BLOAT:
            failure = "tax_capture — revenue feeds bureaucracy not infrastructure"
        else:
            failure = "partial_coupling — channels present but insufficient"
    else:
        failure = None

    return {
        "net_zero":           net_zero,
        "purpose_pass":       purpose_pass,
        "energy_pass":        energy_pass,
        "purpose_delta":      round(purpose_delta * 100, 2),   # as %
        "energy_delta_mwh":   round(energy_delta, 1),
        "dc_pct_of_community": round(self.dc_fraction_of_community * 100, 2),
        "failure_mode":       failure,
        "purpose_added":      self.purpose_added(),
        "purpose_removed":    self.purpose_removed(),
    }

def report(self) -> Dict:
    return {
        "name":       self.name,
        "physical":   self.physical.report(),
        "net_zero":   self.net_zero_test(),
        "coupling": {
            "heat_export_active":       self.coupling.heat_export_active,
            "heat_homes_served":        self.coupling.heat_homes_served,
            "water_recharge_active":    self.coupling.water_recharge_active,
            "water_acres_irrigated":    self.coupling.water_acres_irrigated,
            "compute_purpose":          self.coupling.compute_purpose.value,
            "compute_energy_saved_mwh": self.coupling.compute_energy_saved_mwh,
            "grid_battery_mwh":         self.coupling.grid_battery_mwh,
            "tax_annual_usd":           self.coupling.tax_annual_usd,
            "tax_destination":          self.coupling.tax_destination.value,
        },
    }
```

# ── Preset Configurations ─────────────────────────────────────────────────────

def dc_parasite() -> DataCenter:
“””
99% real data center configuration.
Heat to atmosphere, compute serves ad networks, tax to admin.
“””
return DataCenter(
name     = “Typical DC — Extraction Parasite”,
physical = DCPhysical(
it_load_mw = DC_IT_LOAD_MW,
pue        = 1.58,
wue        = 1.80,
erf        = 0.0,
),
coupling = CouplingChannels(
heat_export_active   = False,
water_recharge_active= False,
compute_purpose      = ComputePurpose.AD_NETWORK,
compute_energy_saved_mwh = 0.0,
grid_battery_mwh     = 0.0,
tax_annual_usd       = 2_000_000,
tax_destination      = TaxDestination.ADMIN_BLOAT,
),
parasitic = ParasiticEffects(
grid_strain_water_pump_loss = 0.10,
heat_island_ac_increase     = 0.05,
property_tax_capture_safety = 0.02,
talent_drain_school         = 0.05,
),
)

def dc_net_zero_passing() -> DataCenter:
“””
Example passing configuration from framework:
ERF 0.8 + closed loop water + traffic optimization + gravity wells.
“””
return DataCenter(
name     = “DC — Net Zero Passing Config”,
physical = DCPhysical(
it_load_mw = DC_IT_LOAD_MW,
pue        = 1.20,    # best practice
wue        = 0.0,     # closed loop
erf        = 0.80,    # 80% heat exported to district heating
),
coupling = CouplingChannels(
heat_export_active       = True,
heat_homes_served        = 10_000,
heat_replaces_gas_mw     = 9.6,    # 80% of 12MW total heat
water_recharge_active    = True,
water_acres_irrigated    = 500,
water_net_draw_fraction  = 0.0,    # fully closed
compute_purpose          = ComputePurpose.TRAFFIC_OPTIMIZATION,
compute_energy_saved_mwh = 400,    # saves 400MWh/day citywide transport
grid_battery_mwh         = 100,
grid_black_start         = True,
tax_annual_usd           = 50_000_000,
tax_destination          = TaxDestination.GRAVITY_WELLS,
),
parasitic = ParasiticEffects(
grid_strain_water_pump_loss = 0.01,   # reduced — grid stable
heat_island_ac_increase     = 0.01,   # reduced — heat captured not exhausted
property_tax_capture_safety = 0.00,   # tax going to infrastructure
talent_drain_school         = 0.02,   # some talent drain remains
),
)

def dc_partial_coupling() -> DataCenter:
“””
Greenwashed DC: some coupling channels active but insufficient.
Heat export active but ERF too low. Compute mixed-local.
Common ‘sustainability report’ configuration.
“””
return DataCenter(
name     = “DC — Greenwashed Partial Coupling”,
physical = DCPhysical(
it_load_mw = DC_IT_LOAD_MW,
pue        = 1.40,
wue        = 0.80,
erf        = 0.25,    # some heat export but below ERF floor
),
coupling = CouplingChannels(
heat_export_active       = True,
heat_homes_served        = 1_200,
water_recharge_active    = True,
water_acres_irrigated    = 50,
water_net_draw_fraction  = 0.4,
compute_purpose          = ComputePurpose.MIXED_LOCAL,
compute_energy_saved_mwh = 30,
grid_battery_mwh         = 10,
tax_annual_usd           = 5_000_000,
tax_destination          = TaxDestination.ADMIN_BLOAT,
),
parasitic = ParasiticEffects(
grid_strain_water_pump_loss = 0.07,
heat_island_ac_increase     = 0.04,
property_tax_capture_safety = 0.02,
talent_drain_school         = 0.04,
),
)

def dc_layer_zero() -> DataCenter:
“””
Ideal: DC as missing Layer Zero infrastructure.
Compute = Layer Zero training platform (10k pump repairs/yr).
“””
return DataCenter(
name     = “DC — Layer Zero Infrastructure”,
physical = DCPhysical(
it_load_mw = DC_IT_LOAD_MW,
pue        = 1.10,
wue        = 0.0,
erf        = 0.85,
),
coupling = CouplingChannels(
heat_export_active       = True,
heat_homes_served        = 12_000,
water_recharge_active    = True,
water_acres_irrigated    = 800,
water_net_draw_fraction  = 0.0,
compute_purpose          = ComputePurpose.LAYER0_TRAINING,
compute_energy_saved_mwh = 600,
grid_battery_mwh         = 200,
grid_black_start         = True,
tax_annual_usd           = 50_000_000,
tax_destination          = TaxDestination.INFRASTRUCTURE_MIX,
),
parasitic = ParasiticEffects(
grid_strain_water_pump_loss = 0.00,
heat_island_ac_increase     = 0.005,
property_tax_capture_safety = 0.00,
talent_drain_school         = 0.01,
),
)

# ── Comparative Runner ────────────────────────────────────────────────────────

def run_comparison() -> List[Dict]:
configs = [
dc_parasite(),
dc_partial_coupling(),
dc_net_zero_passing(),
dc_layer_zero(),
]
return [dc.report() for dc in configs]

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:

```
print("=== DATA CENTER NET ZERO TEST — COMPARISON ===\n")
print(f"Community baseline: {COMMUNITY_POPULATION:,} people | "
      f"{COMMUNITY_ENERGY_DAY_MWH:,.0f} MWh/day | "
      f"{COMMUNITY_KWH_PER_PERSON_DAY} kWh/person/day\n")

configs = [
    dc_parasite(),
    dc_partial_coupling(),
    dc_net_zero_passing(),
    dc_layer_zero(),
]

header = f"{'Configuration':<38} {'Net Zero':>8} {'Purpose Δ':>10} {'Energy Δ MWh':>13} {'Failure Mode'}"
print(header)
print("─" * 100)

for dc in configs:
    r = dc.net_zero_test()
    nz    = "✓ PASS" if r["net_zero"] else "✗ FAIL"
    pct   = f"{r['purpose_delta']:+.1f}%"
    emwh  = f"{r['energy_delta_mwh']:+.0f}"
    fail  = r["failure_mode"] or "—"
    print(f"  {dc.name:<36} {nz:>8} {pct:>10} {emwh:>13}   {fail}")

print("\n\n=== PHYSICAL PARAMETERS ===\n")
print(f"{'Config':<38} {'PUE':>6} {'WUE':>6} {'ERF':>6} "
      f"{'Total MW':>10} {'Heat Wasted MW':>15} {'Water L/day':>12}")
print("─" * 100)
for dc in configs:
    p = dc.physical
    print(f"  {dc.name:<36} {p.pue:>6.2f} {p.wue:>6.2f} {p.erf:>6.2f} "
          f"{p.total_power_mw:>10.1f} {p.heat_wasted_mw:>15.1f} "
          f"{p.water_day_liters:>12,.0f}")

print("\n\n=== COUPLING CHANNEL BREAKDOWN — NET ZERO PASSING CONFIG ===\n")
nz = dc_net_zero_passing()
r  = nz.net_zero_test()
print("Purpose ADDED:")
for k, v in r["purpose_added"].items():
    print(f"  {k:<30} {v*100:+.2f}%")
print("Purpose REMOVED (parasitic):")
for k, v in r["purpose_removed"].items():
    print(f"  {k:<30} {v*100:+.2f}%  (loss)")
print(f"\n  NET PURPOSE DELTA:           {r['purpose_delta']:+.2f}%")
print(f"  NET ENERGY DELTA:            {r['energy_delta_mwh']:+.1f} MWh/day")
print(f"  NET ZERO:                    {'✓ PASS' if r['net_zero'] else '✗ FAIL'}")

print("\n\n=== RULE SUMMARY ===")
print("""
```

Data center is net zero IFF:
1. ERF >= 0.5  — heat exported, not wasted to atmosphere
2. WUE → 0    — water cycle closed, no net aquifer draw
3. Compute serves local purpose (factor > 0)
4. Tax → direct infrastructure (not admin bloat)
5. Grid buffer installed (absorb solar, enable black start)

99% of real data centers fail all five.
Thermodynamic parasite = extracts electrons, exports heat, captures tax,
serves distant economic actors, degrades local Layer Zero capacity.
“””)
