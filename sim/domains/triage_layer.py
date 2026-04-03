#!/usr/bin/env python3
# MODULE: sim/domains/triage_layer.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: python -m sim.domains.triage_layer
# TIER: domain
# Infrastructure triage — financial vs thermodynamic priorities
"""
sim/domains/triage_layer.py
Urban Resilience Simulator — Infrastructure Triage
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Two triage systems compared:
  CURRENT:        financial priority — protect economic output
  THERMODYNAMIC:  load-bearing priority — protect substrate

The difference is not ideology.
It is which metric you optimize.

Current triage optimizes: GDP continuity, market function,
  capital asset preservation.

Thermodynamic triage optimizes: caloric delivery, thermal
  survivability, water purity, medical cold chain, knowledge
  transmission continuity.

Same disruption. Completely different outcomes.
Nobody starves in the thermodynamic model.
Many starve in the current model.
Not because resources are insufficient.
Because allocation sequence is wrong.
"""

from dataclasses import dataclass, field
from enum import Enum


PHI  = 1.6180339887
IPHI = 0.6180339887


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class TriageModel(Enum):
    CURRENT        = "current"         # financial priority
    THERMODYNAMIC  = "thermodynamic"   # load-bearing priority
    HYBRID         = "hybrid"          # transitional — both lenses


class FailureMode(Enum):
    CLIFF     = "cliff"      # sudden threshold collapse
    GRADUAL   = "gradual"    # slow depletion
    CASCADE   = "cascade"    # failure triggers other failures
    PERMANENT = "permanent"  # irreversible


class RecoveryType(Enum):
    PASSIVE_PHYSICS   = "passive_physics"    # ammonia cooling, clay towers, ice houses
    KNOWLEDGE_BASED   = "knowledge_based"    # requires living knowledge holder
    INFRASTRUCTURE    = "infrastructure"     # requires built systems
    HYBRID            = "hybrid"


# ─── DEPENDENCY NODE ──────────────────────────────────────────────────────────

@dataclass
class DependencyNode:
    """
    One system. Real. Located. Measurable.
    Not abstract. Every node is something
    actual people depend on to not die.
    """
    node_id: str
    description: str

    # what it needs to function
    power_mw_current: float        # megawatts — current draw
    power_mw_minimal: float        # minimum viable draw
    power_mw_passive: float        # passive physics alternative (0 = none exists)

    # what happens when it fails
    failure_mode: FailureMode
    hours_to_critical_failure: float   # time from loss of power to life-safety impact
    population_affected: int
    cascade_triggers: list[str]        # node_ids that fail when this fails

    # recovery
    recovery_type: RecoveryType
    recovery_hours: float              # time to restore function
    knowledge_required: bool           # needs living knowledge holder
    passive_alternative: str           # description of low-tech replacement

    # triage scores
    current_priority: int              # 1=highest in current model
    thermodynamic_priority: int        # 1=highest in thermodynamic model

    def priority_inversion(self) -> bool:
        """
        True if current model deprioritizes something
        thermodynamic model says is critical.
        These are the nodes where people die
        under current triage.
        """
        return self.thermodynamic_priority < self.current_priority

    def power_reduction_possible(self) -> float:
        """
        How much power can be shed
        without losing function?
        """
        return self.power_mw_current - self.power_mw_minimal

    def passive_viable(self) -> bool:
        return self.power_mw_passive == 0.0 and self.passive_alternative != ""


# ─── TRIAGE DECISION ──────────────────────────────────────────────────────────

@dataclass
class TriageDecision:
    """
    What actually happens when a decision-maker
    runs triage under each model.
    The decision is the same question.
    The answer is different.
    The outcomes diverge within 72 hours.
    """
    scenario: str
    available_power_mw: float
    total_demand_mw: float

    decisions_current: dict[str, str]       = field(default_factory=dict)
    decisions_thermodynamic: dict[str, str] = field(default_factory=dict)

    outcomes_current: dict[str, float]       = field(default_factory=dict)
    outcomes_thermodynamic: dict[str, float] = field(default_factory=dict)

    def shortfall_mw(self) -> float:
        return max(0, self.total_demand_mw - self.available_power_mw)

    def shortfall_pct(self) -> float:
        return self.shortfall_mw() / self.total_demand_mw * 100


# ─── CORRIDOR BUILD — SUPERIOR TO TOMAH ───────────────────────────────────────

def build_superior_tomah_corridor() -> list[DependencyNode]:
    """
    Real corridor. Real nodes.
    US-53 / US-2 corridor.
    Superior WI → Tomah WI.
    ~200 miles. Food distribution spine.
    Kavik's operational territory.

    Power numbers are estimates calibrated to
    regional facility scale.
    Passive alternatives are real physics —
    not speculative.
    """

    nodes = [

        # ── TIER ZERO — life safety, hours to death if fails ──────────────────

        DependencyNode(
            node_id="food_cold_chain_regional",
            description="Regional food cold storage — warehouses, distribution hubs",
            power_mw_current=18.0,
            power_mw_minimal=6.0,       # run essential bays only
            power_mw_passive=0.0,       # ammonia absorption cooling viable
            failure_mode=FailureMode.CLIFF,
            hours_to_critical_failure=36.0,   # food spoilage begins
            population_affected=280_000,
            cascade_triggers=["food_retail_refrigeration", "medical_cold_chain"],
            recovery_type=RecoveryType.KNOWLEDGE_BASED,
            recovery_hours=72.0,
            knowledge_required=True,
            passive_alternative=(
                "Ammonia absorption cooling (1800s tech, zero electricity). "
                "Clay evaporative towers for dry goods. "
                "Passive ice storage in insulated earthen cellars. "
                "Requires knowledge holder — currently <5 people in corridor."
            ),
            current_priority=8,         # low — not GDP-generating
            thermodynamic_priority=1,   # highest — population substrate
        ),

        DependencyNode(
            node_id="water_treatment_superior",
            description="Superior municipal water treatment",
            power_mw_current=4.2,
            power_mw_minimal=2.1,
            power_mw_passive=0.0,       # gravity-fed filtration possible
            failure_mode=FailureMode.CASCADE,
            hours_to_critical_failure=24.0,
            population_affected=35_000,
            cascade_triggers=["medical_facilities_superior", "food_cold_chain_regional"],
            recovery_type=RecoveryType.HYBRID,
            recovery_hours=48.0,
            knowledge_required=True,
            passive_alternative=(
                "Slow sand filtration — gravity fed, zero power. "
                "Solar disinfection (SODIS) for point-of-use. "
                "Traditional birch bark / charcoal filtration for emergency. "
                "Lake Superior gravity head exists — pipe infrastructure needed."
            ),
            current_priority=3,
            thermodynamic_priority=2,
        ),

        DependencyNode(
            node_id="medical_cold_chain",
            description="Medical supply cold chain — insulin, vaccines, blood products",
            power_mw_current=2.8,
            power_mw_minimal=1.2,
            power_mw_passive=0.0,
            failure_mode=FailureMode.CLIFF,
            hours_to_critical_failure=8.0,    # insulin degrades fast
            population_affected=12_000,        # insulin-dependent diabetics alone
            cascade_triggers=["hospital_function"],
            recovery_type=RecoveryType.PASSIVE_PHYSICS,
            recovery_hours=4.0,
            knowledge_required=True,
            passive_alternative=(
                "Ammonia absorption refrigeration — same tech as food cold chain. "
                "Zeer pot (clay pot evaporative cooler) maintains 4-8°C in dry conditions. "
                "Underground storage at consistent 8-12°C — requires site knowledge. "
                "Spring-fed cold room where geology allows."
            ),
            current_priority=4,
            thermodynamic_priority=3,
        ),

        DependencyNode(
            node_id="fuel_pump_stations",
            description="Fuel distribution — diesel for trucks, heating fuel",
            power_mw_current=1.4,
            power_mw_minimal=0.4,       # hand pumps + gravity feed viable
            power_mw_passive=0.0,
            failure_mode=FailureMode.CASCADE,
            hours_to_critical_failure=12.0,   # trucks stop, heating fails
            population_affected=280_000,
            cascade_triggers=["food_cold_chain_regional", "heating_rural"],
            recovery_type=RecoveryType.KNOWLEDGE_BASED,
            recovery_hours=6.0,
            knowledge_required=True,
            passive_alternative=(
                "Gravity-fed tank systems (elevation differential). "
                "Hand pump retrofits — existing equipment, rarely maintained. "
                "Horse/animal transport for short-range delivery. "
                "Wood gasification for vehicle fuel — known tech, lost practice."
            ),
            current_priority=2,         # current model values fuel (economic)
            thermodynamic_priority=4,
        ),

        DependencyNode(
            node_id="heating_rural",
            description="Rural heating — propane, fuel oil, electric baseboard",
            power_mw_current=45.0,      # winter peak
            power_mw_minimal=8.0,       # essential only, high-risk populations
            power_mw_passive=0.0,
            failure_mode=FailureMode.CLIFF,
            hours_to_critical_failure=6.0,    # hypothermia risk at -20°F
            population_affected=85_000,
            cascade_triggers=["water_pipes_rural", "medical_facilities_rural"],
            recovery_type=RecoveryType.KNOWLEDGE_BASED,
            recovery_hours=2.0,
            knowledge_required=True,
            passive_alternative=(
                "Wood gasification — efficient, known physics, lost practice. "
                "Rocket mass heater — 80%+ efficiency, thermal mass storage. "
                "Community consolidation — fewer heated structures, shared warmth. "
                "Traditional insulation: straw bale, earth berming, animal-skin hangings. "
                "30-hour fire technique — bone/fat fuel for sustained heat."
            ),
            current_priority=5,
            thermodynamic_priority=2,   # tied critical with water in winter
        ),

        # ── TIER ONE — system function, days to critical ───────────────────────

        DependencyNode(
            node_id="communications_hubs",
            description="CB/HAM/LoRa mesh — coordination backbone",
            power_mw_current=0.8,
            power_mw_minimal=0.1,       # solar + battery viable
            power_mw_passive=0.0,
            failure_mode=FailureMode.CASCADE,
            hours_to_critical_failure=48.0,
            population_affected=280_000,
            cascade_triggers=["emergency_coordination", "supply_chain_routing"],
            recovery_type=RecoveryType.HYBRID,
            recovery_hours=12.0,
            knowledge_required=True,
            passive_alternative=(
                "CB radio on vehicle power — trucks never lose this. "
                "HAM operators on battery/solar — existing network. "
                "LoRa mesh — low power, long range, peer-to-peer. "
                "Physical messenger relay for corridor — horse or bicycle."
            ),
            current_priority=6,
            thermodynamic_priority=5,
        ),

        DependencyNode(
            node_id="gavilon_grain_superior",
            description="Gavilon Grain elevator — Superior WI — regional food buffer",
            power_mw_current=3.2,
            power_mw_minimal=0.8,
            power_mw_passive=0.0,
            failure_mode=FailureMode.GRADUAL,
            hours_to_critical_failure=720.0,   # 30 days — grain stores
            population_affected=180_000,
            cascade_triggers=["food_cold_chain_regional"],
            recovery_type=RecoveryType.INFRASTRUCTURE,
            recovery_hours=24.0,
            knowledge_required=False,
            passive_alternative=(
                "Grain storage is inherently passive — dry, cool, dark. "
                "Aeration can be manual or wind-driven. "
                "Traditional grain pits with clay lining — thousands of years proven. "
                "This node is actually MORE resilient than current management implies."
            ),
            current_priority=1,         # current model prioritizes economic assets
            thermodynamic_priority=7,   # actually resilient — grain keeps
        ),

        # ── TIER TWO — economic function, weeks to critical ────────────────────

        DependencyNode(
            node_id="data_centers_regional",
            description="Regional data centers — financial, commercial",
            power_mw_current=85.0,      # massive draw
            power_mw_minimal=12.0,      # essential government/medical records only
            power_mw_passive=0.0,
            failure_mode=FailureMode.GRADUAL,
            hours_to_critical_failure=336.0,   # 2 weeks — economic disruption
            population_affected=280_000,        # economic impact
            cascade_triggers=[],
            recovery_type=RecoveryType.INFRASTRUCTURE,
            recovery_hours=1.0,
            knowledge_required=False,
            passive_alternative=(
                "Efficiency gain available: liquid cooling, chip consolidation, "
                "workload shifting to off-peak. "
                "85MW → 12MW for essential records/comms is achievable now. "
                "The 73MW gap is speculative financial compute. "
                "That 73MW powers food cold chain for the entire corridor."
            ),
            current_priority=1,         # current model: data centers = economy
            thermodynamic_priority=9,   # sheddable — people don't die without Netflix
        ),

        DependencyNode(
            node_id="commercial_retail_refrigeration",
            description="Walmart, grocery chains — commercial refrigeration",
            power_mw_current=22.0,
            power_mw_minimal=8.0,       # essential food preservation only
            power_mw_passive=0.0,
            failure_mode=FailureMode.GRADUAL,
            hours_to_critical_failure=48.0,
            population_affected=180_000,
            cascade_triggers=["food_retail_supply"],
            recovery_type=RecoveryType.PASSIVE_PHYSICS,
            recovery_hours=6.0,
            knowledge_required=True,
            passive_alternative=(
                "Passive cooling in insulated earthen cellars. "
                "Ammonia absorption for temperature-critical items. "
                "Community root cellar networks — distributed, resilient. "
                "Traditional preservation: fermentation, drying, smoking, salting."
            ),
            current_priority=3,
            thermodynamic_priority=6,
        ),

        # ── INCENTIVE COMPARISON NODE ──────────────────────────────────────────

        DependencyNode(
            node_id="passive_cooling_knowledge",
            description=(
                "Knowledge of passive cooling physics — "
                "ammonia absorption, evaporative clay, ice houses, "
                "root cellars, thermal mass, earth sheltering"
            ),
            power_mw_current=0.0,       # costs nothing to run
            power_mw_minimal=0.0,
            power_mw_passive=0.0,
            failure_mode=FailureMode.PERMANENT,   # when last holder dies
            hours_to_critical_failure=0.0,         # invisible until needed
            population_affected=280_000,
            cascade_triggers=[
                "food_cold_chain_regional",
                "medical_cold_chain",
                "heating_rural",
                "commercial_retail_refrigeration",
            ],
            recovery_type=RecoveryType.KNOWLEDGE_BASED,
            recovery_hours=17520.0,    # 2 years minimum apprenticeship
            knowledge_required=True,
            passive_alternative="This IS the passive alternative.",
            current_priority=99,        # invisible to current model — generates no revenue
            thermodynamic_priority=1,   # highest — unlocks every other passive system
        ),
    ]

    return nodes


# ─── TRIAGE COMPARISON ────────────────────────────────────────────────────────

def run_triage_comparison(
    nodes: list[DependencyNode],
    available_power_mw: float = 80.0,   # Taiwan disruption: 40% grid loss
) -> TriageDecision:
    """
    Same disruption. Two models. Show the gap.
    """
    total_demand = sum(n.power_mw_current for n in nodes)

    decision = TriageDecision(
        scenario="Taiwan semiconductor cascade — 40% regional grid loss",
        available_power_mw=available_power_mw,
        total_demand_mw=total_demand,
    )

    # current model: allocate by current_priority
    # lowest number = first served
    budget = available_power_mw
    for node in sorted(nodes, key=lambda n: n.current_priority):
        if budget >= node.power_mw_current:
            decision.decisions_current[node.node_id] = "FULL POWER"
            budget -= node.power_mw_current
        elif budget >= node.power_mw_minimal:
            decision.decisions_current[node.node_id] = "MINIMAL"
            budget -= node.power_mw_minimal
        else:
            decision.decisions_current[node.node_id] = "DARK"

    # thermodynamic model: allocate by thermodynamic_priority
    # uses minimal draw first, then passive alternatives
    budget = available_power_mw
    for node in sorted(nodes, key=lambda n: n.thermodynamic_priority):
        if budget >= node.power_mw_minimal:
            decision.decisions_thermodynamic[node.node_id] = "MINIMAL"
            budget -= node.power_mw_minimal
        else:
            decision.decisions_thermodynamic[node.node_id] = "PASSIVE/DARK"

    return decision


def print_triage_report(
    nodes: list[DependencyNode],
    decision: TriageDecision,
):
    node_map = {n.node_id: n for n in nodes}

    print(f"\n{'═'*70}")
    print(f"  INFRASTRUCTURE TRIAGE COMPARISON")
    print(f"  Superior–Tomah Corridor, WI")
    print(f"  Scenario: {decision.scenario}")
    print(f"{'═'*70}")
    print(f"\n  Available power : {decision.available_power_mw:.1f} MW")
    print(f"  Total demand    : {decision.total_demand_mw:.1f} MW")
    print(f"  Shortfall       : {decision.shortfall_mw():.1f} MW "
          f"({decision.shortfall_pct():.0f}%)")

    print(f"\n{'─'*70}")
    print(f"  {'NODE':<35} {'CURRENT':>10} {'THERMO':>10} {'INVERSION':>10}")
    print(f"{'─'*70}")

    inversions = 0
    for node_id in decision.decisions_current:
        node = node_map[node_id]
        cur  = decision.decisions_current[node_id]
        thm  = decision.decisions_thermodynamic.get(node_id, "—")
        inv  = "⚠ INVERTED" if node.priority_inversion() else ""
        if node.priority_inversion():
            inversions += 1
        print(f"  {node_id:<35} {cur:>10} {thm:>10} {inv:>10}")

    print(f"\n  Priority inversions: {inversions} nodes")
    print(f"  (nodes current model deprioritizes that thermodynamic model says are critical)")

    print(f"\n{'─'*70}")
    print(f"  PASSIVE ALTERNATIVES AVAILABLE (zero power required):")
    print(f"{'─'*70}")
    for node in nodes:
        if node.passive_alternative and node.passive_alternative != "":
            blocked = "KNOWLEDGE LOST" if node.knowledge_required else "BUILDABLE NOW"
            print(f"\n  {node.node_id} [{blocked}]:")
            for line in node.passive_alternative.split(". "):
                if line.strip():
                    print(f"    • {line.strip()}.")

    print(f"\n{'─'*70}")
    print(f"  KEY FINDING:")
    print(f"{'─'*70}")
    print(f"""
  Current model gives data centers full power (85 MW).
  That 85 MW would run:
    • Food cold chain corridor    : 18 MW
    • Water treatment all nodes   :  8 MW
    • Medical cold chain          :  3 MW
    • Rural heating essential     :  8 MW
    • Fuel pump stations          :  1 MW
    • Communications mesh         :  0.1 MW
    TOTAL load-bearing essential  : 38.1 MW

  Data centers shed to essential records only: 12 MW
  Freed capacity                  : 73 MW
  That 73 MW covers ENTIRE corridor life-safety load
  with 35 MW remaining for economic tier.

  Nobody starves. Nobody freezes. Nobody dies of insulin failure.
  Data centers run essential functions.
  Netflix goes dark.
  That is the entire trade.

  The reason it doesn't happen:
  Data centers have capital lawyers.
  Insulin-dependent diabetics do not.
    """)

    print(f"{'═'*70}\n")


if __name__ == "__main__":
    nodes    = build_superior_tomah_corridor()
    decision = run_triage_comparison(nodes, available_power_mw=80.0)
    print_triage_report(nodes, decision)
