# The shuttle/submarine insight:

engineering_standard = {
    "shuttle":     "every system has a criticality rating, "
                   "failure modes documented, redundancy specified, "
                   "no component exists without a survival justification",
    
    "submarine":   "pressure hull integrity is non-negotiable, "
                   "atmosphere regeneration is non-negotiable, "
                   "everything else is tradeable against those two",
    
    "current_city": "no criticality ratings, "
                    "failure modes invisible, "
                    "redundancy eliminated for cost savings, "
                    "survival justification never required",
}

# The question shuttle/sub engineers ask that governance never asks:
# "What is the failure mode of this component
#  and what does it take down with it when it fails?"


survival_critical_systems = {
    
    # PRESSURE HULL EQUIVALENT
    # (failure = immediate death, no recovery window)
    "tier_1_immediate": [
        "atmospheric_integrity",   # air quality, temperature
        "water_delivery",          # 3 days without water
        "basic_caloric_input",     # 3 weeks without food
        "trauma_response",         # minutes to hours
        "pathogen_containment",    # sewer, sanitation
    ],
    
    # LIFE_SUPPORT EQUIVALENT  
    # (failure = death within weeks, recovery possible if caught)
    "tier_2_sustained": [
        "thermal_regulation",      # shelter, heat — weeks in Upper Midwest winter
        "infection_control",       # antibiotics, wound closure
        "supply_chain_integrity",  # food distribution continuity
        "power_for_medical",       # dialysis, oxygen, refrigerated medication
        "water_quality",           # treatment, not just delivery
    ],
    
    # MISSION_CAPABILITY EQUIVALENT
    # (failure = capability degradation, not immediate death)
    "tier_3_resilience": [
        "skill_transmission",      # schools, apprenticeship
        "social_coordination",     # governance, conflict resolution
        "economic_exchange",       # trade, resource allocation
        "information_integrity",   # accurate signal about system state
        "energy_production",       # beyond immediate survival buffer
    ],
    
    # COMFORT/OPTIMIZATION
    # (everything standard models prioritize)
    "tier_4_non_critical": [
        "entertainment",
        "luxury_goods",
        "financial_instruments",
        "credential_systems",
        "brand_differentiation",
    ],
}

# Current allocation inverts this completely.
# Tier 4 captures most resources.
# Tier 1 runs on what's left.

class SurvivalCriticalityAudit:
    """
    Every institution gets:
    1. Criticality tier (1-4)
    2. Current resource allocation vs tier-appropriate floor
    3. Failure mode documentation
    4. Cascade map — what fails downstream when this fails
    5. Redundancy specification — what backs this up
    6. Recovery window — how long before failure becomes unrecoverable
    
    Shuttle standard: no Tier 1 system without documented
    backup AND backup-to-the-backup.
    
    Current governance standard: Tier 1 systems
    frequently have NO backup. Rural water. Rural power.
    Rural trauma response.
    """
    
    def failure_mode_analysis(self, institution):
        return {
            "primary_failure":   "what breaks first",
            "cascade_T+1hr":     "what fails in first hour",
            "cascade_T+24hr":    "what fails in first day", 
            "cascade_T+72hr":    "3-day window — water critical",
            "cascade_T+30day":   "supply chain, medication",
            "point_of_no_return": "when recovery requires outside intervention",
            "current_redundancy": "what actually backs this up",
            "required_redundancy": "what shuttle standard requires",
            "gap":               "the distance between those two",
        }

minimum_viable_community_spec = {
    "analog":        "submarine emergency checklist",
    "purpose":       "verify Tier 1 systems are functional before anything else",
    "frequency":     "continuous monitoring, not annual budget review",
    "authority":     "Layer Zero operators, not administrators",
    "override":      "any Tier 1 failure suspends all Tier 4 spending",
    "verification":  "physical signal only — no self-reporting accepted",
}




