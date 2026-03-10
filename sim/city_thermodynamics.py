# “””
city_thermodynamics.py

City institutions as thermodynamic engines.
All reduce to: Low-entropy input → Temporary local order → High-entropy exhaust.

Architecture:
CityInstitution
├── purpose (irreducible physics function)
├── mvr (minimum viable resources: mass, energy, operators)
│     ├── nominal_kwh_day     (standard operation)
│     └── floor_kwh_day       (absolute minimum — muscle/gravity/sun)
├── thermo_cycle (input → work → waste)
├── efficiency (useful order / total energy in)
├── substitutability (operator vs equipment ceiling)
├── operator_state (trust decay, cognitive load)
└── energy_mode (NOMINAL | MINIMUM | FLOOR)

Efficiency caps:
Human metabolic bottleneck: ~25% (70% body heat loss)
No institution exceeds 70%
Scale adds bureaucratic friction: calories burned, zero work output

Population reference: 1000 people unless noted per-incident.

Integrates InstitutionalFirstPrinciples:

- operator trust decay → pipeline collapse
- substitutability profiles
- Layer Zero bypass (2-3x efficiency, direct input access)
- latent node recovery constants
  “””

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

# ── Constants ─────────────────────────────────────────────────────────────────

HUMAN_METABOLIC_EFFICIENCY   = 0.25   # ~25% useful work; 75% waste heat
HUMAN_THERMAL_LOSS           = 0.70   # 70% body heat radiated
BUREAUCRACY_FRICTION_PER_TIER = 0.05  # each management tier adds ~5% parasitic loss
TRUST_PHASE_TRANSITION       = 0.35
MENTORSHIP_DECAY_RATE        = 0.60
RECOVERY_BASE_YR             = 1.0    # optimistic latent node
RECOVERY_TRUST_COLLAPSE_YR   = 3.5   # pipeline poisoned

# ── Enums ─────────────────────────────────────────────────────────────────────

class EnergyMode(Enum):
NOMINAL  = “nominal”    # standard operation
MINIMUM  = “minimum”    # stripped to essential loads
FLOOR    = “floor”      # absolute minimum: muscle/gravity/sunlight

class SubstitutabilityProfile(Enum):
OPERATOR_DOMINANT  = “operator_dominant”   # rural: skill covers equipment gaps
EQUIPMENT_DOMINANT = “equipment_dominant”  # suburban: equipment covers skill gaps
BALANCED           = “balanced”

class NodeStatus(Enum):
ACTIVE    = “active”
FACADE    = “facade”     # shell standing, no crew
LATENT    = “latent”     # recoverable
COLLAPSED = “collapsed”  # buffer gone or trust gone

# ── Operator State ─────────────────────────────────────────────────────────────

@dataclass
class OperatorState:
“””
Cognitive load decomposed.
Key distinction: hard-case fatigue (recoverable) vs
chronic infrastructure distrust (structural rewiring — different failure mode).
“””
months_in_environment:          float = 0.0
load_primary_function:          float = 0.5
load_equipment_uncertainty:     float = 0.0
load_workaround_maintenance:    float = 0.0
load_infrastructure_monitoring: float = 0.0
infrastructure_trust_index:     float = 1.0

```
@property
def total_load(self) -> float:
    return (self.load_primary_function
            + self.load_equipment_uncertainty
            + self.load_workaround_maintenance
            + self.load_infrastructure_monitoring)

@property
def load_recoverable(self) -> bool:
    return self.infrastructure_trust_index >= TRUST_PHASE_TRANSITION

@property
def skill_transmission_rate(self) -> float:
    if self.infrastructure_trust_index < TRUST_PHASE_TRANSITION:
        return MENTORSHIP_DECAY_RATE  # stop mentoring, warn off successors
    return 1.0

@property
def recruitment_advocacy(self) -> float:
    if self.infrastructure_trust_index < TRUST_PHASE_TRANSITION:
        return 0.0   # net negative signal into pipeline
    return max(0.0, 1.0 - self.total_load * 0.4)

def update(self, infra_quality: float, months_delta: float = 1.0):
    decay = (1.0 - infra_quality) * 0.08 * months_delta
    self.infrastructure_trust_index = max(0.0, self.infrastructure_trust_index - decay)
    self.months_in_environment += months_delta
    t = 1.0 - self.infrastructure_trust_index
    self.load_equipment_uncertainty     = 0.40 * t
    self.load_workaround_maintenance    = 0.30 * t
    self.load_infrastructure_monitoring = 0.20 * t

def report(self) -> Dict:
    return {
        "months":             self.months_in_environment,
        "total_load":         round(self.total_load, 3),
        "trust_index":        round(self.infrastructure_trust_index, 3),
        "load_recoverable":   self.load_recoverable,
        "transmission_rate":  round(self.skill_transmission_rate, 3),
        "recruitment":        round(self.recruitment_advocacy, 3),
    }
```

# ── MVR ───────────────────────────────────────────────────────────────────────

@dataclass
class MVR:
“””
Minimum Viable Resources.
physical_buffer_days: stored supply on hand — explicit, not magic number.
floor_kwh_day: absolute minimum (gravity/muscle/sun — non-zero only for pumping/heat).
“””
mass_kg:              float = 0.0
nominal_kwh_day:      float = 0.0    # standard operation per 1000 people
floor_kwh_day:        float = 0.0    # absolute floor
operators_needed:     int   = 1
physical_buffer_days: float = 3.0
floor_note:           str   = “”     # what enables the floor (gravity, candles, etc.)

# ── Thermo Cycle ──────────────────────────────────────────────────────────────

@dataclass
class ThermoCycle:
“””
Input → Work → Waste Heat.
All institutions: heat pumps against local entropy increase.
“””
input_description:  str = “”   # low-entropy inputs
work_description:   str = “”   # useful order created
waste_description:  str = “”   # high-entropy exhaust
efficiency:         float = 0.25  # useful_order / total_energy_in
efficiency_losses:  str = “”   # where the rest goes

```
@property
def bureaucratic_adjusted_efficiency(self, management_tiers: int = 2) -> float:
    """Each tier of management adds parasitic friction."""
    return max(0.05,
               self.efficiency - (management_tiers * BUREAUCRACY_FRICTION_PER_TIER))

def layer_zero_efficiency(self) -> float:
    """
    Direct access to inputs, no institutional overhead.
    2-3x efficiency empirically — not magic, just removed friction.
    """
    return min(0.70, self.efficiency * 2.5)
```

# ── City Institution ──────────────────────────────────────────────────────────

@dataclass
class CityInstitution:
“””
Thermodynamic substrate.
Utility = f(Layer Zero humans activating it).
Without operators: heated tent burning fuel.
“””
name:    str
purpose: str
mvr:     MVR
cycle:   ThermoCycle
links:   List[str] = field(default_factory=list)

```
profile:                        SubstitutabilityProfile = SubstitutabilityProfile.BALANCED
operator_substitution_ceiling:  float = 0.50
equipment_substitution_ceiling: float = 0.50
infrastructure_quality:         float = 1.0
energy_mode:                    EnergyMode = EnergyMode.NOMINAL
operator_state:                 OperatorState = field(default_factory=OperatorState)

# ── Energy ────────────────────────────────────────────────────────────────

@property
def active_kwh_day(self) -> float:
    if self.energy_mode == EnergyMode.NOMINAL:
        return self.mvr.nominal_kwh_day
    if self.energy_mode == EnergyMode.MINIMUM:
        return (self.mvr.nominal_kwh_day + self.mvr.floor_kwh_day) / 2
    return self.mvr.floor_kwh_day  # FLOOR

# ── Survival Window ───────────────────────────────────────────────────────

def survival_window_days(self, crew: int) -> float:
    buf = self.mvr.physical_buffer_days
    if crew >= self.mvr.operators_needed:
        return buf * (1.0 + self.cycle.efficiency)
    return buf * 0.1  # facade

# ── Node Status ───────────────────────────────────────────────────────────

def node_status(self, crew: int) -> NodeStatus:
    trust = self.operator_state.infrastructure_trust_index
    buf   = self.mvr.physical_buffer_days
    if crew >= self.mvr.operators_needed:
        return NodeStatus.ACTIVE
    if buf > 0 and trust >= TRUST_PHASE_TRANSITION:
        return NodeStatus.LATENT
    if buf <= 0 or trust < TRUST_PHASE_TRANSITION:
        return NodeStatus.COLLAPSED
    return NodeStatus.FACADE

# ── Recovery ──────────────────────────────────────────────────────────────

def recovery_years(self) -> float:
    t = self.operator_state.infrastructure_trust_index
    if t < TRUST_PHASE_TRANSITION:
        return RECOVERY_TRUST_COLLAPSE_YR  # pipeline poisoned
    return 0.5 + 1.5 * (1.0 - t)

# ── Tick ──────────────────────────────────────────────────────────────────

def tick(self, months: float = 1.0):
    self.operator_state.update(self.infrastructure_quality, months)

# ── Report ────────────────────────────────────────────────────────────────

def report(self, crew: int) -> Dict:
    status = self.node_status(crew)
    return {
        "institution":   self.name,
        "purpose":       self.purpose,
        "energy_mode":   self.energy_mode.value,
        "active_kwh_day": self.active_kwh_day,
        "mvr": {
            "mass_kg":          self.mvr.mass_kg,
            "nominal_kwh_day":  self.mvr.nominal_kwh_day,
            "floor_kwh_day":    self.mvr.floor_kwh_day,
            "floor_note":       self.mvr.floor_note,
            "operators_needed": self.mvr.operators_needed,
            "buffer_days":      self.mvr.physical_buffer_days,
        },
        "thermo": {
            "input":      self.cycle.input_description,
            "work":       self.cycle.work_description,
            "waste":      self.cycle.waste_description,
            "efficiency": self.cycle.efficiency,
            "losses":     self.cycle.efficiency_losses,
            "layer_zero_efficiency": round(self.cycle.layer_zero_efficiency(), 3),
        },
        "substitutability": {
            "profile":           self.profile.name,
            "operator_ceiling":  self.operator_substitution_ceiling,
            "equipment_ceiling": self.equipment_substitution_ceiling,
        },
        "operator":       self.operator_state.report(),
        "node_status":    status.value,
        "recovery_years": round(self.recovery_years(), 2),
        "links":          self.links,
    }
```

# ── City ──────────────────────────────────────────────────────────────────────

@dataclass
class City:
“””
Minimum viable city = these cycles running in parallel, floor inputs only.
No institution exceeds 70% efficiency.
Humans cap at ~25% (metabolic waste).
Scale adds bureaucratic friction.
“””
name:         str
population:   int
institutions: List[CityInstitution] = field(default_factory=list)

```
def add(self, inst: CityInstitution):
    self.institutions.append(inst)

def tick(self, months: float = 1.0):
    for inst in self.institutions:
        inst.tick(months)

def total_kwh_day(self) -> float:
    return sum(i.active_kwh_day for i in self.institutions)

def kwh_per_person_day(self) -> float:
    return self.total_kwh_day() / self.population

def energy_report(self) -> Dict:
    rows = []
    for inst in self.institutions:
        rows.append({
            "name":           inst.name,
            "mode":           inst.energy_mode.value,
            "kwh_day":        inst.active_kwh_day,
            "efficiency":     inst.cycle.efficiency,
            "floor_kwh":      inst.mvr.floor_kwh_day,
            "floor_note":     inst.mvr.floor_note,
        })
    return {
        "city":              self.name,
        "population":        self.population,
        "total_kwh_day":     round(self.total_kwh_day(), 1),
        "kwh_per_person":    round(self.kwh_per_person_day(), 3),
        "institutions":      rows,
        "note": (
            "Floor ~0.1 kWh/person/day. Non-zero floors = pumping + winter heat. "
            "Everything else → 0 via muscle/gravity/sun."
        ),
    }

def status_report(self, crew_map: Dict[str, int]) -> List[Dict]:
    out = []
    for inst in self.institutions:
        crew = crew_map.get(inst.name, 0)
        out.append({
            "name":   inst.name,
            "status": inst.node_status(crew).value,
            "window": round(inst.survival_window_days(crew), 1),
            "recovery_yr": round(inst.recovery_years(), 2),
            "trust":  round(inst.operator_state.infrastructure_trust_index, 3),
        })
    return out
```

# ── Archetypes ────────────────────────────────────────────────────────────────

def build_city_1000() -> City:
“””
Minimum viable city, 1000 people.
All institutions at nominal energy. Switch energy_mode to adjust.
“””
city = City(name=“MVR City”, population=1000)

```
city.add(CityInstitution(
    name    = "Church",
    purpose = "Social coordination + morale stabilization",
    mvr     = MVR(mass_kg=2, nominal_kwh_day=20, floor_kwh_day=5,
                  operators_needed=2, physical_buffer_days=30,
                  floor_note="candles + body heat, winter only"),
    cycle   = ThermoCycle(
        input_description  = "Biomass calories",
        work_description   = "Shared rhythm → coordinated labor",
        waste_description  = "Exhaled CO2, radiated body heat",
        efficiency         = 0.35,
        efficiency_losses  = "65% ceremony overhead",
    ),
    links   = ["Food", "School"],
    profile = SubstitutabilityProfile.OPERATOR_DOMINANT,
    operator_substitution_ceiling  = 0.90,
    equipment_substitution_ceiling = 0.10,
))

city.add(CityInstitution(
    name    = "School",
    purpose = "Skill replication (info patterns to child brains)",
    mvr     = MVR(mass_kg=1, nominal_kwh_day=50, floor_kwh_day=10,
                  operators_needed=5, physical_buffer_days=90,
                  floor_note="chalk + daylight, group under one roof"),
    cycle   = ThermoCycle(
        input_description  = "Human metabolism + paper/chalk",
        work_description   = "Verbal/symbolic transfer → retained knowledge",
        waste_description  = "Heat, sound, paper scraps",
        efficiency         = 0.20,
        efficiency_losses  = "80% attention decay, repetition overhead",
    ),
    links   = ["Church", "Water"],
    profile = SubstitutabilityProfile.OPERATOR_DOMINANT,
    operator_substitution_ceiling  = 0.85,
    equipment_substitution_ceiling = 0.15,
))

city.add(CityInstitution(
    name    = "City Water",
    purpose = "Mass transfer H2O aquifer → tap",
    mvr     = MVR(mass_kg=1000, nominal_kwh_day=200, floor_kwh_day=20,
                  operators_needed=3, physical_buffer_days=1,
                  floor_note="gravity feed from hill/reservoir + hand pumps"),
    cycle   = ThermoCycle(
        input_description  = "Electrical work on pump",
        work_description   = "Pressure gradient → drinkable flow",
        waste_description  = "Pipe friction heat, evaporation loss",
        efficiency         = 0.60,
        efficiency_losses  = "40% pipe friction, evaporation",
    ),
    links   = ["Sewer", "Fire Department", "Hospital"],
    profile = SubstitutabilityProfile.EQUIPMENT_DOMINANT,
    operator_substitution_ceiling  = 0.20,
    equipment_substitution_ceiling = 0.80,
))

city.add(CityInstitution(
    name    = "Sewer",
    purpose = "Waste export — biomass decay → soil dilution",
    mvr     = MVR(mass_kg=5, nominal_kwh_day=50, floor_kwh_day=0,
                  operators_needed=2, physical_buffer_days=0,
                  floor_note="gravity only, no lift stations needed"),
    cycle   = ThermoCycle(
        input_description  = "Potential energy (gravity) + lift pump kWh",
        work_description   = "Flow separation → pathogen containment",
        waste_description  = "Treated effluent, methane off-gas",
        efficiency         = 0.70,
        efficiency_losses  = "30% clogs, infiltration",
    ),
    links   = ["City Water"],
    profile = SubstitutabilityProfile.EQUIPMENT_DOMINANT,
    operator_substitution_ceiling  = 0.15,
    equipment_substitution_ceiling = 0.85,
))

city.add(CityInstitution(
    name    = "Electricity Grid",
    purpose = "Electron delivery — voltage for work extraction",
    mvr     = MVR(mass_kg=0, nominal_kwh_day=500, floor_kwh_day=50,
                  operators_needed=5, physical_buffer_days=0,
                  floor_note="critical circuits only: pumps + 1 light per 10 homes"),
    cycle   = ThermoCycle(
        input_description  = "Chemical/thermal fuel → current",
        work_description   = "Usable power at endpoint",
        waste_description  = "Transmission heat, line loss",
        efficiency         = 0.35,
        efficiency_losses  = "65% heat + transmission",
    ),
    links   = ["City Water", "Sewer", "Hospital", "School"],
    profile = SubstitutabilityProfile.EQUIPMENT_DOMINANT,
    operator_substitution_ceiling  = 0.10,
    equipment_substitution_ceiling = 0.90,
))

city.add(CityInstitution(
    name    = "Roads/Transport",
    purpose = "Kinetic energy arbitrage — bodies/goods A→B",
    mvr     = MVR(mass_kg=10, nominal_kwh_day=50, floor_kwh_day=0,
                  operators_needed=4, physical_buffer_days=365,
                  floor_note="4-way stops, foot/bike only — 0 kWh"),
    cycle   = ThermoCycle(
        input_description  = "Fuel combustion",
        work_description   = "Directed motion → relocated mass",
        waste_description  = "Tire heat, exhaust, road friction",
        efficiency         = 0.25,
        efficiency_losses  = "75% idling, rubber heat, empty returns",
    ),
    links   = ["Garbage Collection", "Fire Department", "Police"],
    profile = SubstitutabilityProfile.BALANCED,
    operator_substitution_ceiling  = 0.50,
    equipment_substitution_ceiling = 0.50,
))

city.add(CityInstitution(
    name    = "Garbage Collection",
    purpose = "Entropy dilution — waste → dispersed landfill",
    mvr     = MVR(mass_kg=5, nominal_kwh_day=200, floor_kwh_day=0,
                  operators_needed=3, physical_buffer_days=7,
                  floor_note="compost + burn pits, no collection"),
    cycle   = ThermoCycle(
        input_description  = "Diesel combustion",
        work_description   = "Mechanical compaction → spread disorder",
        waste_description  = "Exhaust, landfill gas",
        efficiency         = 0.40,
        efficiency_losses  = "60% empty return trips",
    ),
    links   = ["Roads/Transport", "Sewer"],
    profile = SubstitutabilityProfile.EQUIPMENT_DOMINANT,
    operator_substitution_ceiling  = 0.30,
    equipment_substitution_ceiling = 0.70,
))

city.add(CityInstitution(
    name    = "Fire Department",
    purpose = "Heat quench — H2O mass to combustion zone",
    mvr     = MVR(mass_kg=500, nominal_kwh_day=25, floor_kwh_day=0,
                  operators_needed=4, physical_buffer_days=1,
                  floor_note="bucket brigades from nearest water source"),
    cycle   = ThermoCycle(
        input_description  = "Pump work + water mass",
        work_description   = "Steam conversion → fire suppression",
        waste_description  = "Steam to atmosphere, overspray",
        efficiency         = 0.45,
        efficiency_losses  = "55% overspray",
    ),
    links   = ["City Water", "Roads/Transport"],
    profile = SubstitutabilityProfile.BALANCED,
    operator_substitution_ceiling  = 0.60,
    equipment_substitution_ceiling = 0.40,
))

city.add(CityInstitution(
    name    = "Police",
    purpose = "Kinetic restraint — violent motion → stasis",
    mvr     = MVR(mass_kg=0, nominal_kwh_day=20, floor_kwh_day=0,
                  operators_needed=6, physical_buffer_days=0,
                  floor_note="foot patrol, no vehicles"),
    cycle   = ThermoCycle(
        input_description  = "Glucose/adrenaline + vehicle fuel",
        work_description   = "Physical control → order restoration",
        waste_description  = "Stress hormones, paper records, patrol heat",
        efficiency         = 0.15,
        efficiency_losses  = "85% negotiation overhead, patrol without incident",
    ),
    links   = ["Roads/Transport", "Hospital"],
    profile = SubstitutabilityProfile.OPERATOR_DOMINANT,
    operator_substitution_ceiling  = 0.80,
    equipment_substitution_ceiling = 0.20,
))

return city
```

# ── Demo ──────────────────────────────────────────────────────────────────────

if **name** == “**main**”:
import json

```
city = build_city_1000()

print("=== NOMINAL OPERATION ===\n")
print(json.dumps(city.energy_report(), indent=2))

print("\n=== SWITCH TO FLOOR MODE ===\n")
for inst in city.institutions:
    inst.energy_mode = EnergyMode.FLOOR
print(json.dumps(city.energy_report(), indent=2))

print("\n=== 18 MONTHS DEGRADED INFRASTRUCTURE (quality=0.4) ===\n")
for inst in city.institutions:
    inst.infrastructure_quality = 0.4
    inst.energy_mode = EnergyMode.NOMINAL
for _ in range(18):
    city.tick(months=1.0)

# Full crew
crew_map = {
    "Church": 2, "School": 5, "City Water": 3, "Sewer": 2,
    "Electricity Grid": 5, "Roads/Transport": 4, "Garbage Collection": 3,
    "Fire Department": 4, "Police": 6,
}
status = city.status_report(crew_map)
print(json.dumps(status, indent=2))

print("\n=== ZERO CREW (facade/collapse mode) ===\n")
zero_crew = {k: 0 for k in crew_map}
status_zero = city.status_report(zero_crew)
print(json.dumps(status_zero, indent=2))
```
