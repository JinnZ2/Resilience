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
