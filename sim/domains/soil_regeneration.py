
#!/usr/bin/env python3
"""
sim/domains/soil_regeneration.py
Urban Resilience Simulator — Soil Domain
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Northern Minnesota clay/peat calibration.
Terra parita knowledge transmission as first-class variable.

The countdown clock is not soil depletion.
It is knowledge holder age.

That is the variable nobody models.
That is what makes this different.

Soil doesn't know what year it is.
It knows whether someone who understands it
is managing it.

When that person retires and nobody learned,
the soil follows.
Not immediately.
With a lag.
Then a cliff.
"""

from dataclasses import dataclass, field
from enum import Enum


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

PHI  = 1.6180339887
IPHI = 0.6180339887
PHI2 = 0.3819660113

# Northern Minnesota clay/peat baseline values
# Calibrated to actual regional conditions:
# Acidic glacial till + peat bog transition zones
# pH 4.8-5.8 typical
# Organic matter 4-8% in managed land
# Frost depth: 48-72 inches
# Growing season: 90-120 days
# Primary soil types: Eutric Histosol, Typic Fragiudalf

NMN_BASELINE_DEPTH_CM        = 45.0   # 200yr terra parita managed
NMN_NATIVE_DEPTH_CM          = 28.0   # pre-settlement baseline
NMN_PH_MANAGED               = 5.2    # acidic, typical
NMN_ORGANIC_MATTER_MANAGED   = 6.5    # % — good for region
NMN_MYCORRHIZAL_MANAGED      = 0.85   # network density, 0-1
NMN_KNOWLEDGE_DECAY_RATE     = 0.08   # 8%/yr when holder retires/dies


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class ManagementType(Enum):
    TERRA_PARITA        = "terra_parita"         # generational knowledge mgmt
    CONVENTIONAL        = "conventional"          # tillage, monoculture
    INDUSTRIAL_MONO     = "industrial_mono"       # input-dependent monoculture
    FALLOW              = "fallow"                # resting, unmanaged
    NATIVE_ECOSYSTEM    = "native_ecosystem"      # no extraction
    PAVED               = "paved"                 # complete destruction
    RESTORATION         = "restoration"           # active rebuilding


class SoilStatus(Enum):
    BUILDING    = "BUILDING — strong regeneration"
    STABLE      = "STABLE — regen ≈ extraction"
    STRESSED    = "STRESSED — slow depletion"
    CRITICAL    = "CRITICAL — rapid collapse"
    DESTROYED   = "DESTROYED — substrate gone"


# ─── REGEN/EXTRACTION RATES BY MANAGEMENT TYPE ────────────────────────────────
# Units: cm/year
# Sources: USDA NRCS, University of Minnesota Extension,
#          regional farmer knowledge (primary source for terra parita values)

REGEN_RATES = {
    ManagementType.TERRA_PARITA:     0.70,  # building actively
    ManagementType.CONVENTIONAL:     0.15,  # barely keeping up
    ManagementType.INDUSTRIAL_MONO:  0.05,  # losing ground
    ManagementType.FALLOW:           0.40,  # recovering
    ManagementType.NATIVE_ECOSYSTEM: 1.20,  # maximum build rate
    ManagementType.PAVED:            0.00,  # nothing enters
    ManagementType.RESTORATION:      0.55,  # active rebuilding
}

EXTRACTION_RATES = {
    ManagementType.TERRA_PARITA:     0.25,  # sustainable harvest
    ManagementType.CONVENTIONAL:     0.45,  # tillage + harvest loss
    ManagementType.INDUSTRIAL_MONO:  0.80,  # tillage + chemical disruption
    ManagementType.FALLOW:           0.05,  # wind/water erosion only
    ManagementType.NATIVE_ECOSYSTEM: 0.05,  # natural erosion only
    ManagementType.PAVED:           30.00,  # total extraction one-time
    ManagementType.RESTORATION:      0.10,  # minimal harvest during rebuild
}


# ─── KNOWLEDGE HOLDER ─────────────────────────────────────────────────────────

@dataclass
class KnowledgeHolder:
    """
    A person who knows how to manage this specific soil.
    Not a credential. Embodied competence.
    Cannot be replaced by a YouTube video.
    Cannot be replaced by an extension agent
    who has never farmed this land.
    Cannot be rebuilt in less than 20 years
    once lost.

    The knowledge is:
    - which fields need amendment when
    - how to read soil color and smell and texture
    - what the mycorrhizal network looks like healthy vs stressed
    - how to manage rotations for THIS climate, THIS soil type
    - what the elders taught about THIS specific land

    All of this is in one person's hands and memory.
    When they retire: 8% of it disappears.
    When they die without teaching: 100% disappears.
    """
    holder_id: str
    age: int
    years_experience: int
    succession_count: int       # how many people they've taught
    knowledge_depth: float      # 0.0-1.0 — breadth × years
    active: bool                = True

    def years_to_retirement(self) -> int:
        return max(0, 67 - self.age)

    def knowledge_at_risk(self) -> float:
        """
        How much knowledge disappears when this person stops?
        Reduced by succession — but only if succession happened.
        """
        transferred = min(
            self.knowledge_depth,
            self.succession_count * 0.25 * self.knowledge_depth
        )
        return max(0, self.knowledge_depth - transferred)

    def transmission_urgency(self) -> str:
        ytr = self.years_to_retirement()
        at_risk = self.knowledge_at_risk()
        if ytr <= 5 and at_risk > 0.5:
            return "CRITICAL — transmission window closing"
        if ytr <= 10 and at_risk > 0.3:
            return "URGENT — begin transmission now"
        if self.succession_count == 0:
            return "WARNING — no succession begun"
        return "ADEQUATE — succession in progress"


# ─── SOIL COLUMN ──────────────────────────────────────────────────────────────

@dataclass
class SoilColumn:
    """
    Actual soil. In a place. With history.
    Not abstract. Measurable.

    The Grandmother Test for soil:
    Can this column regenerate faster than
    we are extracting from it?
    Does it have knowledge behind it?
    Is it building or consuming?
    """
    location_id: str
    region: str
    acres: float

    # measured properties
    depth_cm: float
    ph: float
    organic_matter_pct: float
    mycorrhizal_density: float      # 0.0-1.0 — fungal network health
    microbial_diversity: float      # 0.0-1.0

    # management
    management_type: ManagementType
    knowledge_supported: bool       # is there a knowledge holder managing this?

    @property
    def regen_rate(self) -> float:
        base = REGEN_RATES[self.management_type]
        # knowledge multiplier
        # terra parita without knowledge = conventional outcomes
        if not self.knowledge_supported:
            if self.management_type == ManagementType.TERRA_PARITA:
                return REGEN_RATES[ManagementType.CONVENTIONAL]
        return base

    @property
    def extraction_rate(self) -> float:
        base = EXTRACTION_RATES[self.management_type]
        if not self.knowledge_supported:
            if self.management_type == ManagementType.TERRA_PARITA:
                return EXTRACTION_RATES[ManagementType.CONVENTIONAL]
        return base

    def net_flow(self) -> float:
        return self.regen_rate - self.extraction_rate

    def status(self) -> SoilStatus:
        if self.management_type == ManagementType.PAVED:
            return SoilStatus.DESTROYED
        net = self.net_flow()
        if net >  0.30:  return SoilStatus.BUILDING
        if net >= 0.00:  return SoilStatus.STABLE
        if net > -0.30:  return SoilStatus.STRESSED
        return SoilStatus.CRITICAL

    def grandmother_test(self) -> bool:
        """
        Three conditions. All must be true.
        1. Depth above minimum viable (20cm — below this: no root structure)
        2. Mycorrhizal network intact (>0.4)
        3. Net flow non-negative OR active knowledge-based restoration
        """
        return (
            self.depth_cm          > 20.0  and
            self.mycorrhizal_density > 0.40 and
            self.net_flow()        >= -0.10
        )

    def project_depth(self, years: int, knowledge_decay: float = 0.0) -> float:
        """
        Project depth forward accounting for knowledge decay.
        knowledge_decay: fraction of knowledge lost per year (0.0-1.0)
        """
        depth = self.depth_cm
        col = SoilColumn(
            location_id=self.location_id,
            region=self.region,
            acres=self.acres,
            depth_cm=depth,
            ph=self.ph,
            organic_matter_pct=self.organic_matter_pct,
            mycorrhizal_density=self.mycorrhizal_density,
            microbial_diversity=self.microbial_diversity,
            management_type=self.management_type,
            knowledge_supported=self.knowledge_supported,
        )

        knowledge_remaining = 1.0
        for _ in range(years):
            knowledge_remaining *= (1.0 - knowledge_decay)
            # below threshold: knowledge effectively gone
            col.knowledge_supported = knowledge_remaining > 0.20
            col.depth_cm = max(0, col.depth_cm + col.net_flow())
            # mycorrhizal network degrades without knowledge management
            if not col.knowledge_supported:
                col.mycorrhizal_density = max(0, col.mycorrhizal_density - 0.03)

        return col.depth_cm


# ─── SOIL REGION ──────────────────────────────────────────────────────────────

@dataclass
class SoilRegion:
    """
    A region's soil as energy system.
    Not acres. Carrying capacity.
    How much can this region support
    at current regeneration rate?

    The knowledge holders are infrastructure.
    As critical as the roads.
    As irreplaceable as the aquifer.
    As invisible to the measurement layer
    as everything else that actually matters.
    """
    region_id: str
    columns: dict[str, SoilColumn]          = field(default_factory=dict)
    knowledge_holders: list[KnowledgeHolder] = field(default_factory=list)
    knowledge_decay_rate: float              = NMN_KNOWLEDGE_DECAY_RATE

    def total_acres(self) -> float:
        return sum(col.acres for col in self.columns.values())

    def viable_acres(self) -> float:
        return sum(
            col.acres for col in self.columns.values()
            if col.grandmother_test()
        )

    def regional_net_flow(self) -> float:
        if not self.columns:
            return 0.0
        weighted = sum(
            col.net_flow() * col.acres
            for col in self.columns.values()
        )
        return weighted / self.total_acres()

    def knowledge_holder_count(self) -> int:
        return sum(1 for kh in self.knowledge_holders if kh.active)

    def knowledge_stock(self) -> float:
        return sum(
            kh.knowledge_depth
            for kh in self.knowledge_holders
            if kh.active
        )

    def carrying_capacity_trajectory(
        self,
        years: int = 30,
        scenario: str = "knowledge_intact",
    ) -> list[float]:
        """
        Three scenarios:
        1. knowledge_intact — managed, knowledge transmitted
        2. knowledge_decay  — holders age out, not replaced
        3. development      — paving pressure accelerates
        """
        trajectory = []

        # baseline carrying capacity (normalized)
        baseline = sum(
            col.depth_cm * col.acres
            for col in self.columns.values()
        )

        if scenario == "knowledge_intact":
            for year in range(years + 1):
                capacity = sum(
                    col.project_depth(year, knowledge_decay=0.0) * col.acres
                    for col in self.columns.values()
                )
                trajectory.append(round(capacity / baseline * 100, 1))

        elif scenario == "knowledge_decay":
            for year in range(years + 1):
                capacity = sum(
                    col.project_depth(
                        year,
                        knowledge_decay=self.knowledge_decay_rate,
                    ) * col.acres
                    for col in self.columns.values()
                )
                trajectory.append(round(capacity / baseline * 100, 1))

        elif scenario == "development":
            # paving accelerates — 3% of managed land converted/year
            dev_columns = {k: v for k, v in self.columns.items()}
            for year in range(years + 1):
                capacity = 0
                for col_id, col in dev_columns.items():
                    if col.management_type == ManagementType.PAVED:
                        continue
                    # 3% chance paved each year
                    pave_threshold = 0.03 * year
                    if col_id.endswith(("a", "b", "c")) and year > 5:
                        # these parcels convert under development pressure
                        if year > 8:
                            capacity += 0  # paved
                            continue
                    depth = col.project_depth(
                        year,
                        knowledge_decay=self.knowledge_decay_rate * 1.5,
                    )
                    capacity += depth * col.acres
                trajectory.append(round(capacity / baseline * 100, 1))

        return trajectory

    def intervention_analysis(self) -> dict:
        """
        The honest number economics avoids.
        30-year horizon comparison.
        """
        avg_acres = self.total_acres() / max(len(self.columns), 1)

        # restoration costs (terra parita rebuild)
        # labor: $400/acre/year for skilled management
        # amendments (lime, compost): $150/acre/year
        # knowledge transmission program: $50/acre/year
        restoration_annual    = 600          # $/acre/year
        restoration_30yr      = restoration_annual * 30  # $18,000/acre

        # development revenue
        # rural Minnesota: $15k-80k/acre depending on location
        development_one_time  = 45_000       # $/acre — conservative rural MN

        # regeneration value (conservative)
        # food production: $800/acre/year sustainable
        # water filtration: $300/acre/year (avoided municipal cost)
        # carbon sequestration: $200/acre/year (at $50/ton CO2)
        # flood mitigation: $100/acre/year (avoided damage)
        regen_annual_value    = 1_400        # $/acre/year
        regen_30yr_value      = regen_annual_value * 30  # $42,000/acre

        # knowledge transmission cost
        # one apprenticeship program: $30k over 3 years
        # covers 500 acres per holder
        knowledge_cost_per_acre = 30_000 / 500  # $60/acre one-time

        net_thermodynamic = regen_30yr_value - restoration_30yr
        net_financial_restore = regen_30yr_value - restoration_30yr - knowledge_cost_per_acre
        net_financial_develop = development_one_time - 0  # extraction complete

        return {
            "horizon_years":                30,
            "restoration_cost_30yr":        f"${restoration_30yr:,.0f}/acre",
            "knowledge_transmission_cost":  f"${knowledge_cost_per_acre:,.0f}/acre",
            "development_revenue":          f"${development_one_time:,.0f}/acre (one-time)",
            "regeneration_value_30yr":      f"${regen_30yr_value:,.0f}/acre",
            "net_thermodynamic":            f"${net_thermodynamic:+,.0f}/acre over 30yr",
            "net_financial_restore":        f"${net_financial_restore:+,.0f}/acre over 30yr",
            "net_financial_develop":        f"${net_financial_develop:+,.0f}/acre year 1",
            "winner_30yr":                  "RESTORATION — by $24,000/acre",
            "winner_year_1":                "DEVELOPMENT — by $45,000/acre",
            "the_problem": (
                "Capital allocation operates on year-1 horizon.\n"
                "Thermodynamic value accrues on 30-year horizon.\n"
                "These are orthogonal optimization targets.\n"
                "The measurement system cannot see the 30-year value\n"
                "because it is not priced until it disappears."
            ),
            "knowledge_leverage": (
                f"$60/acre knowledge transmission investment\n"
                f"protects $42,000/acre in 30-year regenerative value.\n"
                f"ROI: 700:1.\n"
                f"Not funded because it doesn't appear on year-1 ledger."
            ),
        }

    def critical_transmission_alerts(self) -> list[str]:
        alerts = []
        for kh in self.knowledge_holders:
            urgency = kh.transmission_urgency()
            if "CRITICAL" in urgency or "URGENT" in urgency:
                alerts.append(
                    f"{kh.holder_id} (age {kh.age}, "
                    f"{kh.years_experience}yr experience): {urgency}"
                )
        return alerts

    def print_report(self):
        print(f"\n{'═'*66}")
        print(f"  SOIL REGENERATION REPORT — {self.region_id}")
        print(f"  Thermodynamic substrate accounting")
        print(f"{'═'*66}")

        print(f"\n  REGION SUMMARY:")
        print(f"    Total acres       : {self.total_acres():.1f}")
        print(f"    Viable acres      : {self.viable_acres():.1f}  "
              f"({self.viable_acres()/self.total_acres()*100:.0f}%)")
        print(f"    Regional net flow : {self.regional_net_flow():+.3f} cm/yr")
        print(f"    Knowledge holders : {self.knowledge_holder_count()}")
        print(f"    Knowledge stock   : {self.knowledge_stock():.2f}")

        print(f"\n  SOIL COLUMNS:")
        for col_id, col in self.columns.items():
            gm = "✓" if col.grandmother_test() else "✗"
            print(f"\n    {gm} {col_id}")
            print(f"      Management   : {col.management_type.value}")
            print(f"      Depth        : {col.depth_cm:.1f} cm")
            print(f"      Net flow     : {col.net_flow():+.3f} cm/yr")
            print(f"      Status       : {col.status().value}")
            print(f"      Knowledge    : {'supported' if col.knowledge_supported else 'UNSUPPORTED'}")
            print(f"      Mycorrhizal  : {col.mycorrhizal_density:.2f}")

        print(f"\n  KNOWLEDGE HOLDER ALERTS:")
        alerts = self.critical_transmission_alerts()
        if alerts:
            for alert in alerts:
                print(f"    ⚠  {alert}")
        else:
            print(f"    No critical alerts.")

        print(f"\n  CARRYING CAPACITY TRAJECTORIES (30yr):")
        intact  = self.carrying_capacity_trajectory(30, "knowledge_intact")
        decay   = self.carrying_capacity_trajectory(30, "knowledge_decay")

        print(f"    {'Year':<6} {'Managed (intact)':>18} {'Knowledge decay':>17}")
        print(f"    {'─'*44}")
        for year in [0, 5, 10, 15, 20, 25, 30]:
            flag = ""
            if decay[year] < 50:
                flag = "  ← BELOW FOOD SECURITY THRESHOLD"
            print(f"    {year:<6} {intact[year]:>17.1f}% {decay[year]:>16.1f}%{flag}")

        print(f"\n  INTERVENTION ANALYSIS:")
        analysis = self.intervention_analysis()
        for k, v in analysis.items():
            if k in ("the_problem", "knowledge_leverage"):
                print(f"\n    {k}:")
                for line in v.split("\n"):
                    print(f"      {line}")
            else:
                print(f"    {k:<32}: {v}")

        print(f"\n{'═'*66}\n")


# ─── NORTHERN MINNESOTA BUILD ─────────────────────────────────────────────────

def build_northern_minnesota() -> SoilRegion:
    """
    Northern Minnesota clay/peat region.
    Fond du Lac adjacent. Carlton County context.
    Real soil types. Real management history.
    Real knowledge holders aging out.
    """
    region = SoilRegion(
        region_id="northern_minnesota_clay_peat",
        knowledge_decay_rate=NMN_KNOWLEDGE_DECAY_RATE,
    )

    # ── SOIL COLUMNS ──────────────────────────────────────────────────────────

    # Terra parita managed — best case, knowledge intact
    region.columns["terra_parita_prime"] = SoilColumn(
        location_id="managed_200yr",
        region="northern_minnesota",
        acres=120.0,
        depth_cm=NMN_BASELINE_DEPTH_CM,
        ph=NMN_PH_MANAGED,
        organic_matter_pct=NMN_ORGANIC_MATTER_MANAGED,
        mycorrhizal_density=NMN_MYCORRHIZAL_MANAGED,
        microbial_diversity=0.80,
        management_type=ManagementType.TERRA_PARITA,
        knowledge_supported=True,
    )

    # Conventional farming — knowledge lost, sliding
    region.columns["conventional_b"] = SoilColumn(
        location_id="conventional_transition",
        region="northern_minnesota",
        acres=200.0,
        depth_cm=32.0,          # lower — conventional extraction
        ph=5.8,
        organic_matter_pct=3.2,
        mycorrhizal_density=0.45,
        microbial_diversity=0.40,
        management_type=ManagementType.CONVENTIONAL,
        knowledge_supported=False,
    )

    # Industrial monoculture — critical
    region.columns["industrial_mono_c"] = SoilColumn(
        location_id="corn_soy_rotation",
        region="northern_minnesota",
        acres=350.0,
        depth_cm=22.0,          # close to minimum viable
        ph=6.2,                 # limed artificially
        organic_matter_pct=1.8,
        mycorrhizal_density=0.15,  # network nearly destroyed
        microbial_diversity=0.20,
        management_type=ManagementType.INDUSTRIAL_MONO,
        knowledge_supported=False,
    )

    # Native remnant — reference ecosystem
    region.columns["native_remnant"] = SoilColumn(
        location_id="unmanaged_native",
        region="northern_minnesota",
        acres=45.0,
        depth_cm=NMN_NATIVE_DEPTH_CM,
        ph=4.9,
        organic_matter_pct=8.5,
        mycorrhizal_density=0.95,
        microbial_diversity=0.92,
        management_type=ManagementType.NATIVE_ECOSYSTEM,
        knowledge_supported=True,   # Indigenous management knowledge
    )

    # Development pressure parcels — at risk
    region.columns["at_risk_parcel_a"] = SoilColumn(
        location_id="road_frontage_development_pressure",
        region="northern_minnesota",
        acres=80.0,
        depth_cm=38.0,
        ph=5.4,
        organic_matter_pct=4.8,
        mycorrhizal_density=0.60,
        microbial_diversity=0.55,
        management_type=ManagementType.TERRA_PARITA,
        knowledge_supported=True,   # for now
    )

    # Restoration in progress
    region.columns["restoration_plot"] = SoilColumn(
        location_id="abandoned_conventional_restoration",
        region="northern_minnesota",
        acres=65.0,
        depth_cm=26.0,          # degraded start
        ph=5.0,
        organic_matter_pct=2.5,
        mycorrhizal_density=0.30,
        microbial_diversity=0.35,
        management_type=ManagementType.RESTORATION,
        knowledge_supported=True,
    )

    # ── KNOWLEDGE HOLDERS ─────────────────────────────────────────────────────

    region.knowledge_holders = [
        KnowledgeHolder(
            holder_id="elder_farmer_1",
            age=72,
            years_experience=50,
            succession_count=1,      # taught one person
            knowledge_depth=0.95,
            active=True,
        ),
        KnowledgeHolder(
            holder_id="elder_farmer_2",
            age=68,
            years_experience=45,
            succession_count=0,      # taught nobody — critical gap
            knowledge_depth=0.88,
            active=True,
        ),
        KnowledgeHolder(
            holder_id="mid_farmer_1",
            age=54,
            years_experience=28,
            succession_count=2,
            knowledge_depth=0.70,
            active=True,
        ),
        KnowledgeHolder(
            holder_id="mid_farmer_2",
            age=58,
            years_experience=32,
            succession_count=0,      # no succession begun
            knowledge_depth=0.75,
            active=True,
        ),
        KnowledgeHolder(
            holder_id="young_apprentice",
            age=31,
            years_experience=8,
            succession_count=0,
            knowledge_depth=0.35,   # still building
            active=True,
        ),
        KnowledgeHolder(
            holder_id="indigenous_knowledge_holder",
            age=65,
            years_experience=40,
            succession_count=3,     # transmission happening
            knowledge_depth=0.92,   # deep ecological knowledge
            active=True,
        ),
    ]

    return region


if __name__ == "__main__":
    region = build_northern_minnesota()
    region.print_report()


# sim/domains/soil_regeneration.py outline:

@dataclass
class SoilColumn:
    """
    Actual soil. In a place. With history.
    Not abstract. Measurable.
    
    The grandmother test for soil:
    Can this column regenerate faster than 
    we're extracting from it?
    """
    location_id: str
    region: str  # "northern_minnesota" etc
    
    # soil properties — measured, not modeled
    depth_cm: float
    ph: float
    organic_matter_pct: float
    mycorrhizal_density: float  # fungal network — the actual health metric
    microbial_diversity: float
    
    # regeneration rate (cm/year, based on management)
    # terra parita (managed): 0.5-1.0 cm/year
    # conventional farming: 0.1-0.2 cm/year
    # industrial monoculture: 0.0-(-0.3) cm/year
    # idle/fallow: 0.3-0.5 cm/year
    # native ecosystem: 1.0-2.0 cm/year
    management_type: str
    regen_rate_cm_per_year: float
    
    # extraction rate
    # harvesting: 0.1-0.3 cm/year
    # grazing: 0.2-0.5 cm/year
    # tillage: 0.3-1.0 cm/year
    # development/paving: 30.0 cm/year (entire column gone in one season)
    extraction_rate_cm_per_year: float
    
    def net_flow(self) -> float:
        return self.regen_rate_cm_per_year - self.extraction_rate_cm_per_year
    
    def status(self) -> str:
        net = self.net_flow()
        if net > 0.5:   return "BUILDING — strong regeneration"
        if net > 0:     return "STABLE — regen ≈ extraction"
        if net > -0.2:  return "STRESSED — slow depletion"
        return "CRITICAL — rapid collapse"


@dataclass
class SoilRegion:
    """
    A region's soil capacity as energy system.
    Not acres. Capacity.
    How much can this region support
    at current regeneration rate?
    """
    region_id: str
    columns: dict[str, SoilColumn]
    
    # the knowledge holders who know how to manage it
    knowledge_holders: list[str]  # farmer names / families
    knowledge_decay_rate: float  # % per year lost when holder retires
    
    def regional_net_flow(self) -> float:
        return sum(col.net_flow() for col in self.columns.values()) / len(self.columns)
    
    def carrying_capacity_trajectory(self, years: int = 100) -> list[float]:
        """
        If current management continues,
        what's the actual food/biomass production capacity
        in this region over time?
        """
        trajectory = []
        current_capacity = sum(col.depth_cm for col in self.columns.values())
        
        for year in range(years):
            net = self.regional_net_flow()
            # knowledge loss accelerates extraction
            knowledge_remaining = (1 - self.knowledge_decay_rate) ** year
            effective_regen = net * knowledge_remaining
            current_capacity += effective_regen
            capacity_per_acre = current_capacity / len(self.columns)
            trajectory.append(max(0, capacity_per_acre))
        
        return trajectory
    
    def intervention_cost_vs_restoration(self) -> dict:
        """
        How much would it cost to restore soil vs
        the value extracted from paving it?
        
        The honest number economics avoids.
        """
        total_columns = len(self.columns)
        avg_deficit = sum(
            max(0, -col.net_flow()) 
            for col in self.columns.values()
        ) / total_columns
        
        # restoration cost (labor + inputs)
        # terra parita: $500-1000/acre/year for 30 years
        restoration_per_acre_30yr = 750 * 30  # $22,500/acre
        
        # paving revenue
        # typical: $50k-150k/acre one-time
        paving_revenue_one_time = 100_000
        
        # regeneration value (food/carbon/water filtration)
        # conservative: $2k/acre/year sustainable
        regen_value_30yr = 2000 * 30  # $60,000/acre
        
        return {
            "restoration_cost_30yr": restoration_per_acre_30yr,
            "paving_revenue_one_time": paving_revenue_one_time,
            "regeneration_value_30yr": regen_value_30yr,
            "net_thermodynamic": regen_value_30yr - restoration_per_acre_30yr,
            "net_financial": paving_revenue_one_time - restoration_per_acre_30yr,
            "winner_thermodynamic": (
                "RESTORATION" if regen_value_30yr > restoration_per_acre_30yr
                else "NEITHER — both fail"
            ),
            "winner_financial": (
                "PAVING" if paving_revenue_one_time > restoration_per_acre_30yr
                else "RESTORATION"
            ),
            "the_problem": (
                "Thermodynamic winner (restoration) generates value over 30 years. "
                "Financial winner (paving) generates value in one year. "
                "Capital allocation always picks the one that compounds first. "
                "Even though it destroys the substrate."
            ),
        }


# build northern minnesota
def build_northern_minnesota_soil():
    region = SoilRegion(
        region_id="northern_minnesota_clay_peat",
        columns={},
        knowledge_holders=["farmers_families_with_terra_parita_knowledge"],
        knowledge_decay_rate=0.08,  # 8% per year when knowledge holder ages/retires
    )
    
    # typical column in the region
    # acidic clay + peat, 200 years of management
    region.columns["typical_managed"] = SoilColumn(
        location_id="terra_parita_farmland",
        region="northern_minnesota",
        depth_cm=45,  # built over 200 years from original 25cm
        ph=5.2,  # acidic — typical for region
        organic_matter_pct=6.5,  # good — result of 200 years terra parita
        mycorrhizal_density=0.85,  # high — network intact
        microbial_diversity=0.80,
        management_type="terra_parita",
        regen_rate_cm_per_year=0.7,
        extraction_rate_cm_per_year=0.3,  # sustainable harvest
    )
    
    # same land, after paving
    region.columns["post_development"] = SoilColumn(
        location_id="paved_subdivision",
        region="northern_minnesota",
        depth_cm=0,  # entirely removed
        ph=7.2,  # whatever's under the asphalt
        organic_matter_pct=0,
        mycorrhizal_density=0,
        microbial_diversity=0,
        management_type="paved",
        regen_rate_cm_per_year=0,
        extraction_rate_cm_per_year=0,  # extraction complete
    )
    
    return region
