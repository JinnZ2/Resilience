#!/usr/bin/env python3
# MODULE: sim/schema_v2.py
# PROVIDES: build_madison_v2
# DEPENDS: stdlib-only
# RUN: —
# TIER: core
# Tightened schema with cognitive readiness and decision authority
"""
sim/schema_v2.py — tightened schema, v2
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Changes from v1:
- CognitiveReadinessLayer: crew_density, adaptation_speed, training_diversity
- DecisionAuthorityNode: authority_mode, decision_lag (explicit hours)
- SocialTrustLayer: trust_span, norm_mode, conflict_load
- InfrastructureLayer: physical_buffer_hours, intervention_required_by, recovery_complexity
- InstitutionalAsset: affordances, access_mode, staff_alignment, policy_friction
- survival_window(): explicit formula, mechanically obvious
- All math stays lookup-table simple — fits in one head in a fire hall
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class AuthorityMode(Enum):
    CENTRALIZED  = "centralized"   # one person/institution decides
    DISTRIBUTED  = "distributed"   # community decides collectively
    ABSENT       = "absent"        # no decision maker reachable
    CONTESTED    = "contested"     # multiple authorities in conflict

class NormMode(Enum):
    GRATITUDE    = "gratitude"     # open loop, compounds
    MIXED        = "mixed"         # partial, degrades under stress
    TRANSACTION  = "transaction"   # closed loop, terminates on payment

class RecoveryComplexity(Enum):
    EASY   = 1   # anyone with basic knowledge can do it
    MEDIUM = 2   # requires skilled person + basic tools
    HARD   = 3   # requires specialist + supply chain + time

class AccessMode(Enum):
    PUBLIC    = "public"     # anyone can use it
    GATED     = "gated"      # requires permission, usually granted
    LOCKED    = "locked"     # requires override — policy friction high
    CAPTURED  = "captured"   # institution controls, community excluded

class StaffAlignment(Enum):
    NEIGHBORHOOD  = "neighborhood"  # will break rules to help community
    INSTITUTION   = "institution"   # follows policy, won't improvise
    SPLIT         = "split"         # depends on individual, unpredictable

class TrainingDiversity(Enum):
    LOW    = 1   # 1-2 skill domains present
    MEDIUM = 2   # 3-4 skill domains present
    HIGH   = 3   # 5+ skill domains present


# ─── LAYER ZERO: COGNITIVE READINESS v2 ───────────────────────────────────────

@dataclass
class CognitiveReadinessV2:
    """
    crew_density:
        People per 1000 residents who can do critical tasks
        without supervision. Fix pumps. Run field triage.
        Improvise food distribution. Drive in bad conditions.
        Not credentialed — actually capable.

    adaptation_speed:
        Hours to switch from normal to emergency improvisation
        without waiting for instructions.
        Rural fringe: 2-4h
        Inner city:   4-8h
        Suburban:     48-168h (if ever)

    training_diversity:
        Distinct skill domains present in zone.
        LOW    = medical OR mechanical OR logistics — not and.
        MEDIUM = 3-4 domains — can cover most failure modes.
        HIGH   = 5+ domains — full local response capacity.
    """
    zone: str                           = ""
    crew_density: float                 = 0.0
    # capable people per 1000 residents
    # rural fringe:  ~40-80
    # inner city:    ~20-40 (dense but lower domain diversity)
    # suburban:      ~2-8   (credentialed but not operationally capable)

    adaptation_speed_hours: float       = 0.0
    # time from event recognition to improvised action without authorization

    training_diversity: TrainingDiversity = TrainingDiversity.LOW

    # derived — do not set manually
    def effective_crew(self, population: int) -> int:
        return int((self.crew_density / 1000) * population)

    def cognitive_load_path(self) -> str:
        if self.crew_density > 30 and self.adaptation_speed_hours < 8:
            return "LOAD_BEARING"
        if self.crew_density > 10 and self.adaptation_speed_hours < 24:
            return "PARTIAL"
        return "FACADE"


# ─── LAYER ZERO: DECISION AUTHORITY v2 ────────────────────────────────────────

@dataclass
class DecisionAuthorityV2:
    """
    authority_mode:
        How decisions actually get made in this zone.
        ABSENT and CONTESTED are the kill modes —
        both produce decision_lag > survival window.

    decision_lag:
        Hours from obvious need to locally authorized action
        that breaks a rule, uses "private" assets,
        or repurposes institutional space.
        This is the number that kills people.
        Not the absence of resources — the absence of authorization.
    """
    zone: str                           = ""
    authority_mode: AuthorityMode       = AuthorityMode.ABSENT
    decision_lag_hours: float           = 0.0
    # time from need recognition to authorized improvised action
    # distributed community council: 1-4h
    # centralized institutional:     6-24h
    # absent:                        36-72h+
    # contested:                     unknown — could be infinite

    owner_resident_same: bool           = False
    absentee_ownership_percent: float   = 0.0
    community_override_likely: bool     = False

    def runs_forward(self) -> bool:
        """Life before property. Authorization before lag kills someone."""
        return (
            self.authority_mode == AuthorityMode.DISTRIBUTED and
            self.decision_lag_hours < 6.0
        ) or self.owner_resident_same


# ─── LAYER ZERO: SOCIAL TRUST v2 ──────────────────────────────────────────────

@dataclass
class SocialTrustV2:
    """
    trust_span:
        Households reachable via trust-based asks.
        Not acquaintances. People who will actually show up
        or lend equipment or take your kid without a contract.
        Rural fringe:  50-200 households
        Inner city:    20-80 households (dense but fracture lines present)
        Suburban:      2-8 households (if any)

    norm_mode:
        The operating logic of exchange in this zone.
        GRATITUDE = open loop, obligation compounds.
        TRANSACTION = closed loop, terminates on payment.
        The difference determines whether stress activates
        or dissolves the network.

    conflict_load:
        Active fracture lines that will block cooperation.
        This is the field nobody else models.
        HOA vs renters. Campus vs neighborhood.
        Racial/ethnic/political splits. Gang territory.
        These don't show up in resilience assessments
        until they prevent a rescue.
    """
    zone: str                           = ""
    trust_span_households: int          = 0
    norm_mode: NormMode                 = NormMode.TRANSACTION
    conflict_load: str                  = "none"
    # "none" / "low" / "moderate" / "high" / describe specific fracture

    mirror_neuron_triggers: list[str]   = field(default_factory=list)

    def cascade_potential(self) -> str:
        if self.norm_mode == NormMode.GRATITUDE and self.trust_span_households > 50:
            return "HIGH"
        if self.norm_mode == NormMode.TRANSACTION:
            return "NONE"
        if self.conflict_load in ["high", "moderate"]:
            return "BLOCKED — conflict load will prevent activation"
        return "MODERATE"


# ─── LAYER ZERO: COMBINED v2 ──────────────────────────────────────────────────

@dataclass
class ResilienceFoundationV2:
    """
    Layer Zero. Before infrastructure.
    Outputs intervention_arrival_time and intervention_quality
    for each infrastructure layer.
    These feed directly into survival_window calculation.
    """
    zone: str                           = ""
    population: int                     = 0
    social_trust_index: float           = 0.0   # 0.0-1.0 composite

    cognition: CognitiveReadinessV2     = field(default_factory=CognitiveReadinessV2)
    authority: DecisionAuthorityV2      = field(default_factory=DecisionAuthorityV2)
    trust: SocialTrustV2               = field(default_factory=SocialTrustV2)

    mutual_aid_active: bool             = False
    knowledge_domains: list[str]        = field(default_factory=list)

    def intervention_arrival_hours(self) -> float:
        """
        How long before someone competent arrives
        and is authorized to act.
        = adaptation_speed + decision_lag
        (can overlap if community council pre-authorizes)
        """
        overlap = 0.5 if self.authority.authority_mode == AuthorityMode.DISTRIBUTED else 0.0
        return (
            self.cognition.adaptation_speed_hours +
            self.authority.decision_lag_hours -
            (self.cognition.adaptation_speed_hours * overlap)
        )

    def intervention_quality(self) -> str:
        """
        Can arriving crew actually fix/bypass the problem
        or just triage consequences?
        """
        cog = self.cognition
        if (cog.crew_density > 30 and
            cog.training_diversity == TrainingDiversity.HIGH):
            return "FIX — can restore or bypass system"
        if (cog.crew_density > 10 and
            cog.training_diversity == TrainingDiversity.MEDIUM):
            return "STABILIZE — can slow deterioration, cannot restore"
        return "TRIAGE — can manage consequences only, system continues failing"

    def entropy_risk(self) -> str:
        if self.authority.decision_lag_hours > 12:
            return "CRITICAL — people will die waiting for authorization"
        if self.trust.conflict_load in ["high", "moderate"]:
            return "HIGH — conflict load blocks network activation"
        if self.authority.absentee_ownership_percent > 0.6:
            return "HIGH — absentee ownership freezes crisis response"
        if self.social_trust_index < 0.4:
            return "ELEVATED — insufficient trust foundation"
        return "MANAGEABLE"

    def survival_window_hours(self, physical_buffer: float) -> float:
        """
        Core formula — explicit and mechanically obvious:

        if intervention arrives before system needs it:
            window = physical_buffer + extension_from_intervention
        else:
            window = physical_buffer (system fails unassisted)

        Cutting decision_lag from 36h to 4h in suburban zone:
            moves window from 14h to 40h+ for most systems.
        That's the number to show people in a fire hall.
        """
        arrival = self.intervention_arrival_hours()
        quality_extension = {
            "FIX":       physical_buffer * 2.0,
            "STABILIZE": physical_buffer * 0.5,
            "TRIAGE":    physical_buffer * 0.1,
        }
        quality = self.intervention_quality()
        extension = quality_extension.get(quality, 0)

        # trust multiplier — gratitude networks extend window
        trust_mult = 0.7 + (self.social_trust_index * 0.6)

        if arrival < physical_buffer:
            return (physical_buffer + extension) * trust_mult
        else:
            return physical_buffer * trust_mult


# ─── INFRASTRUCTURE LAYER v2 ──────────────────────────────────────────────────

@dataclass
class InfrastructureLayerV2:
    """
    physical_buffer_hours:
        How long the system runs with zero intervention.
        This is physics. Not policy. Not money.
        Water pressure without pumps: 6h.
        Food without resupply: 72h.
        Grid without generation: 0h.

    intervention_required_by:
        When some human must do something non-routine
        to avoid step-down failure.
        Before this point: system manages itself.
        After this point: someone must act or system degrades.

    recovery_complexity:
        EASY   = local crew can restore without supply chain.
        MEDIUM = needs skilled person + parts locally available.
        HARD   = needs specialist + supply chain + time.
        HARD systems don't recover during acute crisis.
        They recover after, if conditions allow.
    """
    name: str                           = ""
    physical_buffer_hours: float        = 0.0
    intervention_required_by_hours: float = 0.0
    recovery_complexity: RecoveryComplexity = RecoveryComplexity.HARD
    redundancy_level: int               = 0     # 0=none, 1=single, 2=double
    institutional_backups: list[str]    = field(default_factory=list)
    failure_cascade_targets: list[str]  = field(default_factory=list)

    def compute_survival_window(
        self,
        zone: ResilienceFoundationV2,
    ) -> dict:
        """
        Explicit calculation. Show your work.
        This is the number that matters in the field.
        """
        arrival   = zone.intervention_arrival_hours()
        quality   = zone.intervention_quality()
        buffer    = self.physical_buffer_hours
        required  = self.intervention_required_by_hours

        quality_mult = {"FIX": 2.0, "STABILIZE": 1.5, "TRIAGE": 1.1}
        mult = quality_mult.get(quality, 1.0)

        trust_mult = 0.7 + (zone.social_trust_index * 0.6)

        if arrival < required:
            window = buffer * mult * trust_mult
            status = "INTERVENTION LIKELY IN TIME"
        else:
            window = buffer * trust_mult
            status = "INTERVENTION TOO SLOW — system fails unassisted"

        return {
            "layer":              self.name,
            "physical_buffer_h":  buffer,
            "intervention_required_by_h": required,
            "intervention_arrival_h": arrival,
            "intervention_quality": quality,
            "survival_window_h":  round(window, 1),
            "survival_window_d":  round(window / 24, 1),
            "status":             status,
            "recovery_complexity": self.recovery_complexity.name,
        }


# ─── INSTITUTIONAL ASSET v2 ───────────────────────────────────────────────────

@dataclass
class InstitutionalAssetV2:
    """
    Physical shells with specific affordances.
    Staffed by humans whose loyalty and willingness
    to break rules are functions of Layer Zero,
    not institutional PR.

    The campus kitchen 400m away that never activates
    until day 3 — because policy + security + insurance
    prevent it — is not a resilience asset.
    It is a locked resource that generates resentment.

    staff_alignment determines whether the physical shell
    becomes community infrastructure or remains
    an institution protecting itself.

    policy_friction:
        Hours or probability that institutional policy
        prevents repurposing for community use.
        This is the variable that kills people
        while resources sit idle next door.
    """
    name: str                           = ""
    type: str                           = ""
    # "college" / "hospital" / "coop" / "industrial" / "faith"

    affordances: list[str]              = field(default_factory=list)
    # physical capabilities regardless of policy:
    # "heat_tolerant_kitchen" / "wet_lab" / "dorm_beds"
    # "bus_fleet" / "forklifts" / "cold_storage"
    # "backup_power" / "water_storage" / "shop_floor"
    # "broadcast_antenna" / "loading_dock"

    access_mode: AccessMode             = AccessMode.LOCKED
    staff_alignment: StaffAlignment     = StaffAlignment.INSTITUTION
    policy_friction_hours: float        = 0.0
    # hours before institutional policy allows community use
    # 0   = open immediately
    # 24  = one bureaucratic cycle
    # 72  = requires executive decision
    # 168 = requires board/legal approval
    # inf = will never open without external override

    backup_power: bool                  = False
    water_independent: bool             = False
    capacity: dict                      = field(default_factory=dict)
    # {"beds": 500, "meals_per_day": 2000, "parking": 300}

    seasonal_availability: dict         = field(default_factory=dict)
    # {"summer": 0.2, "fall": 1.0} — UW Madison summer skeleton

    def effective_activation_hours(self, zone: ResilienceFoundationV2) -> float:
        """
        When does this asset actually become usable?
        = max(policy_friction, intervention_arrival)
        
        If staff are neighborhood-aligned,
        they may open the building before policy authorizes it.
        That's the community override — and it saves lives.
        """
        if self.staff_alignment == StaffAlignment.NEIGHBORHOOD:
            # staff override policy when community needs it
            return zone.intervention_arrival_hours()
        if self.staff_alignment == StaffAlignment.SPLIT:
            # unpredictable — use average
            return (self.policy_friction_hours +
                    zone.intervention_arrival_hours()) / 2
        # institution-aligned: policy governs
        return max(self.policy_friction_hours,
                   zone.intervention_arrival_hours())

    def asset_summary(self, zone: ResilienceFoundationV2) -> dict:
        activation = self.effective_activation_hours(zone)
        return {
            "asset":            self.name,
            "access_mode":      self.access_mode.value,
            "staff_alignment":  self.staff_alignment.value,
            "policy_friction_h": self.policy_friction_hours,
            "effective_activation_h": round(activation, 1),
            "affordances":      self.affordances,
            "note": (
                "STAFF OVERRIDE LIKELY — neighborhood-aligned staff "
                "will open before policy authorizes"
                if self.staff_alignment == StaffAlignment.NEIGHBORHOOD
                else "POLICY GOVERNS — activation delayed by institutional friction"
            ),
        }


# ─── MADISON WI: V2 POPULATED ─────────────────────────────────────────────────

def build_madison_v2():
    """
    Madison WI in v2 schema.
    Layer Zero → infrastructure coupling explicit.
    Institutional assets as substrates, not saviors.
    """

    # ── ZONES ────────────────────────────────────────────────────────────────

    inner_city = ResilienceFoundationV2(
        zone="inner_city",
        population=40_000,
        social_trust_index=0.75,
        mutual_aid_active=True,
        knowledge_domains=["medical_triage","food_distribution","building_ops"],
        cognition=CognitiveReadinessV2(
            zone="inner_city",
            crew_density=28.0,
            adaptation_speed_hours=6.0,
            training_diversity=TrainingDiversity.MEDIUM,
        ),
        authority=DecisionAuthorityV2(
            zone="inner_city",
            authority_mode=AuthorityMode.DISTRIBUTED,
            decision_lag_hours=4.0,
            owner_resident_same=False,
            absentee_ownership_percent=0.70,
            community_override_likely=True,
        ),
        trust=SocialTrustV2(
            zone="inner_city",
            trust_span_households=45,
            norm_mode=NormMode.MIXED,
            conflict_load="low",
            # absentee ownership injects some transaction logic
            # but gratitude networks still dominant
            mirror_neuron_triggers=["witnessed_need","kinship","place_attachment"],
        ),
    )

    suburban = ResilienceFoundationV2(
        zone="suburban_sprawl",
        population=160_000,
        social_trust_index=0.25,
        mutual_aid_active=False,
        knowledge_domains=[],
        cognition=CognitiveReadinessV2(
            zone="suburban_sprawl",
            crew_density=4.0,
            adaptation_speed_hours=72.0,
            training_diversity=TrainingDiversity.LOW,
        ),
        authority=DecisionAuthorityV2(
            zone="suburban_sprawl",
            authority_mode=AuthorityMode.ABSENT,
            decision_lag_hours=36.0,
            owner_resident_same=False,
            absentee_ownership_percent=0.55,
            community_override_likely=False,
        ),
        trust=SocialTrustV2(
            zone="suburban_sprawl",
            trust_span_households=4,
            norm_mode=NormMode.TRANSACTION,
            conflict_load="moderate",
            # HOA vs renters / campus vs neighborhood tensions
            mirror_neuron_triggers=[],
        ),
    )

    rural_fringe = ResilienceFoundationV2(
        zone="rural_fringe",
        population=25_000,
        social_trust_index=0.85,
        mutual_aid_active=True,
        knowledge_domains=[
            "water_systems","food_preservation","equipment_repair",
            "medical_triage","animal_husbandry","fuel_management",
            "ice_navigation","oral_weather_prediction","soil_culture",
        ],
        cognition=CognitiveReadinessV2(
            zone="rural_fringe",
            crew_density=65.0,
            adaptation_speed_hours=3.0,
            training_diversity=TrainingDiversity.HIGH,
        ),
        authority=DecisionAuthorityV2(
            zone="rural_fringe",
            authority_mode=AuthorityMode.DISTRIBUTED,
            decision_lag_hours=1.0,
            owner_resident_same=True,
            absentee_ownership_percent=0.10,
            community_override_likely=True,
        ),
        trust=SocialTrustV2(
            zone="rural_fringe",
            trust_span_households=120,
            norm_mode=NormMode.GRATITUDE,
            conflict_load="none",
            mirror_neuron_triggers=[
                "witnessed_need","shared_hardship","kinship",
                "place_attachment","professional_identity",
            ],
        ),
    )

    zones = [inner_city, suburban, rural_fringe]

    # ── INFRASTRUCTURE LAYERS ────────────────────────────────────────────────

    infrastructure = [
        InfrastructureLayerV2(
            name="water",
            physical_buffer_hours=6.0,
            # pump stations on generator — extends to ~72h with fuel
            # but generator IS the redundancy, so buffer without it = 6h
            intervention_required_by_hours=4.0,
            recovery_complexity=RecoveryComplexity.MEDIUM,
            redundancy_level=1,
            institutional_backups=["UW_Madison","Willy_Street_Coop"],
            failure_cascade_targets=["medical","sewage","fire_suppression"],
        ),
        InfrastructureLayerV2(
            name="food",
            physical_buffer_hours=72.0,
            intervention_required_by_hours=48.0,
            recovery_complexity=RecoveryComplexity.MEDIUM,
            redundancy_level=1,
            institutional_backups=["Willy_Street_Coop","UW_cafeteria"],
            failure_cascade_targets=["medical","social"],
        ),
        InfrastructureLayerV2(
            name="energy",
            physical_buffer_hours=1.0,
            # grid goes down — buffer is essentially zero
            intervention_required_by_hours=0.5,
            recovery_complexity=RecoveryComplexity.HARD,
            redundancy_level=0,
            institutional_backups=["UW_Madison_backup"],
            failure_cascade_targets=["water","food","medical","comms"],
        ),
        InfrastructureLayerV2(
            name="medical",
            physical_buffer_hours=168.0,   # 7 days stockpile
            intervention_required_by_hours=120.0,
            recovery_complexity=RecoveryComplexity.HARD,
            redundancy_level=1,
            institutional_backups=["UW_Health","UW_nursing"],
            failure_cascade_targets=["social","economic"],
        ),
        InfrastructureLayerV2(
            name="comms",
            physical_buffer_hours=2.0,
            # cell towers have ~2-4h battery backup
            intervention_required_by_hours=1.0,
            recovery_complexity=RecoveryComplexity.HARD,
            redundancy_level=0,
            institutional_backups=[],
            failure_cascade_targets=["medical","social","institutional"],
        ),
        InfrastructureLayerV2(
            name="repair",
            physical_buffer_hours=720.0,   # 30 days before critical
            intervention_required_by_hours=480.0,
            recovery_complexity=RecoveryComplexity.MEDIUM,
            redundancy_level=0,
            institutional_backups=["UW_engineering"],
            failure_cascade_targets=["water","energy","food"],
        ),
    ]

    # ── INSTITUTIONAL ASSETS AS SUBSTRATES ───────────────────────────────────

    assets = [
        InstitutionalAssetV2(
            name="UW_Madison",
            type="college",
            affordances=[
                "heat_tolerant_kitchen","wet_lab","dorm_beds",
                "backup_power","shop_floor","cold_storage",
                "broadcast_capable","loading_dock","ag_land",
            ],
            access_mode=AccessMode.GATED,
            staff_alignment=StaffAlignment.SPLIT,
            # some staff neighborhood-aligned, some institution-aligned
            # depends on individual — unpredictable under stress
            policy_friction_hours=48.0,
            # community feeding from campus kitchen:
            # requires dean approval, insurance waiver, facilities sign-off
            # ~48h minimum in normal institutional timeline
            backup_power=True,
            water_independent=False,
            capacity={"beds": 10_000, "meals_per_day": 15_000},
            seasonal_availability={"summer": 0.2, "fall": 1.0, "winter": 0.85},
        ),
        InstitutionalAssetV2(
            name="UW_Health",
            type="hospital",
            affordances=[
                "trauma_capable","backup_power","sterile_environment",
                "cold_storage","pharmaceutical_stockpile","loading_dock",
            ],
            access_mode=AccessMode.GATED,
            staff_alignment=StaffAlignment.NEIGHBORHOOD,
            # medical staff will treat regardless of policy
            # this is the one institution where alignment holds under stress
            policy_friction_hours=2.0,
            backup_power=True,
            water_independent=False,
            capacity={"beds": 592, "surge_beds": 830},
        ),
        InstitutionalAssetV2(
            name="Willy_Street_Coop",
            type="coop",
            affordances=[
                "cold_storage","backup_power","distribution_infrastructure",
                "member_network","loading_dock","bulk_storage",
            ],
            access_mode=AccessMode.PUBLIC,
            staff_alignment=StaffAlignment.NEIGHBORHOOD,
            # coop structure — staff ARE community members
            # will open for community distribution before policy requires it
            policy_friction_hours=0.0,
            backup_power=True,
            water_independent=False,
            capacity={"distribution_per_day": 2_000, "storage_days": 14},
        ),
    ]

    return zones, infrastructure, assets


def print_v2_report(zones, infrastructure, assets):
    print(f"\n{'═'*66}")
    print(f"  URBAN RESILIENCE REPORT v2 — Madison WI")
    print(f"  Schema: crew_density | adaptation_speed | trust_span")
    print(f"  Coupling: physical_buffer → intervention_required_by → arrival")
    print(f"{'═'*66}")

    for zone in zones:
        print(f"\n  ── ZONE: {zone.zone.upper()}")
        print(f"     Load path        : {zone.cognition.cognitive_load_path()}")
        print(f"     Crew density     : {zone.cognition.crew_density:.0f}/1000 residents")
        print(f"     Effective crew   : {zone.cognition.effective_crew(zone.population):,} people")
        print(f"     Adaptation speed : {zone.cognition.adaptation_speed_hours:.0f}h")
        print(f"     Training divrsty : {zone.cognition.training_diversity.name}")
        print(f"     Authority mode   : {zone.authority.authority_mode.value}")
        print(f"     Decision lag     : {zone.authority.decision_lag_hours:.0f}h")
        print(f"     Runs forward     : {'✓ YES' if zone.authority.runs_forward() else '✗ NO'}")
        print(f"     Trust span       : {zone.trust.trust_span_households} households")
        print(f"     Norm mode        : {zone.trust.norm_mode.value}")
        print(f"     Conflict load    : {zone.trust.conflict_load}")
        print(f"     Cascade potential: {zone.trust.cascade_potential()}")
        print(f"     Entropy risk     : {zone.entropy_risk()}")
        print(f"     Intervention arr : {zone.intervention_arrival_hours():.0f}h")
        print(f"     Intervention qual: {zone.intervention_quality()}")

        print(f"\n     Infrastructure survival windows:")
        for layer in infrastructure:
            result = layer.compute_survival_window(zone)
            flag = " ⚠" if result["intervention_arrival_h"] > result["intervention_required_by_h"] else " ✓"
            print(f"       {result['layer']:<16} "
                  f"buffer {result['physical_buffer_h']:>5.0f}h → "
                  f"window {result['survival_window_h']:>6.1f}h "
                  f"({result['survival_window_d']:.1f}d){flag}")

    print(f"\n  INSTITUTIONAL ASSETS (as substrates):")
    for asset in assets:
        # use suburban zone as worst-case activation test
        suburban = [z for z in zones if z.zone == "suburban_sprawl"][0]
        summary = asset.asset_summary(suburban)
        print(f"\n    {asset.name}")
        print(f"      Access          : {summary['access_mode']}")
        print(f"      Staff alignment : {summary['staff_alignment']}")
        print(f"      Policy friction : {summary['policy_friction_h']:.0f}h")
        print(f"      Activation      : {summary['effective_activation_h']:.0f}h (suburban scenario)")
        print(f"      Affordances     : {', '.join(asset.affordances[:4])}...")
        print(f"      Note            : {summary['note']}")

    # KEY INSIGHT: show the suburban decision_lag intervention
    print(f"\n  KEY LEVER — SUBURBAN DECISION LAG REDUCTION:")
    suburban = [z for z in zones if z.zone == "suburban_sprawl"][0]
    water = [l for l in infrastructure if l.name == "water"][0]
    current = water.compute_survival_window(suburban)

    # simulate cutting decision lag from 36h to 4h
    from copy import deepcopy
    suburban_improved = deepcopy(suburban)
    suburban_improved.authority.decision_lag_hours = 4.0
    suburban_improved.authority.authority_mode = AuthorityMode.DISTRIBUTED
    improved = water.compute_survival_window(suburban_improved)

    print(f"    Water layer, suburban zone:")
    print(f"    Current  (36h lag): {current['survival_window_h']:.0f}h window")
    print(f"    Improved  (4h lag): {improved['survival_window_h']:.0f}h window")
    print(f"    Delta: +{improved['survival_window_h'] - current['survival_window_h']:.0f}h")
    print(f"    Method: establish distributed community council before crisis")
    print(f"    Cost: zero infrastructure spend")

    print(f"\n{'═'*66}\n")


if __name__ == "__main__":
    zones, infrastructure, assets = build_madison_v2()
    print_v2_report(zones, infrastructure, assets)
