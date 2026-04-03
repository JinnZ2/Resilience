#!/usr/bin/env python3
# MODULE: sim/domains/incentive_alignment.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: python -m sim.domains.incentive_alignment
# TIER: domain
# Incentive structure alignment for regeneration vs extraction
"""
sim/domains/incentive_alignment.py
Urban Resilience Simulator — Incentive Layer
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

The problem is not knowledge loss.
The problem is that the incentive structure
points backwards.

It rewards extraction over regeneration.
It rewards capital intensity over thermodynamic efficiency.
It rewards what shows up in quarterly earnings
over what keeps people alive.

You cannot fix knowledge decay
by teaching people ice storage
if the economy still pays them more to pave the land.

This module models incentive alignment as infrastructure.
Not ethics. Physics.
"""

from dataclasses import dataclass, field
from enum import Enum


class IncentiveType(Enum):
    EXTRACTION    = "extraction"     # rewards consuming substrate
    NEUTRAL       = "neutral"        # no signal either direction
    REGENERATIVE  = "regenerative"   # rewards building substrate


class SignalSource(Enum):
    MARKET        = "market"         # price signals
    REGULATORY    = "regulatory"     # policy/law
    SOCIAL        = "social"         # community obligation
    THERMODYNAMIC = "thermodynamic"  # physical reality
    KNOWLEDGE     = "knowledge"      # embodied competence valued


@dataclass
class IncentiveSignal:
    """
    A single signal pointing toward or away from
    substrate maintenance.

    strength: -1.0 (pure extraction) to +1.0 (pure regeneration)
    reach:    fraction of population receiving signal
    lag:      years before signal becomes visible
    decay:    does signal weaken over time?
    """
    signal_id:    str
    source:       SignalSource
    itype:        IncentiveType
    strength:     float          # -1.0 to +1.0
    reach:        float          # 0.0-1.0 fraction of population
    lag_years:    int            # years before consequences visible
    description:  str


@dataclass
class KnowledgeDomain:
    """
    A body of knowledge that keeps infrastructure viable.
    Ice storage. Passive cooling. Soil management.
    Food preservation. Heat retention without fuel.

    current_holders: people alive who carry this knowledge
    transmission_rate: new people learning per year
    decay_rate: holders retiring/dying per year
    market_signal: what does the economy pay for this? (-1 to +1)
    social_signal: what does the community value for this? (-1 to +1)
    """
    domain_id:          str
    description:        str
    current_holders:    int
    minimum_viable:     int      # below this: knowledge effectively gone
    transmission_rate:  float    # new holders per year
    decay_rate:         float    # holders lost per year
    market_signal:      float    # -1.0 to +1.0
    social_signal:      float    # -1.0 to +1.0
    enables:            list[str] = field(default_factory=list)  # what this unlocks

    def net_holder_change(self) -> float:
        return self.transmission_rate - self.decay_rate

    def years_to_critical(self) -> float:
        """Years until below minimum viable at current trajectory."""
        if self.net_holder_change() >= 0:
            return float('inf')
        gap = self.current_holders - self.minimum_viable
        return gap / abs(self.net_holder_change())

    def composite_incentive(self) -> float:
        """
        What signal is the world sending about learning this?
        Market dominates in current system.
        Social signal matters in intact communities.
        """
        return (self.market_signal * 0.75) + (self.social_signal * 0.25)

    def will_survive(self) -> bool:
        """
        Will this knowledge domain survive 30 years
        at current incentive alignment?
        """
        if self.composite_incentive() > 0.2:
            return True
        if self.current_holders > self.minimum_viable * 3:
            return True
        return self.years_to_critical() > 30


@dataclass
class CompensationMechanism:
    """
    What do you give people in exchange for maintaining
    knowledge and practices the market doesn't price?

    Not charity. Exchange.
    Thermodynamic handshake.
    You maintain the substrate,
    the community guarantees your substrate.
    """
    mechanism_id:   str
    description:    str
    provides:       list[str]    # what the community provides
    requires:       list[str]    # what the knowledge holder provides
    reach:          float        # fraction of holders this reaches
    market_delta:   float        # how much this shifts market signal
    social_delta:   float        # how much this shifts social signal


@dataclass
class IncentiveSystem:
    """
    The full incentive map for a region.
    Shows why knowledge dies.
    Shows what would have to change.
    Shows what compensation makes regeneration rational.
    """
    region_id:      str
    domains:        dict[str, KnowledgeDomain]       = field(default_factory=dict)
    signals:        list[IncentiveSignal]             = field(default_factory=list)
    compensation:   list[CompensationMechanism]       = field(default_factory=list)

    def domains_at_risk(self) -> list[KnowledgeDomain]:
        return [
            d for d in self.domains.values()
            if not d.will_survive()
        ]

    def cascade_map(self) -> dict[str, list[str]]:
        """
        If domain X dies, what else dies with it?
        Follows enables[] chains.
        """
        at_risk = {d.domain_id for d in self.domains_at_risk()}
        cascade = {}
        for domain_id in at_risk:
            domain = self.domains[domain_id]
            cascade[domain_id] = domain.enables
        return cascade

    def incentive_gap(self, domain_id: str) -> float:
        """
        How far is the current incentive signal
        from the minimum needed to sustain transmission?
        Minimum viable composite signal: ~0.15
        """
        domain = self.domains[domain_id]
        return domain.composite_incentive() - 0.15

    def apply_compensation(self, mechanism: CompensationMechanism):
        """
        Apply a compensation mechanism and show
        what changes.
        """
        for domain in self.domains.values():
            for requirement in mechanism.requires:
                if requirement in domain.domain_id or requirement in domain.description:
                    domain.market_signal = min(
                        1.0,
                        domain.market_signal + mechanism.market_delta * mechanism.reach
                    )
                    domain.social_signal = min(
                        1.0,
                        domain.social_signal + mechanism.social_delta * mechanism.reach
                    )

    def print_report(self):
        print(f"\n{'═'*66}")
        print(f"  INCENTIVE ALIGNMENT REPORT — {self.region_id}")
        print(f"  What the system is telling people to learn.")
        print(f"  What they need to learn to survive.")
        print(f"  The gap between those two things.")
        print(f"{'═'*66}")

        print(f"\n  KNOWLEDGE DOMAINS — CURRENT INCENTIVE ALIGNMENT:")
        print(f"  {'Domain':<32} {'Signal':>8} {'Holders':>8} {'Yrs Left':>10} {'Survive?':>10}")
        print(f"  {'─'*70}")

        for domain in sorted(
            self.domains.values(),
            key=lambda d: d.composite_incentive()
        ):
            ytc = domain.years_to_critical()
            ytc_str = f"{ytc:.0f}" if ytc != float('inf') else "stable"
            survive = "YES" if domain.will_survive() else "NO ←"
            signal = domain.composite_incentive()
            signal_str = f"{signal:+.2f}"
            print(
                f"  {domain.domain_id:<32} {signal_str:>8} "
                f"{domain.current_holders:>8} {ytc_str:>10} {survive:>10}"
            )

        print(f"\n  CASCADE RISK MAP:")
        cascade = self.cascade_map()
        if not cascade:
            print(f"    No cascades identified.")
        for domain_id, enables in cascade.items():
            print(f"\n    {domain_id} dies →")
            for e in enables:
                print(f"      → {e} at risk")

        print(f"\n  INCENTIVE GAPS (how far from minimum viable signal):")
        for domain_id, domain in self.domains.items():
            gap = self.incentive_gap(domain_id)
            bar = "█" * int(abs(gap) * 20)
            direction = "above" if gap >= 0 else "BELOW"
            print(f"    {domain_id:<32} {gap:+.3f} {direction} threshold  {bar}")

        print(f"\n{'═'*66}\n")


# ─── SUPERIOR-TOMAH CORRIDOR BUILD ───────────────────────────────────────────

def build_superior_tomah_corridor() -> IncentiveSystem:
    system = IncentiveSystem(region_id="superior_tomah_corridor")

    system.domains = {

        "ice_storage_passive_cooling": KnowledgeDomain(
            domain_id="ice_storage_passive_cooling",
            description="Ice harvest, cave storage, evaporative clay cooling, passive icehouse geometry",
            current_holders=4,
            minimum_viable=3,
            transmission_rate=0.1,   # almost nobody learning this
            decay_rate=0.4,          # holders aging out fast
            market_signal=-0.6,      # market pays you to buy industrial refrigeration
            social_signal=0.3,       # some community value
            enables=[
                "food_cold_chain_independence",
                "pharmaceutical_storage_backup",
                "dairy_without_grid_power",
            ],
        ),

        "ammonium_absorption_cooling": KnowledgeDomain(
            domain_id="ammonium_absorption_cooling",
            description="Ammonia refrigeration systems — 1800s technology, still thermodynamically superior",
            current_holders=2,
            minimum_viable=2,
            transmission_rate=0.05,
            decay_rate=0.3,
            market_signal=-0.7,      # regulatory friction + HVAC industry incumbency
            social_signal=0.1,
            enables=[
                "large_scale_cooling_without_freon",
                "food_warehouse_independence",
            ],
        ),

        "passive_solar_heating": KnowledgeDomain(
            domain_id="passive_solar_heating",
            description="Thermal mass, south-facing geometry, heat retention without fuel",
            current_holders=12,
            minimum_viable=5,
            transmission_rate=0.8,   # some revival happening
            decay_rate=0.6,
            market_signal=-0.2,      # market slightly negative (insulation industry)
            social_signal=0.6,
            enables=[
                "winter_survival_without_propane",
                "building_stock_resilience",
            ],
        ),

        "food_preservation_ferment_dry_smoke": KnowledgeDomain(
            domain_id="food_preservation_ferment_dry_smoke",
            description="Fermentation, drying, smoking, root cellar management — multi-season food security",
            current_holders=18,
            minimum_viable=8,
            transmission_rate=1.2,   # fermentation revival real
            decay_rate=0.8,
            market_signal=-0.1,
            social_signal=0.7,
            enables=[
                "food_security_without_cold_chain",
                "seed_preservation",
                "nutritional_independence",
            ],
        ),

        "soil_terra_parita": KnowledgeDomain(
            domain_id="soil_terra_parita",
            description="Generational soil management — mycorrhizal network maintenance, rotation, clay/peat specifics",
            current_holders=6,
            minimum_viable=4,
            transmission_rate=0.2,
            decay_rate=0.5,
            market_signal=-0.5,      # industrial ag inputs more profitable short-term
            social_signal=0.4,
            enables=[
                "regional_food_production",
                "water_filtration",
                "carbon_sequestration",
                "flood_mitigation",
            ],
        ),

        "water_sourcing_treatment_low_tech": KnowledgeDomain(
            domain_id="water_sourcing_treatment_low_tech",
            description="Spring identification, gravity-fed systems, biochar filtration, constructed wetlands",
            current_holders=5,
            minimum_viable=3,
            transmission_rate=0.2,
            decay_rate=0.4,
            market_signal=-0.4,
            social_signal=0.5,
            enables=[
                "potable_water_without_municipal",
                "agricultural_water_independence",
            ],
        ),

        "cb_ham_lora_mesh_comms": KnowledgeDomain(
            domain_id="cb_ham_lora_mesh_comms",
            description="CB radio, HAM, LoRa mesh — communication without internet or cell towers",
            current_holders=22,
            minimum_viable=8,
            transmission_rate=1.5,   # HAM community reasonably active
            decay_rate=0.9,
            market_signal=0.0,
            social_signal=0.5,
            enables=[
                "coordination_without_internet",
                "emergency_communication",
                "logistics_routing_backup",
            ],
        ),

        "animal_husbandry_draft_power": KnowledgeDomain(
            domain_id="animal_husbandry_draft_power",
            description="Draft horses, oxen — farming without diesel, transport without fuel",
            current_holders=3,
            minimum_viable=3,
            transmission_rate=0.1,
            decay_rate=0.3,
            market_signal=-0.8,      # diesel cheaper until it isn't
            social_signal=0.2,
            enables=[
                "agriculture_without_diesel",
                "timber_extraction_without_equipment",
                "transport_backup",
            ],
        ),

        "medicinal_plant_knowledge": KnowledgeDomain(
            domain_id="medicinal_plant_knowledge",
            description="Regional medicinal plants — northern Minnesota specific, indigenous knowledge base",
            current_holders=8,
            minimum_viable=4,
            transmission_rate=0.5,
            decay_rate=0.6,
            market_signal=-0.3,
            social_signal=0.7,
            enables=[
                "healthcare_without_supply_chain",
                "wound_treatment_backup",
            ],
        ),

    }

    # compensation mechanisms — what would actually shift incentives
    system.compensation = [

        CompensationMechanism(
            mechanism_id="food_security_guarantee",
            description=(
                "Community guarantees: you will not go hungry, "
                "in exchange for: you teach what you know."
            ),
            provides=["food security", "medical access", "fuel allocation priority"],
            requires=["active teaching", "knowledge documentation", "apprentice support"],
            reach=0.6,
            market_delta=0.3,
            social_delta=0.5,
        ),

        CompensationMechanism(
            mechanism_id="knowledge_apprenticeship_wage",
            description=(
                "Pay apprenticeship wages from regional resilience fund. "
                "Learning ice storage pays as well as retail. "
                "Not charity — substrate investment."
            ),
            provides=["living wage during apprenticeship", "housing priority", "tool access"],
            requires=["3yr apprenticeship commitment", "documented knowledge transfer"],
            reach=0.4,
            market_delta=0.6,
            social_delta=0.3,
        ),

        CompensationMechanism(
            mechanism_id="property_tax_exemption_regenerative",
            description=(
                "Zero property tax for land under documented regenerative management. "
                "Development pressure is a tax problem as much as a values problem."
            ),
            provides=["property tax exemption", "development pressure relief"],
            requires=["soil regeneration documentation", "open inspection"],
            reach=0.5,
            market_delta=0.5,
            social_delta=0.2,
        ),

    ]

    return system


if __name__ == "__main__":
    system = build_superior_tomah_corridor()
    system.print_report()

    print("\n  APPLYING COMPENSATION MECHANISMS...\n")
    for mechanism in system.compensation:
        system.apply_compensation(mechanism)
        print(f"  Applied: {mechanism.mechanism_id}")
        print(f"    Provides: {', '.join(mechanism.provides)}")
        print(f"    Requires: {', '.join(mechanism.requires)}")

    print("\n  POST-COMPENSATION INCENTIVE ALIGNMENT:\n")
    system.print_report()
