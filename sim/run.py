#!/usr/bin/env python3
"""
run.py — entry point
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Usage:
    python run.py
"""

from sim.core import StressScenario, StressType, Season
from sim.engine import run_city_assessment, print_report
from sim.cities.madison_wi import build_madison

if __name__ == "__main__":
    city = build_madison()

    scenarios = [
        StressScenario(
            type=StressType.GRID_FAILURE,
            severity=0.8,
            duration_days=10,
            season=Season.WINTER,
            notes="Winter grid failure — pump stations on generator, "
                  "sewage cascade risk to aquifer recharge zones",
        ),
        StressScenario(
            type=StressType.SUPPLY_CHAIN_DISRUPTION,
            severity=0.7,
            duration_days=14,
            season=Season.WINTER,
            notes="Midwest winter supply chain disruption — roads compromised",
        ),
    ]

    for scenario in scenarios:
        result = run_city_assessment(city, scenario)
        print_report(result)
