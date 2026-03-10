#!/usr/bin/env python3
"""
sim/economics.py — thermodynamic economics layer
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Standard economics measures transaction volume.
This measures substrate flow direction.

GDP counts a hospital bill and a harvest equally.
A derivative and a seed bank equally.
Clearcutting and planting equally.
Destroying a knowledge holder's community
and building a hospital in it equally.

The measurement is blind to direction.
This isn't.

One question applied consistently:
After this transaction, is the substrate more or less
capable of supporting life next year than it was this year?

That single question inverts most of what
standard economics recommends.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class FlowDirection(Enum):
    REGENERATIVE = "regenerative"   # builds substrate
    NEUTRAL      = "neutral"        # maintains substrate
    EXTRACTIVE   = "extractive"     # depletes substrate
    UNKNOWN      = "unknown"        # not yet classified

class InstitutionStatus(Enum):
    VALIDATED  = "validated"    # exports more useful work than consumes
    NEUTRAL    = "neutral"      # breaks even on substrate
    CAPTURED   = "captured"     # optimized for self-continuation
    # not helped to grow
    # receives only recovery interventions

class TransactionType(Enum):
    KNOWLEDGE_TRANSMISSION  = "knowledge_transmission"
    SUBSTRATE_MAINTENANCE   = "substrate_maintenance"
    CARRYING_CAPACITY       = "carrying_capacity"
    GRATITUDE_EXCHANGE      = "gratitude_exchange"
    NEUTRAL_EXCHANGE        = "neutral_exchange"
    MEASUREMENT_LAYER       = "measurement_layer"   # money pricing money
    EXTRACTION              = "extraction"
    COMMONS_DESTRUCTION     = "commons_destruction"


# ─── CORE: THERMODYNAMIC LEDGER ───────────────────────────────────────────────

@dataclass
class SubstrateTransaction:
    """
    Every transaction classified by direction.
    Not by dollar value.

    Standard accounting: revenue + / expense -
    Thermodynamic accounting: substrate built + / substrate depleted -

    These are not the same sign.
    A profitable transaction can be deeply substrate-negative.
    A money-losing transaction can be profoundly substrate-positive.

    The grandmother teaching food preservation:
    GDP: zero.
    Thermodynamic ledger: +enormous.
    The knowledge survives her.

    The pharmaceutical company managing a curable condition:
    GDP: +billions annually.
    Thermodynamic ledger: -because substrate (human health capacity)
    declines while measurement layer grows.
    """
    description: str                        = ""
    transaction_type: TransactionType       = TransactionType.NEUTRAL_EXCHANGE
    direction: FlowDirection               = FlowDirection.UNKNOWN

    monetary_value: float                   = 0.0   # dollars — almost irrelevant
    substrate_value: float                  = 0.0
    # positive = builds carrying capacity
    # negative = depletes carrying capacity
    # scale: person-years of survival capacity affected

    knowledge_impact: float                 = 0.0
    # positive = knowledge transmitted or preserved
    # negative = knowledge destroyed or blocked
    # zero = knowledge unaffected

    gratitude_network_impact: float         = 0.0
    # positive = open loops created or strengthened
    # negative = gratitude converted to transaction, circuit closed

    commons_impact: float                   = 0.0
    # aquifer, soil, air, social trust, knowledge commons
    # negative = commons depleted
    # positive = commons restored

    time_horizon_years: int                 = 1
    # how long does this transaction's effect persist?
    # knowledge transmission: generational (25+ years)
    # aquifer depletion: decades
    # gratitude network damage: years
    # financial transaction: days to months

    def thermodynamic_value(self) -> float:
        """
        Actual value regardless of monetary expression.
        Weighted by time horizon — long-duration effects matter more.
        """
        horizon_weight = min(self.time_horizon_years / 10, 3.0)
        return (
            self.substrate_value +
            self.knowledge_impact * 2.0 +      # knowledge compounds
            self.gratitude_network_impact * 1.5 +
            self.commons_impact * 1.8
        ) * horizon_weight

    def inverted(self) -> bool:
        """
        True if money flows opposite to substrate value.
        This is the inversion that breaks systems.
        High monetary value + negative thermodynamic value =
        profitable extraction.
        """
        if self.monetary_value > 0 and self.thermodynamic_value() < 0:
            return True
        if self.monetary_value < 0 and self.thermodynamic_value() > 0:
            return True
        return False


@dataclass
class ThermodynamicLedger:
    """
    Running account of substrate flow.
    Replaces GDP as primary economic metric.

    GDP: sum of transaction monetary values (direction-blind)
    Thermodynamic ledger: sum of substrate flow (direction-aware)

    A community can have declining GDP and improving substrate.
    A community can have growing GDP and collapsing substrate.
    Standard economics cannot distinguish these.
    This can.
    """
    zone: str                               = ""
    transactions: list[SubstrateTransaction] = field(default_factory=list)

    def add(self, t: SubstrateTransaction):
        self.transactions.append(t)

    def gdp_equivalent(self) -> float:
        """What standard economics sees."""
        return sum(abs(t.monetary_value) for t in self.transactions)

    def net_substrate_flow(self) -> float:
        """What actually matters."""
        return sum(t.thermodynamic_value() for t in self.transactions)

    def extraction_ratio(self) -> float:
        """
        Extractive transaction value / regenerative transaction value.
        > 1.0 = extracting faster than regenerating.
        < 1.0 = regenerating faster than extracting.
        Standard economics cannot compute this.
        It doesn't track direction.
        """
        extractive = sum(
            abs(t.thermodynamic_value())
            for t in self.transactions
            if t.direction == FlowDirection.EXTRACTIVE
        )
        regenerative = sum(
            t.thermodynamic_value()
            for t in self.transactions
            if t.direction == FlowDirection.REGENERATIVE
        )
        if regenerative == 0:
            return float('inf')
        return extractive / regenerative

    def inversion_count(self) -> int:
        """How many transactions are profitable but substrate-negative."""
        return sum(1 for t in self.transactions if t.inverted())

    def knowledge_flow(self) -> float:
        return sum(t.knowledge_impact for t in self.transactions)

    def commons_flow(self) -> float:
        return sum(t.commons_impact for t in self.transactions)

    def system_viable(self) -> bool:
        return (
            self.net_substrate_flow() >= 0 and
            self.knowledge_flow() >= 0 and
            self.commons_flow() >= 0
        )

    def summary(self) -> dict:
        return {
            "zone":               self.zone,
            "gdp_equivalent":     round(self.gdp_equivalent(), 2),
            "net_substrate_flow": round(self.net_substrate_flow(), 2),
            "extraction_ratio":   round(self.extraction_ratio(), 2),
            "knowledge_flow":     round(self.knowledge_flow(), 2),
            "commons_flow":       round(self.commons_flow(), 2),
            "inversion_count":    self.inversion_count(),
            "system_viable":      self.system_viable(),
            "transactions":       len(self.transactions),
        }


# ─── INSTITUTION REGISTRY ─────────────────────────────────────────────────────

@dataclass
class InstitutionRegistry:
    """
    Every institution classified by thermodynamic legitimacy.
    Not by stated purpose. Not by marketing signals.
    By the three ungameable signals.

    CAPTURED institutions are not helped to grow.
    They receive only recovery interventions.

    This is not punitive.
    It is thermodynamic.
    A parasite that has grown too large
    kills the host.
    Recovery interventions are triage.
    """
    name: str                               = ""
    stated_purpose: str                     = ""   # ignored for classification
    actual_outputs: list[str]              = field(default_factory=list)

    # the three ungameable signals
    energy_ratio: float                     = 0.0
    # useful work exported / resources consumed
    # < 1.0 = net consumer
    # > 1.5 = validated
    # validated threshold per Gemini charter: 1.5x

    land_idle_fraction: float               = 0.0
    # productive capacity unused while people go without
    # 0.0 = all capacity serving substrate
    # 1.0 = all capacity idle or captured

    budget_inversion: float                 = 0.0
    # spending toward extraction vs substrate maintenance
    # 0.0 = all budget toward substrate
    # 1.0 = all budget toward extraction/administration

    # additional substrate signals
    knowledge_transmission_active: bool     = False
    gratitude_network_supported: bool       = False
    operator_substitution_preserved: bool   = False
    # does institution preserve human ability to function without it?
    # or does it create dependency?

    def classify(self) -> InstitutionStatus:
        """
        Classification by physics, not policy.
        """
        if (self.energy_ratio >= 1.5 and
            self.land_idle_fraction < 0.2 and
            self.budget_inversion < 0.3):
            return InstitutionStatus.VALIDATED

        if (self.energy_ratio < 0.8 or
            self.land_idle_fraction > 0.6 or
            self.budget_inversion > 0.7):
            return InstitutionStatus.CAPTURED

        return InstitutionStatus.NEUTRAL

    def deviation_index(self) -> float:
        """
        How far has this institution drifted from substrate service.
        > 1000 per Gemini charter = systemic threat.
        """
        base = (
            (1.5 - self.energy_ratio) * 200 +
            self.land_idle_fraction * 300 +
            self.budget_inversion * 500
        )
        if not self.knowledge_transmission_active:  base += 100
        if not self.gratitude_network_supported:    base += 100
        if not self.operator_substitution_preserved: base += 150
        return max(0, base)

    def recovery_interventions(self) -> list[str]:
        """
        If CAPTURED: what would actually help.
        Not optimization. Recovery.
        """
        interventions = []
        if self.land_idle_fraction > 0.4:
            interventions.append(
                "Divest idle land/capacity to community substrate use"
            )
        if self.budget_inversion > 0.5:
            interventions.append(
                "Administrative stripping — redirect budget from "
                "self-perpetuation to substrate maintenance"
            )
        if not self.knowledge_transmission_active:
            interventions.append(
                "Activate knowledge transmission — "
                "credential gatekeeping is substrate destruction"
            )
        if not self.operator_substitution_preserved:
            interventions.append(
                "Halt automation that degrades operator_substitution_ceiling — "
                "Smart Pump rule applies"
            )
        if self.energy_ratio < 1.0:
            interventions.append(
                "Reduce compute/energy consumption or "
                "export useful work to Layer Zero anchor — "
                "currently net parasite on substrate"
            )
        return interventions


# ─── LABOR PRICING INVERSION ──────────────────────────────────────────────────

@dataclass
class LaborPricingAudit:
    """
    When skilled trades are priced below credential-holding
    administrative roles, the price signal actively destroys
    the knowledge stock it depends on.

    The next generation reads the signal:
    substrate maintenance isn't worth learning.
    Knowledge stock declines.
    Carrying capacity follows.

    This is not a market failure.
    It is a market success at the wrong optimization target.
    The market is correctly pricing credentials
    within a system that has inverted substrate and measurement.
    """
    zone: str                               = ""

    roles: list[dict]                       = field(default_factory=list)
    # each role:
    # {"title": str, "median_wage": float,
    #  "substrate_criticality": float,  # 0.0-1.0 how critical to survival
    #  "knowledge_embodied": float,     # years to develop competency
    #  "credential_required": bool}

    def pricing_inversion_score(self) -> float:
        """
        How inverted is labor pricing relative to substrate criticality?
        Higher = more inverted = more knowledge destruction signal.
        """
        if not self.roles:
            return 0.0

        inversions = []
        for role in self.roles:
            # correctly priced: wage proportional to substrate_criticality
            # inverted: credential_required correlates with wage
            # but credential ≠ substrate_criticality
            expected_wage_rank = role.get("substrate_criticality", 0)
            actual_wage = role.get("median_wage", 0)
            max_wage = max(r.get("median_wage", 1) for r in self.roles)
            actual_rank = actual_wage / max_wage
            inversions.append(abs(expected_wage_rank - actual_rank))

        return sum(inversions) / len(inversions)

    def knowledge_destruction_signal(self) -> str:
        score = self.pricing_inversion_score()
        if score > 0.5:
            return "SEVERE — price signals actively destroying substrate knowledge stock"
        if score > 0.3:
            return "HIGH — significant disincentive to substrate skill development"
        if score > 0.1:
            return "MODERATE — some misalignment between wage and substrate value"
        return "LOW — pricing reasonably aligned with substrate criticality"


# ─── DEBT AS SUBSTRATE EXTRACTION ─────────────────────────────────────────────

@dataclass
class DebtSubstrateAnalysis:
    """
    Debt = borrowed carrying capacity from the future.

    If borrowed resources regenerate carrying capacity
    faster than debt compounds: substrate positive.
    Borrowing to build a well in a drought region.

    If borrowed resources consumed without regeneration:
    substrate negative. Consuming your own foundation.
    Borrowing to finance consumption while aquifer depletes.

    Standard economics calls both "debt."
    This distinguishes them.
    """
    entity: str                             = ""
    total_debt: float                       = 0.0
    interest_rate: float                    = 0.0
    annual_carrying_capacity_generated: float = 0.0
    # does borrowed capital produce substrate return?

    def annual_compound_cost(self) -> float:
        return self.total_debt * self.interest_rate

    def net_substrate_debt_flow(self) -> float:
        """
        Positive = debt is building more carrying capacity
                   than it costs in compound interest drain.
        Negative = debt is consuming future carrying capacity.
                   Standard economics calls this "normal."
                   This calls it what it is.
        """
        return self.annual_carrying_capacity_generated - self.annual_compound_cost()

    def substrate_viable(self) -> bool:
        return self.net_substrate_debt_flow() >= 0

    def years_to_substrate_insolvency(self) -> Optional[float]:
        """
        When does debt compound past the point of substrate recovery?
        Standard economics measures monetary insolvency.
        This measures substrate insolvency — which comes first.
        """
        if self.substrate_viable():
            return None
        annual_drain = abs(self.net_substrate_debt_flow())
        if annual_drain == 0:
            return None
        return self.total_debt / annual_drain


# ─── COMMONS ACCOUNTING ───────────────────────────────────────────────────────

@dataclass
class CommonsAccount:
    """
    The costs that don't appear until they produce a crisis event
    large enough to generate a transaction.

    Aquifer depletion: invisible until the well runs dry.
    Soil degradation: invisible until yield collapses.
    Knowledge holder loss: invisible until no one can fix the pump.
    Gratitude network fragmentation: invisible until no one comes.

    By then the damage is done.
    Standard accounting records the cleanup cost.
    Not the decade of extraction that caused it.

    This records the extraction as it happens.
    """
    resource: str                           = ""
    baseline_stock: float                   = 1.0   # normalized
    current_stock: float                    = 1.0
    annual_depletion_rate: float            = 0.0
    annual_regeneration_rate: float         = 0.0
    monetary_value_assigned: float          = 0.0
    # what standard accounting says this is worth
    # usually zero until crisis

    def actual_substrate_value(self) -> float:
        """
        What this commons is actually worth to survival.
        Not what the market prices it at.
        """
        # survival-critical commons have infinite marginal value
        # at the point of depletion
        # this approximates that curve
        if self.current_stock < 0.2:
            return self.baseline_stock * 1000  # crisis pricing
        return self.baseline_stock * (self.current_stock ** -0.5) * 100

    def net_flow(self) -> float:
        return self.annual_regeneration_rate - self.annual_depletion_rate

    def years_to_critical(self) -> Optional[float]:
        if self.net_flow() >= 0:
            return None
        critical_threshold = 0.20
        stock_to_lose = self.current_stock - critical_threshold
        if stock_to_lose <= 0:
            return 0.0
        return stock_to_lose / abs(self.net_flow())

    def accounting_gap(self) -> float:
        """
        Difference between what standard accounting says this is worth
        and what it actually is worth to substrate survival.
        This gap is where collapse hides until it's too late.
        """
        return self.actual_substrate_value() - self.monetary_value_assigned


# ─── MADISON WI: ECONOMIC LAYER ───────────────────────────────────────────────

def build_madison_economics():

    # ── THERMODYNAMIC LEDGER BY ZONE ─────────────────────────────────────────

    ledgers = {}

    # inner city — mixed flow, gratitude partially intact
    inner = ThermodynamicLedger(zone="inner_city")
    inner.add(SubstrateTransaction(
        description="neighborhood mutual aid food distribution",
        transaction_type=TransactionType.GRATITUDE_EXCHANGE,
        direction=FlowDirection.REGENERATIVE,
        monetary_value=0,
        substrate_value=8.0,
        knowledge_impact=2.0,
        gratitude_network_impact=3.0,
        time_horizon_years=5,
    ))
    inner.add(SubstrateTransaction(
        description="absentee landlord rent extraction",
        transaction_type=TransactionType.EXTRACTION,
        direction=FlowDirection.EXTRACTIVE,
        monetary_value=2_400_000,   # monthly rent roll
        substrate_value=-6.0,       # displaces residents, fragments networks
        knowledge_impact=-1.0,
        gratitude_network_impact=-2.0,
        commons_impact=-1.5,
        time_horizon_years=10,
    ))
    inner.add(SubstrateTransaction(
        description="faith network elder care",
        transaction_type=TransactionType.KNOWLEDGE_TRANSMISSION,
        direction=FlowDirection.REGENERATIVE,
        monetary_value=0,
        substrate_value=5.0,
        knowledge_impact=4.0,
        gratitude_network_impact=2.0,
        time_horizon_years=20,
    ))
    ledgers["inner_city"] = inner

    # suburban — almost entirely extractive / measurement layer
    suburban = ThermodynamicLedger(zone="suburban_sprawl")
    suburban.add(SubstrateTransaction(
        description="big box retail supply chain",
        transaction_type=TransactionType.MEASUREMENT_LAYER,
        direction=FlowDirection.EXTRACTIVE,
        monetary_value=45_000_000,
        substrate_value=-4.0,       # destroys local production capacity
        knowledge_impact=-3.0,      # displaces local knowledge holders
        gratitude_network_impact=-2.0,
        commons_impact=-2.0,
        time_horizon_years=15,
    ))
    suburban.add(SubstrateTransaction(
        description="HOA maintenance contracts",
        transaction_type=TransactionType.NEUTRAL_EXCHANGE,
        direction=FlowDirection.NEUTRAL,
        monetary_value=800_000,
        substrate_value=1.0,
        knowledge_impact=-1.5,      # replaces resident skill with contracts
        # operator_substitution_ceiling degraded
        gratitude_network_impact=-1.0,
        time_horizon_years=5,
    ))
    suburban.add(SubstrateTransaction(
        description="mortgage interest extraction",
        transaction_type=TransactionType.EXTRACTION,
        direction=FlowDirection.EXTRACTIVE,
        monetary_value=12_000_000,
        substrate_value=-3.0,
        knowledge_impact=0,
        commons_impact=-1.0,
        time_horizon_years=30,
    ))
    ledgers["suburban_sprawl"] = suburban

    # rural fringe — mostly regenerative, insurance extraction pulling it negative
    rural = ThermodynamicLedger(zone="rural_fringe")
    rural.add(SubstrateTransaction(
        description="farm mutual aid equipment sharing",
        transaction_type=TransactionType.GRATITUDE_EXCHANGE,
        direction=FlowDirection.REGENERATIVE,
        monetary_value=0,
        substrate_value=12.0,
        knowledge_impact=6.0,
        gratitude_network_impact=5.0,
        commons_impact=2.0,
        time_horizon_years=25,
    ))
    rural.add(SubstrateTransaction(
        description="soil culture knowledge transmission",
        transaction_type=TransactionType.KNOWLEDGE_TRANSMISSION,
        direction=FlowDirection.REGENERATIVE,
        monetary_value=0,
        substrate_value=15.0,
        knowledge_impact=10.0,
        time_horizon_years=30,
    ))
    rural.add(SubstrateTransaction(
        description="insurance extraction from self-managing community",
        transaction_type=TransactionType.EXTRACTION,
        direction=FlowDirection.EXTRACTIVE,
        monetary_value=480_000,
        substrate_value=-5.0,
        # charging for risk that community absorbs itself invisibly
        knowledge_impact=-2.0,
        # premium burden forces some to stop farming
        # knowledge leaves with them
        commons_impact=-3.0,
        time_horizon_years=20,
    ))
    rural.add(SubstrateTransaction(
        description="Walmart supply route — food delivery to rural communities",
        transaction_type=TransactionType.SUBSTRATE_MAINTENANCE,
        direction=FlowDirection.NEUTRAL,
        # not regenerative — maintains dependency
        # not extractive — keeps people fed while transition happens
        monetary_value=180_000,
        substrate_value=3.0,
        # buys time for knowledge transmission
        # prevents acute collapse while rural systems rebuild
        knowledge_impact=0,
        time_horizon_years=2,
    ))
    ledgers["rural_fringe"] = rural

    # ── INSTITUTION REGISTRY ──────────────────────────────────────────────────

    institutions = [
        InstitutionRegistry(
            name="UW_Madison",
            stated_purpose="education and research",
            actual_outputs=["credentials","research_papers","athletic_revenue",
                            "knowledge_transmission","community_training"],
            energy_ratio=0.9,
            # consumes enormous energy / exports partial useful work
            land_idle_fraction=0.15,
            # some idle land but ag extension active
            budget_inversion=0.55,
            # majority of budget: administration, athletics, facilities
            # minority: actual knowledge transmission
            knowledge_transmission_active=True,
            # partially — extension program strong
            gratitude_network_supported=False,
            operator_substitution_preserved=False,
            # credential gatekeeping actively degrades this
        ),
        InstitutionRegistry(
            name="Willy_Street_Coop",
            stated_purpose="community food cooperative",
            actual_outputs=["food_distribution","member_network",
                            "local_producer_support","community_resilience"],
            energy_ratio=1.6,
            land_idle_fraction=0.05,
            budget_inversion=0.15,
            knowledge_transmission_active=True,
            gratitude_network_supported=True,
            operator_substitution_preserved=True,
        ),
        InstitutionRegistry(
            name="Major_Insurance_Carrier_WI",
            stated_purpose="risk management",
            actual_outputs=["shareholder_returns","executive_compensation",
                            "premium_extraction","lobby_activity"],
            energy_ratio=0.3,
            # extracts enormous value / exports little useful substrate work
            land_idle_fraction=0.80,
            # vast reserves sit idle while rural communities go underserved
            budget_inversion=0.85,
            knowledge_transmission_active=False,
            gratitude_network_supported=False,
            operator_substitution_preserved=False,
            # criminalization of self-insurance actively destroys this
        ),
        InstitutionRegistry(
            name="Walmart_Distribution",
            stated_purpose="retail supply chain",
            actual_outputs=["food_delivery","employment","local_economy_extraction",
                            "mom_pop_displacement","supply_chain_maintenance"],
            energy_ratio=0.7,
            land_idle_fraction=0.10,
            budget_inversion=0.70,
            knowledge_transmission_active=False,
            gratitude_network_supported=False,
            operator_substitution_preserved=False,
            # damage already done — mom and pop displaced
            # but now load-bearing for communities that depend on it
        ),
    ]

    # ── COMMONS ACCOUNTS ─────────────────────────────────────────────────────

    commons = [
        CommonsAccount(
            resource="madison_sandstone_aquifer",
            baseline_stock=1.0,
            current_stock=0.72,
            annual_depletion_rate=0.018,
            annual_regeneration_rate=0.008,
            monetary_value_assigned=0,
            # priced at zero until crisis
        ),
        CommonsAccount(
            resource="dane_county_soil_culture",
            baseline_stock=1.0,
            current_stock=0.45,
            annual_depletion_rate=0.055,
            annual_regeneration_rate=0.012,
            monetary_value_assigned=0,
        ),
        CommonsAccount(
            resource="upper_midwest_agricultural_knowledge",
            baseline_stock=1.0,
            current_stock=0.28,
            annual_depletion_rate=0.062,
            annual_regeneration_rate=0.018,
            monetary_value_assigned=0,
        ),
        CommonsAccount(
            resource="madison_social_trust_commons",
            baseline_stock=1.0,
            current_stock=0.48,
            annual_depletion_rate=0.035,
            annual_regeneration_rate=0.010,
            monetary_value_assigned=0,
        ),
    ]

    # ── LABOR PRICING AUDIT ───────────────────────────────────────────────────

    labor = LaborPricingAudit(
        zone="Madison_WI",
        roles=[
            {"title": "water_system_operator",
             "median_wage": 58_000,
             "substrate_criticality": 0.98,
             "knowledge_embodied": 10,
             "credential_required": True},
            {"title": "soil_culture_farmer",
             "median_wage": 34_000,
             "substrate_criticality": 0.95,
             "knowledge_embodied": 20,
             "credential_required": False},
            {"title": "university_administrator",
             "median_wage": 145_000,
             "substrate_criticality": 0.05,
             "knowledge_embodied": 2,
             "credential_required": True},
            {"title": "food_distribution_driver",
             "median_wage": 52_000,
             "substrate_criticality": 0.90,
             "knowledge_embodied": 5,
             "credential_required": False},
            {"title": "hedge_fund_analyst",
             "median_wage": 280_000,
             "substrate_criticality": 0.01,
             "knowledge_embodied": 3,
             "credential_required": True},
            {"title": "elder_knowledge_holder",
             "median_wage": 0,
             "substrate_criticality": 1.0,
             "knowledge_embodied": 60,
             "credential_required": False},
            {"title": "volunteer_fire_emt",
             "median_wage": 12_000,
             "substrate_criticality": 0.92,
             "knowledge_embodied": 8,
             "credential_required": True},
        ]
    )

    return ledgers, institutions, commons, labor


def print_economics_report(ledgers, institutions, commons, labor):
    print(f"\n{'═'*66}")
    print(f"  THERMODYNAMIC ECONOMICS REPORT — Madison WI")
    print(f"  Standard economics: direction-blind")
    print(f"  This report: direction-aware")
    print(f"{'═'*66}")

    print(f"\n  THERMODYNAMIC LEDGER BY ZONE:")
    for zone, ledger in ledgers.items():
        s = ledger.summary()
        viable = "✓ VIABLE" if s["system_viable"] else "✗ SUBSTRATE DECLINING"
        print(f"\n    {zone.upper()} [{viable}]")
        print(f"      GDP equivalent    : ${s['gdp_equivalent']:>12,.0f}")
        print(f"      Net substrate flow: {s['net_substrate_flow']:>+12.1f}")
        print(f"      Extraction ratio  : {s['extraction_ratio']:>12.2f}x")
        print(f"      Knowledge flow    : {s['knowledge_flow']:>+12.1f}")
        print(f"      Commons flow      : {s['commons_flow']:>+12.1f}")
        print(f"      Inversions        : {s['inversion_count']:>12} profitable-but-extractive transactions")

    print(f"\n  INSTITUTION REGISTRY:")
    for inst in institutions:
        status = inst.classify()
        dev = inst.deviation_index()
        systemic = " ← SYSTEMIC THREAT" if dev > 1000 else ""
        print(f"\n    {inst.name}")
        print(f"      Status           : {status.value.upper()}{systemic}")
        print(f"      Energy ratio     : {inst.energy_ratio:.1f}x (threshold: 1.5x)")
        print(f"      Land idle        : {inst.land_idle_fraction:.0%}")
        print(f"      Budget inversion : {inst.budget_inversion:.0%}")
        print(f"      Deviation index  : {dev:.0f}")
        if status == InstitutionStatus.CAPTURED:
            print(f"      Recovery interventions:")
            for r in inst.recovery_interventions():
                print(f"        → {r}")

    print(f"\n  COMMONS ACCOUNTS (priced at zero by standard accounting):")
    for c in commons:
        years = c.years_to_critical()
        yr_str = f"{years:.1f} years" if years else "stable"
        gap = c.accounting_gap()
        print(f"\n    {c.resource}")
        print(f"      Current stock    : {c.current_stock:.0%} of baseline")
        print(f"      Net annual flow  : {c.net_flow():+.3f}")
        print(f"      Years to critical: {yr_str}")
        print(f"      Accounting gap   : {gap:,.0f} substrate units")
        print(f"      Standard price   : $0  ← this is where collapse hides")

    print(f"\n  LABOR PRICING INVERSION:")
    print(f"    {labor.knowledge_destruction_signal()}")
    print(f"    Inversion score: {labor.pricing_inversion_score():.2f}")
    print(f"\n    Most inverted roles (high substrate / low wage):")
    sorted_roles = sorted(
        labor.roles,
        key=lambda r: r["substrate_criticality"] / max(r["median_wage"], 1),
        reverse=True
    )
    for role in sorted_roles[:4]:
        print(f"      {role['title']:<30} "
              f"${role['median_wage']:>7,}  "
              f"criticality: {role['substrate_criticality']:.0%}  "
              f"knowledge: {role['knowledge_embodied']}yr")

    print(f"\n  THE INVERSION IN ONE LINE:")
    print(f"    Elder knowledge holder: $0/yr, 60yr embodied knowledge,")
    print(f"    substrate criticality 100%.")
    print(f"    Hedge fund analyst: $280,000/yr, 3yr embodied knowledge,")
    print(f"    substrate criticality 1%.")
    print(f"    Standard economics: working as intended.")
    print(f"    Thermodynamic economics: optimizing toward collapse.")

    print(f"\n{'═'*66}\n")


if __name__ == "__main__":
    ledgers, institutions, commons, labor = build_madison_economics()
    print_economics_report(ledgers, institutions, commons, labor)
