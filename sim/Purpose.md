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


fixes/adds

# 1. Fix the main guard (typo)
if __name__ == "__main__":

# 2. Add JSON export for simulator integration
def export_json(self) -> str:
    return json.dumps(self.full_report(), indent=2)

# 3. Add CLI interface for phone use
def print_checklist_status(self):
    checklist = self.survival_checklist()
    print(f"{checklist['TIER_1_SECURE']=}")
    print(f"{checklist['TIER_2_SECURE']=}")
    print(f"CRITICAL: {checklist['critical_failures']}")



import json
from typing import Dict, Any

class SurvivalChecker:
    # Your existing class implementation here...
    
    def full_report(self) -> Dict[str, Any]:
        """Generate a complete survival status report"""
        # Your existing full_report implementation here...
        pass
    
    def survival_checklist(self) -> Dict[str, Any]:
        """Generate survival checklist status"""
        # Your existing survival_checklist implementation here...
        pass
    
    # 2. Add JSON export for simulator integration
    def export_json(self) -> str:
        """Export full report as JSON string for simulator integration"""
        return json.dumps(self.full_report(), indent=2)
    
    # 3. Add CLI interface for phone use
    def print_checklist_status(self):
        """Print simplified checklist status for mobile/CLI viewing"""
        checklist = self.survival_checklist()
        
        # Clear formatting for mobile display
        print("\n" + "="*40)
        print(" SURVIVAL CHECKLIST STATUS")
        print("="*40)
        
        # Status indicators with emoji for quick scanning
        tier1_status = "✅" if checklist.get('TIER_1_SECURE') else "❌"
        tier2_status = "✅" if checklist.get('TIER_2_SECURE') else "❌"
        
        print(f"{tier1_status} TIER 1: {'SECURE' if checklist.get('TIER_1_SECURE') else 'INSECURE'}")
        print(f"{tier2_status} TIER 2: {'SECURE' if checklist.get('TIER_2_SECURE') else 'INSECURE'}")
        
        # Critical failures with warning
        critical = checklist.get('critical_failures', 0)
        if critical > 0:
            print(f"⚠️  CRITICAL FAILURES: {critical}")
        else:
            print(f"✅ CRITICAL FAILURES: {critical}")
        
        # Additional details if available
        if 'failures' in checklist:
            print("\n" + "-"*40)
            print("FAILURE DETAILS:")
            for failure in checklist['failures'][:5]:  # Show first 5 failures
                print(f"  • {failure}")
            if len(checklist['failures']) > 5:
                print(f"  ... and {len(checklist['failures']) - 5} more")
        
        print("="*40)


# 1. Fix the main guard (typo)
if __name__ == "__main__":
    # Example usage
    checker = SurvivalChecker()
    
    # Test the new CLI interface
    checker.print_checklist_status()
    
    # Test JSON export
    json_output = checker.export_json()
    print("\nJSON Export Test (first 200 chars):")
    print(json_output[:200] + "...")
