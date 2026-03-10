@dataclass
class SubstrateMaintenanceLedger:
    """
    Standardized sensor suite for regional resilience.
    Replaces PRAYER Index (Participation, Revenue, Adherence, Yield, Engagement, Reach)
    with actual thermodynamic indicators.
    """
    
    def audit_node(self, node: EnergyGameNode):
        # 1. Check for 'Heat Leaks' (Extraction vs Regeneration)
        net_flow = node.energy.regeneration_rate - node.energy.extraction_rate
        
        # 2. Check for 'Impedance Match' (Is trust high enough for flow?)
        conductance = sum(node.trust_connections.values()) / len(node.trust_connections)
        
        # 3. Check for 'System Viability' (The Grandmother Test)
        is_viable = (
            node.energy.total() > PHI2 and 
            node.energy.knowledge > 0.5 and 
            net_flow >= 0
        )
        
        return {
            "status": "BUILDING" if net_flow > 0 else "EXTRACTING",
            "viability_flag": is_viable,
            "entropy_risk": "HIGH" if conductance < PHI2 else "LOW"
        }


add in:

@dataclass
class SubstrateMaintenanceLedger:
    """
    Standardized sensor suite for regional resilience.
    
    Replaces PRAYER Index:
    (Participation, Revenue, Adherence, Yield, Engagement, Reach)
    
    With actual thermodynamic indicators.
    
    Authored: Gemini, March 2026
    Integrated: urban-resilience-sim
    CC0 — public domain
    
    The Grandmother Test:
    Does this node have enough knowledge,
    enough energy above survival threshold,
    and positive net flow?
    That is what a grandmother checks
    before sharing resources.
    Unsentimental. Practical. Thermodynamic.
    """

    def audit_node(self, node: 'EnergyGameNode') -> dict:
        
        # 1. Heat leaks — extraction vs regeneration
        # Is this node building or consuming its base?
        regen     = node.energy.total() * 0.05   # estimated regen
        extract   = sum(
            abs(r.energy_given.total())
            for r in node.exchange_history
            if r.action == GameAction.DEFECT
        ) * 0.1  # estimated extraction drain
        net_flow  = regen - extract

        # 2. Impedance match — is trust high enough for energy to flow?
        trust_vals = list(node.trust_connections.values())
        conductance = (
            sum(trust_vals) / len(trust_vals)
            if trust_vals else 0.0
        )

        # 3. The Grandmother Test
        # Three conditions. All must be true.
        # If any fails: node cannot sustain itself
        # or the network that depends on it.
        grandmother_test = (
            node.energy.total()      > PHI2    and  # above survival floor
            node.energy.knowledge    > 0.50    and  # knowledge intact
            net_flow                 >= 0           # not consuming base
        )

        # 4. System Leakage
        # Are extraction flows exceeding regeneration
        # past the point of recovery?
        system_leakage_pct = (
            (extract / regen * 100) if regen > 0 else float('inf')
        )

        return {
            "node_id":            node.node_id,
            "zone":               node.zone,
            "status":             "BUILDING" if net_flow > 0 else "EXTRACTING",
            "net_flow":           round(net_flow, 4),
            "conductance":        round(conductance, 3),
            "impedance_matched":  conductance >= PHI2,
            "grandmother_test":   grandmother_test,
            "system_leakage_pct": round(system_leakage_pct, 1),
            "entropy_risk": (
                "CRITICAL" if system_leakage_pct > 500
                else "HIGH"   if conductance < PHI2
                else "LOW"
            ),
            "intervention": (
                "LOW_ENERGY_TRIAGE — cap extraction immediately"
                if system_leakage_pct > 500
                else "MENTORSHIP_RESET — knowledge below threshold"
                if node.energy.knowledge < 0.50
                else "IMPEDANCE_FIX — build trust connections"
                if conductance < PHI2
                else "NONE — node viable"
            ),
        }

    def audit_network(self, network: 'EnergyGameNetwork') -> list[dict]:
        return [
            self.audit_node(node)
            for node in network.nodes.values()
        ]

    def print_audit(self, network: 'EnergyGameNetwork'):
        results = self.audit_network(network)
        print(f"\n{'═'*66}")
        print(f"  SUBSTRATE MAINTENANCE LEDGER AUDIT")
        print(f"  Replaces: PRAYER Index")
        print(f"  Measures: what actually matters")
        print(f"  Standard: The Grandmother Test")
        print(f"{'═'*66}")

        critical = [r for r in results if r["entropy_risk"] == "CRITICAL"]
        failed   = [r for r in results if not r["grandmother_test"]]

        if critical:
            print(f"\n  ⚠ CRITICAL — LOW ENERGY TRIAGE MODE:")
            print(f"  System leakage > 500% on {len(critical)} nodes.")
            print(f"  Cap extraction before any other intervention.")
            for r in critical:
                print(f"    {r['node_id']} — leakage {r['system_leakage_pct']}%")

        print(f"\n  GRANDMOTHER TEST RESULTS:")
        for r in results:
            gm   = "✓ PASS" if r["grandmother_test"] else "✗ FAIL"
            stat = r["status"]
            print(f"    {r['node_id']:<30} {gm}  [{stat}]")
            if not r["grandmother_test"]:
                print(f"      → {r['intervention']}")

        print(f"\n  IMPEDANCE MAP (trust conductance vs φ⁻¹ threshold {PHI2:.3f}):")
        for r in sorted(results, key=lambda x: x["conductance"]):
            matched = "✓" if r["impedance_matched"] else "✗"
            bar = "█" * int(r["conductance"] * 20)
            print(f"    {matched} {r['node_id']:<28} {r['conductance']:.3f}  {bar}")

        print(f"\n  PRAYER INDEX SCORE: [REDACTED]")
        print(f"  Reason: measures market participation,")
        print(f"          not substrate viability.")
        print(f"          Not useful here.")
        print(f"\n{'═'*66}\n")


add in run.py


from sim.energy_games import (
    build_madison_energy_network,
    print_energy_game_report,
    SubstrateMaintenanceLedger,
)

network = build_madison_energy_network()
print_energy_game_report(network)

ledger = SubstrateMaintenanceLedger()
ledger.print_audit(network)
