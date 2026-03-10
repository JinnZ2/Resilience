#!/usr/bin/env python3
"""
sim/core.py — all dataclasses and enums
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class Season(Enum):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL   = "fall"

class DensityType(Enum):
    URBAN        = "urban"
    SUBURBAN     = "suburban"
    RURAL_FRINGE = "rural_fringe"

class RedundancyLevel(Enum):
    NONE   = 0
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3

class StressType(Enum):
    SUPPLY_CHAIN_DISRUPTION = "supply_chain_disruption"
    GRID_FAILURE            = "grid_failure"
    POPULATION_INFLUX       = "population_influx"
    SEASONAL_EXTREME        = "seasonal_extreme"
    CASCADING_FAILURE       = "cascading_failure"
    INFRASTRUCTURE_COLLAPSE = "infrastructure_collapse"

class ZoneType(Enum):
    INNER_CITY   = "inner_city"
    SUBURBAN     = "suburban"
    RURAL_FRINGE = "rural_fringe"

@dataclass
class CognitiveReadinessLayer:
    """
    Human wetware as infrastructure.
    Neuroplasticity determines actual response time
    more than any hardware redundancy.

    Constraint-raised brains scan constantly for failure modes.
    Comfort-raised brains default to institutional mediation.
    Under stress, that difference determines survival windows.

    Not a moral judgment. A training artifact.
    Nobody chooses their childhood constraint gradient.
    """
    zone: str                               = ""
    constraint_gradient: float             = 0.0
    # 0.0-1.0 childhood exposure to genuine scarcity and consequence
    # rural_fringe ~0.85 / inner_city ~0.70 / suburban ~0.15
    failure_mode_scanning: float           = 0.0
    abundance_assumption: float            = 0.0
    institutional_mediation_default: float = 0.0
    adaptation_hours_low: float            = 0.0
    adaptation_hours_high: float           = 0.0
    # rural_fringe 2-6h / inner_city 4-12h / suburban 72-720h

    def cognitive_load_path(self) -> str:
        if self.constraint_gradient > 0.6:
            return "LOAD_BEARING — scans for failure modes, acts under uncertainty"
        if self.constraint_gradient > 0.3:
            return "PARTIAL — some capacity, degrades under high stress"
        return "FACADE — comfort layer only, freezes when institutions fail"

    def rewire_window(self) -> str:
        low  = self.adaptation_hours_low  / 24
        high = self.adaptation_hours_high / 24
        if high < 1:
            return f"{self.adaptation_hours_low:.0f}-{self.adaptation_hours_high:.0f}h"
        return f"{low:.1f}-{high:.1f} days"

@dataclass
class DecisionAuthorityNode:
    """
    Who decides what happens to critical buildings during crisis.
    Are they present? Skin in the game?

    Absentee ownership injects entropy into resilient systems.
    A functional mutual aid network can be frozen by one​​​​​​​​​​​​​​​​
