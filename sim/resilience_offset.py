# MODULE: sim/resilience_offset.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: domain
# Thermodynamic bail system for institutions failing tests
# ”””
# resilience_offset.py
#
# Extension to city_optimization.py.
# Provides a formal thermodynamic "Handshake" for institutions that
# fail the 2x/0.5x rule but seek entry into the Registry.
# ”””

@dataclass
class ResilienceOffset:
    """
    The 'Thermodynamic Bail' system.
    If NewNode fails UpgradeTest, it must provide a physical 'Resilience Delta'
    to a Tier 1 (Layer Zero) anchor to neutralize its entropy footprint.
    """
    petitioner_name: str
    energy_deficit_kwh: float  # The 'excess' energy above 0.5x threshold
    purpose_gap_units: float   # The 'missing' output below 2x threshold
    
    # The 'Host' node receiving the offset (e.g., a Rural Clinic or Fire Hall)
    host_anchor_name: str
    offset_type: str           # "Thermal", "Infrastructure", "Skill"

    def calculate_offset_validity(self, host_energy_pre: float, host_energy_post: float) -> bool:
        """
        An offset is VALID if the reduction in the Host's energy (actual - floor)
        is >= 1.5x the Petitioner's energy deficit. 
        (1.5x factor accounts for scale friction and transport loss).
        """
        host_savings = host_energy_pre - host_energy_post
        return host_savings >= (self.energy_deficit_kwh * 1.5)

    def verify_trust_recovery(self, trust_pre: float, trust_post: float) -> float:
        """
        If the offset is 'Skill/Mentorship', we measure the delta in the 
        operator_trust_index. 
        A move from 0.3 (Collapsed) to 0.6 (Recoverable) is a massive system gain.
        """
        return trust_post - trust_pre
