#!/usr/bin/env python3
# MODULE: sim/engine.py
# PROVIDES: run_city_assessment, print_report
# DEPENDS: sim.core
# RUN: —
# TIER: core
# Simulation engine — run_city_assessment(), print_report()
"""
sim/engine.py — stress engine and cascade logic
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim
"""

from dataclasses import dataclass, field
from sim.core import (
    CityNode, ResilienceFoundation, InfrastructureLayers,
    StressScenario, RedundancyLevel
)

@dataclass
class ZoneResult:
    zone: str
    runs_forward: bool
    entropy_risk: str
    survival_window_hours: float
    cognitive_load_path: str
    rewire_window: str
    cascade_potential: str
    layer_failures: dict
    chokepoints: list[str]
    redundancy_payoffs: list[str]
    interventions: list[str]

@dataclass
class CascadeResult:
    scenario: StressScenario
    city: str
    zone_results: list[ZoneResult]
    city_wide_chokepoints: list[str]
    priority_interventions: list[str]

def assess_chokepoints(infra: InfrastructureLayers) -> list[str]:
    chokepoints = []
    layers = {
        "water": infra.water, "food": infra.food,
        "energy": infra.energy, "medical": infra.medical,
        "repair": infra.repair, "comms": infra.comms,
        "manufacturing": infra.manufacturing,
    }
    for name, system in layers.items():
        if system.redundancy == RedundancyLevel.NONE:
            chokepoints.append(name)
        if not system.institutional_backups:
            chokepoints.append(f"{name}_no_institutional_backup")
    return chokepoints

def run_zone_assessment(
    zone: ResilienceFoundation,
    infra: InfrastructureLayers,
    scenario: StressScenario,
) -> ZoneResult:
    chokepoints = assess_chokepoints(infra)
    layer_failures = {}
    redundancy_payoffs = []
    interventions = []

    # Layer Zero modifies all infrastructure timelines
    trust_mult      = 0.5 + zone.social_trust_index        # 0.5-1.5
    cognition_mult  = 0.7 + zone.cognition.constraint_gradient * 0.6
    forward         = zone.system_runs_forward()

    layers = {
        "water": infra.water, "food": infra.food,
        "energy": infra.energy, "medical": infra.medical,
        "repair": infra.repair, "comms": infra.comms,
        "manufacturing": infra.manufacturing,
    }

    for name, system in layers.items():
        base_days   = system.days_to_critical or 3
        backed_days = system.days_to_critical_backed or 14

        if name in chokepoints:
            raw   = base_days * 24 * (1 - scenario.severity)
            adj   = raw * trust_mult * cognition_mult
            if not forward: adj *= 0.6
            layer_failures[name] = max(1, int(adj))
        else:
            if system.institutional_backups:
                redundancy_payoffs.append(name)
            raw   = backed_days * 24 * (1 - scenario.severity * 0.4)
            adj   = raw * trust_mult * cognition_mult
            if not forward: adj *= 0.7
            layer_failures[name] = int(adj)

    if not forward:
        interventions.append(
            f"CRITICAL: Establish crisis decision protocol — "
            f"current lag {zone.decision_authority.estimated_decision_lag_hours}h "
            f"will freeze response in {zone.zone}"
        )
    if not zone.mutual_aid_networks_active:
        interventions.append(
            f"Build mutual aid network in {zone.zone} before crisis — "
            f"trust index {zone.social_trust_index:.2f} insufficient under stress"
        )
    if zone.cognition.constraint_gradient < 0.3:
        interventions.append(
            f"Cognitive rewire lag {zone.cognition.rewire_window()} in {zone.zone} — "
            f"peer skill training needed before crisis, not during"
        )
    for cp in set(c.split("_no_")[0] for c in chokepoints):
        interventions.append(
            f"Build redundancy: {cp} in {zone.zone} — "
            f"connect to nearest college/coop asset or local backup"
        )

    return ZoneResult(
        zone=zone.zone,
        runs_forward=forward,
        entropy_risk=zone.entropy_risk(),
        survival_window_hours=zone.survival_window_hours(),
        cognitive_load_path=zone.cognition.cognitive_load_path(),
        rewire_window=zone.cognition.rewire_window(),
        cascade_potential=zone.social_trust.cascade_potential(),
        layer_failures=layer_failures,
        chokepoints=chokepoints,
        redundancy_payoffs=redundancy_payoffs,
        interventions=interventions,
    )

def run_city_assessment(city: CityNode, scenario: StressScenario) -> CascadeResult:
    zone_results = []
    for zone in city.zones:
        zr = run_zone_assessment(zone, city.infrastructure, scenario)
        zone_results.append(zr)

    all_chokepoints = list({
        cp for zr in zone_results for cp in zr.chokepoints
    })

    priority = []
    for zr in sorted(zone_results, key=lambda z: z.survival_window_hours):
        if not zr.runs_forward:
            priority.append(
                f"URGENT — {zr.zone}: {zr.entropy_risk} "
                f"({zr.survival_window_hours:.0f}h window)"
            )
    for zr in zone_results:
        priority.extend(zr.interventions)

    return CascadeResult(
        scenario=scenario,
        city=city.name,
        zone_results=zone_results,
        city_wide_chokepoints=all_chokepoints,
        priority_interventions=priority,
    )

def print_report(result: CascadeResult):
    print(f"\n{'═'*66}")
    print(f"  URBAN RESILIENCE REPORT: {result.city}")
    print(f"  Scenario : {result.scenario.type.value}")
    print(f"  Severity : {result.scenario.severity:.0%} | "
          f"Duration: {result.scenario.duration_days}d | "
          f"Season: {result.scenario.season.value}")
    if result.scenario.notes:
        print(f"  Notes    : {result.scenario.notes}")
    print(f"{'═'*66}")

    for zr in result.zone_results:
        fwd = "✓ RUNS FORWARD" if zr.runs_forward else "✗ FROZEN"
        print(f"\n  ── ZONE: {zr.zone.upper()} [{fwd}]")
        print(f"     Entropy risk      : {zr.entropy_risk}")
        print(f"     Survival window   : {zr.survival_window_hours:.0f}h "
              f"({zr.survival_window_hours/24:.1f}d)")
        print(f"     Cognitive layer   : {zr.cognitive_load_path}")
        print(f"     Rewire lag        : {zr.rewire_window}")
        print(f"     Cascade potential : {zr.cascade_potential}")
        print(f"\n     Layer failure timeline (hours to critical):")
        for layer, hours in sorted(zr.layer_failures.items(), key=lambda x: x[1]):
            flag = " ⚠ CHOKEPOINT" if layer in zr.chokepoints else ""
            print(f"       {layer:<22} {hours:>6}h  ({hours/24:.1f}d){flag}")
        if zr.redundancy_payoffs:
            print(f"\n     Redundancy assets buffering:")
            for r in zr.redundancy_payoffs:
                print(f"       ✓ {r}")

    print(f"\n  PRIORITY INTERVENTIONS (by urgency):")
    seen = []
    count = 1
    for rec in result.priority_interventions:
        if rec not in seen:
            print(f"    {count:>2}. {rec}")
            seen.append(rec)
            count += 1
        if count > 12: break

    print(f"\n{'═'*66}\n")
