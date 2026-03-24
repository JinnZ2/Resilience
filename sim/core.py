#!/usr/bin/env python3
"""
sim/core.py — all dataclasses and enums
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class Season(Enum):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL   = "fall"

class DensityType(Enum):
    URBAN        = "urban"
    SUBURBAN     = "suburban"
    RURAL_FRINGE = "rural_fringe"

class RedundancyLevel(Enum):
    NONE   = 0
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3

class StressType(Enum):
    SUPPLY_CHAIN_DISRUPTION = "supply_chain_disruption"
    GRID_FAILURE            = "grid_failure"
    POPULATION_INFLUX       = "population_influx"
    SEASONAL_EXTREME        = "seasonal_extreme"
    CASCADING_FAILURE       = "cascading_failure"
    INFRASTRUCTURE_COLLAPSE = "infrastructure_collapse"

class ZoneType(Enum):
    INNER_CITY   = "inner_city"
    SUBURBAN     = "suburban"
    RURAL_FRINGE = "rural_fringe"

@dataclass
class CognitiveReadinessLayer:
    """
    Human wetware as infrastructure.
    Neuroplasticity determines actual response time
    more than any hardware redundancy.

    Constraint-raised brains scan constantly for failure modes.
    Comfort-raised brains default to institutional mediation.
    Under stress, that difference determines survival windows.

    Not a moral judgment. A training artifact.
    Nobody chooses their childhood constraint gradient.
    """
    zone: str                               = ""
    constraint_gradient: float             = 0.0
    # 0.0-1.0 childhood exposure to genuine scarcity and consequence
    # rural_fringe ~0.85 / inner_city ~0.70 / suburban ~0.15
    failure_mode_scanning: float           = 0.0
    abundance_assumption: float            = 0.0
    institutional_mediation_default: float = 0.0
    adaptation_hours_low: float            = 0.0
    adaptation_hours_high: float           = 0.0
    # rural_fringe 2-6h / inner_city 4-12h / suburban 72-720h

    def cognitive_load_path(self) -> str:
        if self.constraint_gradient > 0.6:
            return "LOAD_BEARING — scans for failure modes, acts under uncertainty"
        if self.constraint_gradient > 0.3:
            return "PARTIAL — some capacity, degrades under high stress"
        return "FACADE — comfort layer only, freezes when institutions fail"

    def rewire_window(self) -> str:
        low  = self.adaptation_hours_low  / 24
        high = self.adaptation_hours_high / 24
        if high < 1:
            return f"{self.adaptation_hours_low:.0f}-{self.adaptation_hours_high:.0f}h"
        return f"{low:.1f}-{high:.1f} days"

@dataclass
class DecisionAuthorityNode:
    """
    Who decides what happens to critical buildings during crisis.
    Are they present? Skin in the game?

    Absentee ownership injects entropy into resilient systems.
    A functional mutual aid network can be frozen by one absent
    landlord protecting abstract property rights while people die.
    """
    zone: str                               = ""
    owner_resident_same: bool               = False
    decision_maker_present_in_crisis: bool  = False
    absentee_ownership_percent: float       = 0.0
    corporate_ownership_percent: float      = 0.0
    community_council_exists: bool          = False
    crisis_decision_protocol: str           = "none"
    # "community" / "owner" / "government" / "none"
    estimated_decision_lag_hours: float     = 0.0
    community_override_likely: bool         = False
    post_crisis_legal_risk: str             = ""

@dataclass
class SocialTrustLayer:
    """
    The actual operating system.

    Gratitude: open loop, compounds indefinitely.
    Transaction: closed loop, terminates on payment.
    None: atomized, no circuit to activate.

    Money injected into gratitude networks converts obligation
    into settled debt. Mirror neuron response stops.
    Circuit closes. Network fragments.

    A system that settles all obligations in cash
    has no stored social energy to draw on under stress.
    """
    zone: str                               = ""
    gratitude_network_active: bool          = False
    obligation_type: str                    = "none"
    # "gratitude" / "transaction" / "none"
    money_penetration: float               = 0.0
    # 0.0 = pure gratitude / 1.0 = pure transaction
    mirror_neuron_triggers: list[str]      = field(default_factory=list)
    # "witnessed_need" / "shared_hardship" / "faith"
    # "kinship" / "professional_identity" / "place_attachment"

    def cascade_potential(self) -> str:
        if self.obligation_type == "gratitude" and self.money_penetration < 0.3:
            return "HIGH — obligation compounds, network self-sustains"
        if self.obligation_type == "transaction":
            return "NONE — every exchange terminates the circuit"
        if self.money_penetration > 0.7:
            return "LOW — gratitude drowned by transaction logic"
        return "MODERATE — degrades under sustained stress"

@dataclass
class ResilienceFoundation:
    """
    Layer Zero. Before infrastructure.
    Standard emergency management models skip this entirely.
    They model pipes and generators.
    Not the humans who operate them under stress,
    make decisions about access,
    and choose whether to help a neighbor
    or wait for institutional authorization.
    """
    zone: str                               = ""
    zone_type: ZoneType                     = ZoneType.SUBURBAN
    population: int                         = 0
    social_trust_index: float              = 0.0
    mutual_aid_networks_active: bool        = False
    mutual_aid_network_names: list[str]     = field(default_factory=list)
    knowledge_holders_present: bool         = False
    knowledge_holders_mobile: bool          = False
    knowledge_domains: list[str]            = field(default_factory=list)
    cognition: CognitiveReadinessLayer      = field(default_factory=CognitiveReadinessLayer)
    decision_authority: DecisionAuthorityNode = field(default_factory=DecisionAuthorityNode)
    social_trust: SocialTrustLayer          = field(default_factory=SocialTrustLayer)

    def system_runs_forward(self) -> bool:
        """
        True  → life takes priority over property in crisis
        False → system freezes waiting for authorization
        A system running backward optimizes property over life.
        It will be bypassed by surviving people.
        The bypassing will be called criminal.
        """
        da = self.decision_authority
        return da.owner_resident_same or (
            da.community_council_exists and
            da.estimated_decision_lag_hours < 6.0
        )

    def entropy_risk(self) -> str:
        da = self.decision_authority
        if da.estimated_decision_lag_hours > 12:
            return "CRITICAL — people will die waiting for authorization"
        if da.absentee_ownership_percent > 0.6:
            return "HIGH — absentee ownership will freeze crisis response"
        if self.social_trust_index < 0.4:
            return "HIGH — no trust foundation"
        if not self.mutual_aid_networks_active:
            return "ELEVATED — no mutual aid structure to activate"
        return "MANAGEABLE"

    def survival_window_hours(self) -> float:
        base = 72.0
        if not self.mutual_aid_networks_active:  base *= 0.5
        if self.decision_authority.absentee_ownership_percent > 0.6: base *= 0.4
        if self.social_trust_index > 0.7:        base *= 1.5
        if self.cognition.constraint_gradient > 0.6: base *= 1.3
        return base

@dataclass
class ActuarialBlindSpot:
    """
    What insurance companies cannot see: only reported claims.

    Rural people extinguish their own fires.
    Fix their own equipment. Triage their own emergencies.
    None of that enters claims data.

    Actuaries: low claims = low risk = lower premiums.
    Reality:   low claims = high competence absorbing risk invisibly.

    Inversion: competent populations undercharged for risk absorbed.
    Dependent populations overcharged for claims generated.
    Insurance extracts from resilience, subsidizes fragility.

    When rural areas can't afford premiums they self-insure.
    Self-insurance is illegal in most jurisdictions.
    Competence gets criminalized.
    """
    zone: str                                   = ""
    unreported_fires_annual: int               = 0
    unreported_accidents_annual: int           = 0
    unreported_equipment_failures_annual: int  = 0
    unreported_medical_events_annual: int      = 0
    actual_risk_events_annual: int             = 0
    institutional_claims_annual: int           = 0
    premium_charged_annual: float              = 0.0
    prevented_claim_value_annual: float        = 0.0

    def institutional_visibility_pct(self) -> float:
        if self.actual_risk_events_annual == 0: return 0.0
        return (self.institutional_claims_annual /
                self.actual_risk_events_annual) * 100

    def extraction_rate(self) -> float:
        if self.prevented_claim_value_annual > 0:
            return self.premium_charged_annual / self.prevented_claim_value_annual
        return 0.0

    def affordability_cliff(self) -> bool:
        return self.extraction_rate() > 3.0

@dataclass
class FailureMode:
    trigger: str                            = ""
    time_to_failure_hours: int             = 0
    cascade_targets: list[str]             = field(default_factory=list)
    recovery_path: list[str]               = field(default_factory=list)
    knowledge_required: list[str]          = field(default_factory=list)

@dataclass
class System:
    name: str                               = ""
    capacity_percent: float                = 100.0
    redundancy: RedundancyLevel            = RedundancyLevel.NONE
    failure_modes: list[FailureMode]       = field(default_factory=list)
    institutional_backups: list[str]       = field(default_factory=list)
    days_to_critical: Optional[int]        = None
    days_to_critical_backed: Optional[int] = None

@dataclass
class WaterSystem(System):
    source: str                             = ""
    treatment_capacity_gpd: int            = 0
    storage_days: float                    = 0
    backup_source: str                     = ""
    purification_methods: list[str]        = field(default_factory=list)

@dataclass
class FoodSystem(System):
    local_production_percent: float        = 0.0
    supply_chain_days: float               = 0
    cold_storage_capacity_tons: float      = 0
    distribution_nodes: list[str]          = field(default_factory=list)
    growing_season_days: int               = 0

@dataclass
class EnergySystem(System):
    grid_dependent_percent: float          = 100.0
    local_generation_mw: float             = 0
    storage_capacity_mwh: float            = 0
    backup_fuel_days: float                = 0
    renewable_sources: list[str]           = field(default_factory=list)

@dataclass
class MedicalSystem(System):
    beds_per_1000: float                   = 0
    trauma_centers: int                    = 0
    supply_stockpile_days: int             = 0
    community_health_workers: int          = 0
    triage_capable_population_pct: float   = 0.0

@dataclass
class RepairSystem(System):
    skilled_trades_per_1000: float         = 0
    tool_library_nodes: int                = 0
    parts_supply_days: int                 = 0
    knowledge_transmission_active: bool    = False

@dataclass
class CommsSystem(System):
    grid_dependent: bool                   = True
    ham_operators: int                     = 0
    cb_network_active: bool                = False
    lora_mesh_nodes: int                   = 0
    backup_comms_range_miles: float        = 0

@dataclass
class ManufacturingSystem(System):
    local_essential_production: list[str]  = field(default_factory=list)
    fabrication_capacity: str              = ""
    raw_material_days: int                 = 0

@dataclass
class InfrastructureLayers:
    water:         WaterSystem             = field(default_factory=WaterSystem)
    food:          FoodSystem              = field(default_factory=FoodSystem)
    energy:        EnergySystem            = field(default_factory=EnergySystem)
    medical:       MedicalSystem           = field(default_factory=MedicalSystem)
    repair:        RepairSystem            = field(default_factory=RepairSystem)
    comms:         CommsSystem             = field(default_factory=CommsSystem)
    manufacturing: ManufacturingSystem     = field(default_factory=ManufacturingSystem)

@dataclass
class LabAsset:
    type: str                               = ""
    equipment_list: list[str]              = field(default_factory=list)
    skill_required: str                    = ""
    potential_functions: list[str]         = field(default_factory=list)

@dataclass
class CollegeNode:
    name: str                               = ""
    enrollment: int                         = 0
    departments: list[str]                 = field(default_factory=list)
    labs: list[LabAsset]                   = field(default_factory=list)
    dormitory_capacity: int                = 0
    cafeteria_capacity: int                = 0
    backup_power: bool                     = False
    water_independent: bool                = False
    seasonal_population: dict              = field(default_factory=dict)
    community_access_agreement: bool       = False
    supply_stockpile_days: int             = 0

@dataclass
class HospitalNode:
    name: str                               = ""
    bed_capacity: int                       = 0
    trauma_capable: bool                   = False
    backup_power_hours: int                = 0
    water_independent: bool                = False
    supply_stockpile_days: int             = 0
    surge_capacity_multiplier: float       = 1.0

@dataclass
class CoopNode:
    name: str                               = ""
    type: str                               = ""
    member_count: int                       = 0
    distribution_capacity_day: int         = 0
    storage_capacity_days: int             = 0
    production_capable: bool               = False
    cold_storage: bool                     = False
    backup_power: bool                     = False

@dataclass
class IndustrialNode:
    name: str                               = ""
    type: str                               = ""
    repurposable: bool                     = False
    potential_functions: list[str]         = field(default_factory=list)
    backup_power: bool                     = False
    water_access: bool                     = False

@dataclass
class InstitutionalAssets:
    colleges:   list[CollegeNode]          = field(default_factory=list)
    hospitals:  list[HospitalNode]         = field(default_factory=list)
    coops:      list[CoopNode]             = field(default_factory=list)
    industrial: list[IndustrialNode]       = field(default_factory=list)

@dataclass
class CityNode:
    name: str                               = ""
    population: int                         = 0
    density: DensityType                   = DensityType.URBAN
    area_sq_miles: float                   = 0
    season: Season                         = Season.WINTER
    zones: list[ResilienceFoundation]      = field(default_factory=list)
    assets: InstitutionalAssets            = field(default_factory=InstitutionalAssets)
    infrastructure: InfrastructureLayers   = field(default_factory=InfrastructureLayers)

@dataclass
class StressScenario:
    type: StressType                        = StressType.GRID_FAILURE
    severity: float                         = 0.5
    duration_days: int                      = 7
    season: Season                         = Season.WINTER
    notes: str                             = ""
