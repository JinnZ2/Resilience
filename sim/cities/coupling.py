#!/usr/bin/env python3
# MODULE: sim/cities/coupling.py
# PROVIDES: RESILIENCE.COUPLING_EDGE, RESILIENCE.KNOWLEDGE_DECAY
# DEPENDS: stdlib-only
# RUN: python -m sim.cities.coupling
# TIER: domain
# Cross-domain coupling and cascade amplification dynamics
"""
sim/coupling.py — cross-domain coupling and cascade amplification
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Standard models assume other domains stay stable
while their domain fails.

Coupled systems don't fail that way.
Each shock depletes buffers that absorbed the last shock.
Each depletion makes the next shock larger.
Edge cases stack. Amplification compounds.
The model that missed the coupling on the way in
misses it on the way out too.
"""

from dataclasses import dataclass, field
from enum import Enum


class DomainType(Enum):
    CLIMATE        = "climate"
    FOOD           = "food"
    ENERGY         = "energy"
    ECONOMIC       = "economic"
    SOCIAL         = "social"
    INSTITUTIONAL  = "institutional"
    INFRASTRUCTURE = "infrastructure"
    KNOWLEDGE      = "knowledge"      # the one MIT doesn't model


class ShockMagnitude(Enum):
    MINOR    = 0.1
    MODERATE = 0.3
    MAJOR    = 0.6
    EXTREME  = 0.9


@dataclass
class DomainState:
    """
    Current condition of a single domain.
    Buffer capacity is what absorbs shocks without cascade.
    Buffer depletes with each shock and regenerates slowly.
    Standard models assume full buffer always.
    """
    domain: DomainType
    baseline_capacity: float        = 1.0   # 0.0-1.0
    current_capacity: float         = 1.0
    buffer_remaining: float         = 1.0   # absorbs shocks before cascade
    buffer_regen_rate_per_year: float = 0.1  # how fast buffer rebuilds
    # knowledge domain: 0.02 — one generation to rebuild
    # economic domain:  0.15 — recovers faster with right conditions
    # social domain:    0.05 — trust rebuilds slowly
    
    shock_history: list[float]      = field(default_factory=list)
    # each entry depletes buffer permanently if regen < depletion rate
    
    def absorb_shock(self, magnitude: float) -> float:
        """
        Returns spillover — amount that exceeds buffer capacity
        and cascades into coupled domains.
        """
        if self.buffer_remaining >= magnitude:
            self.buffer_remaining -= magnitude
            self.shock_history.append(magnitude)
            return 0.0                          # fully absorbed
        else:
            spillover = magnitude - self.buffer_remaining
            self.buffer_remaining = 0.0
            self.current_capacity *= (1 - spillover)
            self.shock_history.append(magnitude)
            return spillover                    # cascades outward

    def stress_level(self) -> float:
        return 1.0 - self.current_capacity

    def buffer_depleted(self) -> bool:
        return self.buffer_remaining < 0.05


@dataclass
class CouplingEdge:
    """
    How shock in one domain amplifies into another.
    Amplification factor > 1.0 means the receiving domain
    gets hit harder than the source shock.

    These couplings are what standard single-domain models miss.
    """
    source: DomainType
    target: DomainType
    amplification: float            # how much spillover amplifies in target
    lag_days: float                 # how long before coupling manifests
    description: str                = ""
    # example:
    # climate → food: 1.4 amplification, 90 day lag
    # (drought hits harvest 3 months after it starts)
    # food → economic: 1.6 amplification, 30 day lag
    # (food price spike hits purchasing power fast)
    # economic → social: 1.3 amplification, 60 day lag
    # (financial stress degrades trust networks over months)


@dataclass
class KnowledgeDecayLayer:
    """
    The variable MIT doesn't model.
    The actual countdown clock.

    Industrial agriculture didn't just replace small farms.
    It replaced the knowledge of how to farm without it.
    That took two generations.
    Rebuilding takes at least one generation of sustained
    practice under mentorship.

    When the industrial measurement layer collapses,
    what remains is only what was transmitted person to person
    before the transmission chain broke.
    """
    domain: str
    knowledge_holders_current: int
    knowledge_holders_peak: int
    annual_loss_rate: float         # % lost per year to age/migration/death
    transmission_rate: float        # % successfully transmitted per year
    # if loss_rate > transmission_rate: net decay
    # if transmission_rate > loss_rate: net growth
    
    years_to_critical_loss: float   = 0.0
    # point where remaining holders can't transmit fast enough
    # to replace losses even if conditions improve
    
    embodied_vs_documented: float   = 0.9
    # 0.9 = 90% of this knowledge exists only in people, not text
    # when holders die, knowledge dies with them
    # YouTube videos of grandmothers making bread
    # are not the same as apprenticing with the grandmother

    def net_decay_rate(self) -> float:
        return self.annual_loss_rate - self.transmission_rate

    def transmission_window_years(self) -> float:
        """
        How many years before the knowledge base
        drops below minimum viable for reconstruction.
        """
        if self.net_decay_rate() <= 0:
            return float('inf')     # growing or stable
        viable_threshold = 0.20     # 20% of peak = minimum viable
        current_ratio = self.knowledge_holders_current / self.knowledge_holders_peak
        decay_to_threshold = current_ratio - viable_threshold
        if decay_to_threshold <= 0:
            return 0.0              # already below threshold
        return decay_to_threshold / self.net_decay_rate()


@dataclass
class CoupledSystemState:
    """
    All domains simultaneously.
    Shocks propagate through coupling edges.
    Buffer depletion compounds over time.
    Knowledge decay runs underneath everything.

    This is the model standard frameworks don't build
    because it requires admitting that domains
    are not independent and that history matters.
    """
    city: str
    domains: dict                   = field(default_factory=dict)
    # DomainType → DomainState
    coupling_edges: list[CouplingEdge] = field(default_factory=list)
    knowledge_layers: list[KnowledgeDecayLayer] = field(default_factory=list)
    
    # shock event log
    event_log: list[dict]           = field(default_factory=list)

    def apply_shock(
        self,
        domain: DomainType,
        magnitude: float,
        day: int,
        description: str = "",
    ):
        """
        Apply shock to one domain.
        Calculate spillover.
        Propagate through coupling edges.
        Log everything.
        """
        if domain not in self.domains:
            return

        ds = self.domains[domain]
        spillover = ds.absorb_shock(magnitude)

        self.event_log.append({
            "day": day,
            "domain": domain.value,
            "magnitude": magnitude,
            "spillover": spillover,
            "buffer_remaining": ds.buffer_remaining,
            "description": description,
        })

        # propagate spillover through coupling edges
        if spillover > 0:
            for edge in self.coupling_edges:
                if edge.source == domain:
                    amplified = spillover * edge.amplification
                    target_ds = self.domains.get(edge.target)
                    if target_ds:
                        cascade_spillover = target_ds.absorb_shock(amplified)
                        self.event_log.append({
                            "day": day + edge.lag_days,
                            "domain": edge.target.value,
                            "magnitude": amplified,
                            "spillover": cascade_spillover,
                            "buffer_remaining": target_ds.buffer_remaining,
                            "description": f"cascade from {domain.value}: {edge.description}",
                        })

    def system_stress(self) -> dict:
        return {
            d.value: self.domains[d].stress_level()
            for d in self.domains
        }

    def depleted_buffers(self) -> list[str]:
        return [
            d.value for d in self.domains
            if self.domains[d].buffer_depleted()
        ]

    def knowledge_countdown(self) -> dict:
        return {
            kl.domain: {
                "window_years": kl.transmission_window_years(),
                "net_decay_rate": kl.net_decay_rate(),
                "holders_remaining": kl.knowledge_holders_current,
                "embodied_only_pct": kl.embodied_vs_documented * 100,
            }
            for kl in self.knowledge_layers
        }


def build_madison_coupled_system() -> CoupledSystemState:
    """
    Madison WI coupled domain state.
    Pre-loaded with current estimated stress levels
    based on route observation and public data.
    """
    system = CoupledSystemState(city="Madison_WI")

    # current domain states — buffers already partially depleted
    # by prior shocks: COVID supply chain, 2020-2024 inflation,
    # grid stress events, social fragmentation trends
    system.domains = {
        DomainType.CLIMATE:        DomainState(
            domain=DomainType.CLIMATE,
            current_capacity=0.75,
            buffer_remaining=0.55,
            buffer_regen_rate_per_year=0.05,  # slow — physical systems
        ),
        DomainType.FOOD:           DomainState(
            domain=DomainType.FOOD,
            current_capacity=0.70,
            buffer_remaining=0.40,            # supply chain shocks depleted this
            buffer_regen_rate_per_year=0.12,
        ),
        DomainType.ENERGY:         DomainState(
            domain=DomainType.ENERGY,
            current_capacity=0.72,
            buffer_remaining=0.45,
            buffer_regen_rate_per_year=0.08,
        ),
        DomainType.ECONOMIC:       DomainState(
            domain=DomainType.ECONOMIC,
            current_capacity=0.65,
            buffer_remaining=0.35,            # inflation + debt depleted
            buffer_regen_rate_per_year=0.15,
        ),
        DomainType.SOCIAL:         DomainState(
            domain=DomainType.SOCIAL,
            current_capacity=0.55,
            buffer_remaining=0.30,            # fragmentation accelerating
            buffer_regen_rate_per_year=0.05,  # trust rebuilds very slowly
        ),
        DomainType.INSTITUTIONAL:  DomainState(
            domain=DomainType.INSTITUTIONAL,
            current_capacity=0.50,
            buffer_remaining=0.25,            # legitimacy crisis depleted
            buffer_regen_rate_per_year=0.07,
        ),
        DomainType.INFRASTRUCTURE: DomainState(
            domain=DomainType.INFRASTRUCTURE,
            current_capacity=0.68,
            buffer_remaining=0.40,
            buffer_regen_rate_per_year=0.06,
        ),
        DomainType.KNOWLEDGE:      DomainState(
            domain=DomainType.KNOWLEDGE,
            current_capacity=0.45,            # significant loss already occurred
            buffer_remaining=0.20,            # very thin — elders dying faster than transmission
            buffer_regen_rate_per_year=0.02,  # one generation to rebuild
        ),
    }

    # coupling edges — how shocks amplify across domains
    system.coupling_edges = [
        CouplingEdge(DomainType.CLIMATE, DomainType.FOOD,
            amplification=1.4, lag_days=90,
            description="drought/flood hits harvest 3 months later"),
        CouplingEdge(DomainType.CLIMATE, DomainType.INFRASTRUCTURE,
            amplification=1.3, lag_days=7,
            description="extreme weather stresses grid and roads directly"),
        CouplingEdge(DomainType.FOOD, DomainType.ECONOMIC,
            amplification=1.6, lag_days=30,
            description="food price spike hits purchasing power fast"),
        CouplingEdge(DomainType.FOOD, DomainType.SOCIAL,
            amplification=1.5, lag_days=45,
            description="food insecurity degrades social cohesion"),
        CouplingEdge(DomainType.ENERGY, DomainType.FOOD,
            amplification=1.8, lag_days=3,
            description="grid failure hits cold storage and distribution immediately"),
        CouplingEdge(DomainType.ENERGY, DomainType.INFRASTRUCTURE,
            amplification=2.0, lag_days=1,
            description="grid failure IS infrastructure failure — direct coupling"),
        CouplingEdge(DomainType.ECONOMIC, DomainType.SOCIAL,
            amplification=1.3, lag_days=60,
            description="financial stress degrades trust networks over months"),
        CouplingEdge(DomainType.ECONOMIC, DomainType.INSTITUTIONAL,
            amplification=1.4, lag_days=90,
            description="economic crisis accelerates institutional legitimacy loss"),
        CouplingEdge(DomainType.ECONOMIC, DomainType.INFRASTRUCTURE,
            amplification=1.2, lag_days=180,
            description="deferred maintenance when budgets cut"),
        CouplingEdge(DomainType.SOCIAL, DomainType.INSTITUTIONAL,
            amplification=1.5, lag_days=30,
            description="social fragmentation accelerates institutional collapse"),
        CouplingEdge(DomainType.SOCIAL, DomainType.KNOWLEDGE,
            amplification=1.6, lag_days=365,
            description="fragmentation breaks transmission chains — knowledge dies with holders"),
        CouplingEdge(DomainType.INSTITUTIONAL, DomainType.INFRASTRUCTURE,
            amplification=1.3, lag_days=90,
            description="institutional failure means no one coordinates maintenance"),
        CouplingEdge(DomainType.KNOWLEDGE, DomainType.FOOD,
            amplification=1.9, lag_days=730,
            description="knowledge loss hits food production 2 years later when no one knows how to grow without industrial inputs"),
        CouplingEdge(DomainType.KNOWLEDGE, DomainType.INFRASTRUCTURE,
            amplification=1.7, lag_days=365,
            description="knowledge loss means no one can repair systems without supply chain"),
    ]

    # knowledge decay layers — the actual countdown clocks
    system.knowledge_layers = [
        KnowledgeDecayLayer(
            domain="soil_culture_upper_midwest",
            knowledge_holders_current=12_000,
            knowledge_holders_peak=180_000,
            annual_loss_rate=0.06,
            transmission_rate=0.02,
            years_to_critical_loss=8.0,
            embodied_vs_documented=0.92,
        ),
        KnowledgeDecayLayer(
            domain="water_system_manual_ops",
            knowledge_holders_current=800,
            knowledge_holders_peak=4_000,
            annual_loss_rate=0.05,
            transmission_rate=0.03,
            years_to_critical_loss=12.0,
            embodied_vs_documented=0.85,
        ),
        KnowledgeDecayLayer(
            domain="food_preservation_without_grid",
            knowledge_holders_current=25_000,
            knowledge_holders_peak=400_000,
            annual_loss_rate=0.07,
            transmission_rate=0.015,
            years_to_critical_loss=6.0,
            embodied_vs_documented=0.95,
        ),
        KnowledgeDecayLayer(
            domain="equipment_repair_without_supply_chain",
            knowledge_holders_current=18_000,
            knowledge_holders_peak=120_000,
            annual_loss_rate=0.055,
            transmission_rate=0.025,
            years_to_critical_loss=10.0,
            embodied_vs_documented=0.88,
        ),
        KnowledgeDecayLayer(
            domain="indigenous_ecological_knowledge_upper_midwest",
            knowledge_holders_current=400,
            knowledge_holders_peak=15_000,
            annual_loss_rate=0.08,
            transmission_rate=0.04,
            years_to_critical_loss=5.0,
            embodied_vs_documented=0.98,
            # almost entirely oral/practice — not in any database
        ),
    ]

    return system


def print_coupled_report(system: CoupledSystemState):
    print(f"\n{'═'*66}")
    print(f"  COUPLED DOMAIN REPORT: {system.city}")
    print(f"{'═'*66}")

    print(f"\n  DOMAIN STRESS LEVELS (current):")
    stress = system.system_stress()
    for domain, level in sorted(stress.items(), key=lambda x: -x[1]):
        bar = "█" * int(level * 20)
        print(f"    {domain:<20} {level:.0%}  {bar}")

    depleted = system.depleted_buffers()
    if depleted:
        print(f"\n  ⚠ BUFFERS DEPLETED — next shock cascades directly:")
        for d in depleted:
            print(f"    {d}")

    print(f"\n  KNOWLEDGE COUNTDOWN CLOCKS:")
    countdown = system.knowledge_countdown()
    for domain, data in sorted(
        countdown.items(), key=lambda x: x[1]["window_years"]
    ):
        yrs = data["window_years"]
        yr_str = f"{yrs:.1f} years" if yrs != float('inf') else "stable"
        print(f"    {domain}")
        print(f"      Window remaining : {yr_str}")
        print(f"      Net decay rate   : {data['net_decay_rate']:.1%}/yr")
        print(f"      Holders remaining: {data['holders_remaining']:,}")
        print(f"      Embodied only    : {data['embodied_only_pct']:.0f}%")

    if system.event_log:
        print(f"\n  CASCADE EVENT LOG:")
        for event in sorted(system.event_log, key=lambda x: x["day"]):
            spill = f" → spillover {event['spillover']:.2f}" if event['spillover'] > 0 else ""
            print(f"    Day {event['day']:>4} | {event['domain']:<20} "
                  f"shock {event['magnitude']:.2f}{spill}")
            if event['description']:
                print(f"           {event['description']}")

    print(f"\n{'═'*66}\n")


if __name__ == "__main__":
    system = build_madison_coupled_system()

    # simulate stacking edge case events — 2026-2030
    events = [
        (DomainType.CLIMATE,    0.3,  30,  "late spring drought begins"),
        (DomainType.ENERGY,     0.4,  45,  "grid stress event — heat demand spike"),
        (DomainType.FOOD,       0.3,  120, "harvest shortfall — drought impact"),
        (DomainType.ECONOMIC,   0.3,  150, "food price cascade hits purchasing power"),
        (DomainType.CLIMATE,    0.5,  200, "early winter storm — infrastructure stress"),
        (DomainType.ENERGY,     0.5,  205, "grid failure — 72 hour event"),
        (DomainType.SOCIAL,     0.3,  240, "social fragmentation accelerates"),
        (DomainType.INSTITUTIONAL, 0.4, 300, "institutional response failure exposed"),
    ]

    for domain, magnitude, day, description in events:
        system.apply_shock(domain, magnitude, day, description)

    print_coupled_report(system)
