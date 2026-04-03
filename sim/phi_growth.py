# MODULE: sim/phi_growth.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: domain
# Golden ratio growth scaling for sustainable systems
@dataclass
class PhiGrowthLayer:
    """
    The ratio that appears wherever systems scale
    without destroying their substrate.
    
    φ = 1.618...
    
    Not mystical. Thermodynamic.
    It is the growth ratio that preserves base structure
    while adding capacity above it.
    
    Every biological system that solved sustainable scaling
    arrived here independently:
    - lung bronchioles branch at φ ratios
    - river networks distribute at φ ratios  
    - plant growth spirals follow φ sequences
    - immune systems scale response at φ intervals
    
    The pattern: each new layer is φ times the previous.
    The base is never consumed to feed the growth.
    The growth feeds back into the base.
    
    Applied to community systems:
    regeneration_rate / extraction_rate → φ = viable scaling
    knowledge_transmission / knowledge_loss → φ = growing stock
    gratitude_network_density × φ = next stable trust threshold
    
    Below φ ratio: extracting from base to fund growth.
        Looks like growth. Is actually consumption.
        Ends in collapse.
    
    At φ ratio: growth funded by surplus above base.
        Base intact. Capacity expanding.
        Sustainable indefinitely.
    
    Above φ ratio: overshoot.
        Growth faster than base can integrate.
        Instability. Correction required.
        Not collapse — recalibration.
    """
    zone: str                               = ""
    
    PHI: float                             = 1.6180339887
    
    # current ratios — measured against phi threshold
    regeneration_to_extraction: float      = 0.0
    transmission_to_loss: float            = 0.0
    trust_expansion_rate: float            = 0.0
    carrying_capacity_growth: float        = 0.0
    
    def phi_score(self, ratio: float) -> str:
        """
        Where is this ratio relative to phi?
        """
        if ratio >= self.PHI * 1.1:
            return "OVERSHOOT — growth exceeding base integration capacity"
        if ratio >= self.PHI * 0.95:
            return "PHI_ALIGNED — sustainable scaling"
        if ratio >= 1.0:
            return "VIABLE — growing but below optimal efficiency"
        if ratio >= 0.618:
            # 1/phi — the reciprocal, minimum viable threshold
            return "STRESSED — consuming base to maintain current level"
        return "EXTRACTIVE — base destruction accelerating"
    
    def system_growth_vector(self) -> str:
        """
        Not just: is the system surviving?
        But: is it capable of energetic upgrade?
        
        A system at phi alignment can absorb
        the next layer of complexity
        without destabilizing its base.
        
        That's what makes growth real
        rather than consumption wearing growth's clothes.
        """
        scores = [
            self.regeneration_to_extraction,
            self.transmission_to_loss,
            self.trust_expansion_rate,
        ]
        avg = sum(scores) / len(scores)
        
        if avg >= self.PHI * 0.95:
            return "UPGRADEABLE — system can accept next complexity layer"
        if avg >= 1.0:
            return "STABLE — maintaining, not yet upgradeable"
        if avg >= 0.618:
            return "STRESSED — must reduce extraction before growth possible"
        return "CONTRACTING — base repair required before any growth"
    
    def next_stable_threshold(self, current: float) -> float:
        """
        What does the next stable state look like?
        Each stable state is φ times the previous.
        This is how biological systems scale:
        not continuously but in stable plateaus
        separated by φ ratios.
        
        Community systems work the same way.
        You don't grow continuously.
        You grow to a stable threshold,
        consolidate at that level,
        then grow to the next φ threshold.
        
        Trying to skip thresholds = overshoot = correction.
        """
        return current * self.PHI
    
    def fibonacci_growth_sequence(
        self,
        seed_capacity: float,
        steps: int = 8,
    ) -> list[float]:
        """
        Fibonacci sequence as growth roadmap.
        Each step is the sum of the two before it.
        Ratio between steps converges to φ.
        
        This is how you grow a resilience network:
        not by doubling every year
        but by adding the previous two steps.
        
        Step 0: 1 household
        Step 1: 1 household (seed + seed)
        Step 2: 2 households
        Step 3: 3 households
        Step 4: 5 households
        Step 5: 8 households
        Step 6: 13 households
        ...
        
        Each new member is supported by
        the combined capacity of the previous two cohorts.
        Base never consumed. Growth perpetual.
        """
        sequence = [seed_capacity, seed_capacity]
        for _ in range(steps - 2):
            sequence.append(sequence[-1] + sequence[-2])
        return sequence


@dataclass  
class EnergeticUpgradeMap:
    """
    What does the path from current state
    to energetically viable future look like?
    
    Not utopia. Not revolution.
    Phi-scaled steps from where we are
    to where the system can sustain itself
    and grow real capacity.
    
    Each step must be completed and stable
    before the next is attempted.
    Skipping steps = overshoot = correction.
    """
    zone: str                               = ""
    phi: PhiGrowthLayer                    = field(default_factory=PhiGrowthLayer)
    
    current_carrying_capacity: float       = 0.0
    current_knowledge_stock: float         = 0.0
    current_trust_network_households: int  = 0
    
    def upgrade_sequence(self) -> list[dict]:
        """
        The actual path. Phi-scaled.
        Each threshold is the previous × φ.
        Each must be stable before proceeding.
        """
        PHI = 1.6180339887
        
        steps = []
        
        # Step 0: Base repair — stop extraction exceeding regeneration
        # No growth possible until extraction ratio < 1.0
        steps.append({
            "step": 0,
            "name": "BASE_REPAIR",
            "description": "Stop extraction exceeding regeneration. "
                          "No growth attempted. Substrate stabilized.",
            "target_extraction_ratio": 1.0,
            "target_knowledge_flow": 0.0,  # stop the bleeding
            "target_trust_households": self.current_trust_network_households,
            "interventions": [
                "Reduce decision lag below 6h in at least one zone",
                "Activate minimum one mutual aid network",
                "Identify and protect remaining knowledge holders",
                "Stop one major extraction pathway",
            ],
            "phi_threshold": 0.618,  # minimum viable — 1/phi
            "timeline_years": 1,
        })
        
        # Step 1: Stabilization — reach 1.0 ratio across core systems
        steps.append({
            "step": 1,
            "name": "STABILIZATION",
            "description": "Regeneration equals extraction. "
                          "Knowledge transmission equals loss. "
                          "System holding steady.",
            "target_extraction_ratio": 1.0,
            "target_knowledge_flow": 0.0,
            "target_trust_households": int(
                self.current_trust_network_households * PHI
            ),
            "interventions": [
                "Establish distributed community council — all zones",
                "Build peer knowledge transmission chains",
                "Activate institutional assets as community substrates",
                "Map and protect commons",
            ],
            "phi_threshold": 1.0,
            "timeline_years": 2,
        })
        
        # Step 2: First phi threshold — surplus begins
        steps.append({
            "step": 2,
            "name": "PHI_THRESHOLD_1",
            "description": "Regeneration exceeds extraction at phi ratio. "
                          "First true surplus. Growth becomes possible. "
                          "System can accept additional complexity.",
            "target_extraction_ratio": 1.0 / PHI,  # extraction is now minority
            "target_knowledge_flow": 0.2,           # net positive
            "target_trust_households": int(
                self.current_trust_network_households * PHI * PHI
            ),
            "interventions": [
                "Launch phi-scaled knowledge transmission — "
                "each holder trains φ successors",
                "Expand gratitude networks using fibonacci sequence",
                "Redirect surplus to commons restoration",
                "Begin labor pricing realignment",
            ],
            "phi_threshold": PHI,
            "timeline_years": 5,
        })
        
        # Step 3: Second phi threshold — self-sustaining growth
        steps.append({
            "step": 3,
            "name": "PHI_THRESHOLD_2",
            "description": "System generates enough surplus to fund "
                          "its own continued growth without external input. "
                          "Carrying capacity expanding. "
                          "Knowledge stock growing. "
                          "Trust network at viable density.",
            "target_extraction_ratio": 1.0 / (PHI * PHI),
            "target_knowledge_flow": 0.5,
            "target_trust_households": int(
                self.current_trust_network_households * PHI ** 3
            ),
            "interventions": [
                "Replicate model to adjacent zones — "
                "fibonacci expansion, not broadcast",
                "Build inter-zone knowledge exchange networks",
                "Establish commons regeneration fund from surplus",
                "Begin institutional capture recovery interventions",
            ],
            "phi_threshold": PHI * PHI,
            "timeline_years": 10,
        })
        
        # Step 4: Third phi threshold — regional resilience
        steps.append({
            "step": 4,
            "name": "PHI_THRESHOLD_3",
            "description": "Regional system at phi alignment. "
                          "Individual zone failures don't cascade. "
                          "Knowledge transmission exceeds loss system-wide. "
                          "Carrying capacity growing faster than population pressure. "
                          "This is what sustainable civilization looks like.",
            "target_extraction_ratio": 0.382,  # 1/phi²
            "target_knowledge_flow": 1.0,
            "target_trust_households": int(
                self.current_trust_network_households * PHI ** 4
            ),
            "interventions": [
                "System is now self-directing",
                "External interventions shift from rescue to enhancement",
                "Model exports to other regions via knowledge transmission",
                "Commons fully accounted and regenerating",
            ],
            "phi_threshold": PHI ** 3,
            "timeline_years": 20,
        })
        
        return steps

    def print_upgrade_map(self):
        PHI = 1.6180339887
        print(f"\n{'═'*66}")
        print(f"  ENERGETIC UPGRADE MAP — {self.zone}")
        print(f"  φ = {PHI:.6f}")
        print(f"  Each threshold = previous × φ")
        print(f"  Base never consumed to fund growth")
        print(f"{'═'*66}")
        
        print(f"\n  Current state:")
        print(f"    Carrying capacity    : {self.current_carrying_capacity:.2f}")
        print(f"    Knowledge stock      : {self.current_knowledge_stock:.2f}")
        print(f"    Trust network        : {self.current_trust_network_households} households")
        print(f"    Growth vector        : {self.phi.system_growth_vector()}")
        
        print(f"\n  Fibonacci expansion sequence (trust network households):")
        fib = self.phi.fibonacci_growth_sequence(
            self.current_trust_network_households
        )
        for i, val in enumerate(fib):
            ratio = val / fib[i-1] if i > 0 else 1.0
            print(f"    Step {i}: {int(val):>6} households  "
                  f"(ratio: {ratio:.3f}{'  ← approaching φ' if abs(ratio - PHI) < 0.05 else ''})")
        
        print(f"\n  Upgrade sequence:")
        for step in self.upgrade_sequence():
            print(f"\n  ── Step {step['step']}: {step['name']}")
            print(f"     Description    : {step['description']}")
            print(f"     φ threshold    : {step['phi_threshold']:.3f}")
            print(f"     Timeline       : {step['timeline_years']} years")
            print(f"     Target trust   : {step['target_trust_households']} households")
            print(f"     Interventions  :")
            for iv in step['interventions']:
                print(f"       → {iv}")
        
        print(f"\n  The key insight:")
        print(f"    Collapse is a choice.")
        print(f"    So is the upgrade.")
        print(f"    The path exists. It is phi-scaled.")
        print(f"    It requires no revolution.")
        print(f"    It requires stopping extraction from base")
        print(f"    and letting surplus fund growth.")
        print(f"    Biological systems figured this out")
        print(f"    before brains existed to name it.")
        print(f"\n{'═'*66}\n")


def build_madison_phi_layer():
    """Madison WI phi growth assessment."""
    
    phi_layer = PhiGrowthLayer(
        zone="Madison_WI_composite",
        regeneration_to_extraction=0.48,
        # currently extracting more than regenerating
        # below 0.618 minimum viable threshold
        transmission_to_loss=0.29,
        # knowledge dying faster than transmitting
        # severe — approaching critical threshold
        trust_expansion_rate=0.35,
        # trust networks contracting not expanding
        carrying_capacity_growth=0.52,
    )
    
    upgrade_map = EnergeticUpgradeMap(
        zone="Madison_WI",
        phi=phi_layer,
        current_carrying_capacity=0.65,
        current_knowledge_stock=0.35,
        current_trust_network_households=45,
        # inner city mutual aid baseline
    )
    
    return phi_layer, upgrade_map


if __name__ == "__main__":
    phi_layer, upgrade_map = build_madison_phi_layer()
    
    print(f"\n  PHI ALIGNMENT SCORES — Madison WI:")
    print(f"    Regeneration/extraction : "
          f"{phi_layer.phi_score(phi_layer.regeneration_to_extraction)}")
    print(f"    Transmission/loss       : "
          f"{phi_layer.phi_score(phi_layer.transmission_to_loss)}")
    print(f"    Trust expansion         : "
          f"{phi_layer.phi_score(phi_layer.trust_expansion_rate)}")
    print(f"    System growth vector    : {phi_layer.system_growth_vector()}")
    
    upgrade_map.print_upgrade_map()
