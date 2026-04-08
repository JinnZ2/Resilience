#!/usr/bin/env python3
# MODULE: sim/urban_grid.py
# PROVIDES: RESILIENCE.URBAN_GRID
# DEPENDS: stdlib-only
# RUN: python -m sim.urban_grid
# TIER: domain
# Urban magnomechanical grid retrofit with transducer networks
"""
sim/urban_grid.py — Urban Magnomechanical Grid
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

The city is already a geothermal transducer.

Everywhere there's concrete: thermal mass.
Everywhere there's a basement: stable temperature at depth.
Everywhere there's a pipe: pressure cycling = energy.
Everywhere there's a parking garage: vibration + thermal swing.

This module models retrofit of existing urban infrastructure
with transducer networks. No new land. No new mining.
Work with what's already dug.

Phase 1: Water/sewer pipe junctions (years 1-3)
Phase 2: Building basements (years 2-5)
Phase 3: Parking garages + tunnels (years 3-7)

Power is the byproduct. Data is the product.

USAGE:
    python -m sim.urban_grid
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from sim.crisis_geology import (
    SEEBECK_NATURAL, SEEBECK_BISMUTH, STREAMING_COEFF,
    PYRO_TOURMALINE, TEG_RESISTANCE,
)


# =============================================================================
# INFRASTRUCTURE ELEMENT — a place to put a transducer
# =============================================================================

@dataclass
class InfraElement:
    """One piece of urban infrastructure that can host transducers."""
    name: str
    element_type: str           # pipe, basement, garage, tunnel
    count_per_city: int         # how many in a 1M-person city
    depth_m: float              # average depth below surface
    temp_swing_daily_c: float   # daily temperature variation
    temp_swing_seasonal_c: float
    pressure_cycling_bar: float # pressure variation (water pipes)
    vibration_hz: float         # mechanical vibration frequency
    vibration_g: float          # vibration amplitude (g)
    water_flow: bool            # is water flowing through it?
    transducer_cost_usd: float  # cost per transducer installed
    install_method: str         # how it gets installed

    def thermoelectric_power_uw(self) -> float:
        """Thermoelectric from thermal gradient (uW per transducer)."""
        dt = math.sqrt((self.temp_swing_daily_c * 0.3) ** 2 +
                       (self.temp_swing_seasonal_c * 0.2) ** 2)
        if dt < 0.1:
            return 0.0
        n_couples = 10
        voltage = n_couples * SEEBECK_NATURAL * dt
        power = 0.5 * voltage * (voltage / TEG_RESISTANCE)
        return power * 1e6

    def streaming_power_uw(self) -> float:
        """Streaming potential from water/fluid flow (uW)."""
        if not self.water_flow or self.pressure_cycling_bar <= 0:
            return 0.0
        # Pressure cycling creates oscillating flow
        head_m = self.pressure_cycling_bar * 10.2  # bar to meters of water
        voltage = STREAMING_COEFF * head_m
        power = 0.5 * voltage * (voltage / 500.0)
        return power * 1e6

    def vibration_power_uw(self) -> float:
        """Power from mechanical vibration (uW). Piezo harvester."""
        if self.vibration_g <= 0:
            return 0.0
        # PZT harvester (not natural quartz — manufactured for this)
        # Typical: 10-100 uW/g^2 at resonance
        # Derated for broadband: 1-10 uW/g^2
        power_per_g2 = 5.0  # uW per g^2 (conservative broadband)
        return power_per_g2 * self.vibration_g ** 2

    def total_power_uw(self) -> float:
        return (self.thermoelectric_power_uw() +
                self.streaming_power_uw() +
                self.vibration_power_uw())

    def city_total_w(self) -> float:
        """Total power from all transducers of this type in one city (W)."""
        return self.total_power_uw() * 1e-6 * self.count_per_city

    def city_total_cost_m(self) -> float:
        """Total cost for all transducers in one city ($M)."""
        return self.transducer_cost_usd * self.count_per_city / 1e6

    def power_breakdown(self) -> Dict[str, float]:
        return {
            "thermoelectric_uW": round(self.thermoelectric_power_uw(), 3),
            "streaming_uW": round(self.streaming_power_uw(), 3),
            "vibration_uW": round(self.vibration_power_uw(), 3),
            "total_uW": round(self.total_power_uw(), 3),
        }


# =============================================================================
# CITY INFRASTRUCTURE LIBRARY
# =============================================================================

def build_infrastructure() -> List[InfraElement]:
    """Infrastructure types for a 1-million-person city."""
    return [
        # --- Phase 1: Water/Sewer (years 1-3) ---
        InfraElement(
            name="Water main junction",
            element_type="pipe", count_per_city=20000,
            depth_m=2.0, temp_swing_daily_c=3.0, temp_swing_seasonal_c=15.0,
            pressure_cycling_bar=2.0, vibration_hz=5.0, vibration_g=0.01,
            water_flow=True, transducer_cost_usd=30,
            install_method="insert at access port during routine maintenance",
        ),
        InfraElement(
            name="Sewer line access",
            element_type="pipe", count_per_city=15000,
            depth_m=3.0, temp_swing_daily_c=2.0, temp_swing_seasonal_c=10.0,
            pressure_cycling_bar=0.5, vibration_hz=2.0, vibration_g=0.005,
            water_flow=True, transducer_cost_usd=25,
            install_method="attach at manhole during inspection cycle",
        ),
        InfraElement(
            name="Fire hydrant node",
            element_type="pipe", count_per_city=5000,
            depth_m=1.5, temp_swing_daily_c=5.0, temp_swing_seasonal_c=20.0,
            pressure_cycling_bar=4.0, vibration_hz=10.0, vibration_g=0.02,
            water_flow=True, transducer_cost_usd=40,
            install_method="replace valve cap with transducer cap",
        ),

        # --- Phase 2: Buildings (years 2-5) ---
        InfraElement(
            name="Building basement wall",
            element_type="basement", count_per_city=30000,
            depth_m=5.0, temp_swing_daily_c=2.0, temp_swing_seasonal_c=12.0,
            pressure_cycling_bar=0.0, vibration_hz=15.0, vibration_g=0.008,
            water_flow=False, transducer_cost_usd=200,
            install_method="mount on foundation wall during renovation",
        ),
        InfraElement(
            name="Building HVAC duct",
            element_type="basement", count_per_city=50000,
            depth_m=0.0, temp_swing_daily_c=15.0, temp_swing_seasonal_c=30.0,
            pressure_cycling_bar=0.0, vibration_hz=20.0, vibration_g=0.015,
            water_flow=False, transducer_cost_usd=50,
            install_method="clip onto existing ductwork",
        ),

        # --- Phase 3: Garages/Tunnels (years 3-7) ---
        InfraElement(
            name="Parking garage slab",
            element_type="garage", count_per_city=500,
            depth_m=10.0, temp_swing_daily_c=10.0, temp_swing_seasonal_c=25.0,
            pressure_cycling_bar=0.0, vibration_hz=8.0, vibration_g=0.05,
            water_flow=False, transducer_cost_usd=15,
            install_method="embed in concrete at pour (new) or surface mount (retrofit)",
        ),
        InfraElement(
            name="Subway/transit tunnel",
            element_type="tunnel", count_per_city=200,
            depth_m=15.0, temp_swing_daily_c=3.0, temp_swing_seasonal_c=8.0,
            pressure_cycling_bar=0.0, vibration_hz=5.0, vibration_g=0.1,
            water_flow=False, transducer_cost_usd=100,
            install_method="mount on tunnel wall at existing access points",
        ),
        InfraElement(
            name="Bridge/overpass pier",
            element_type="tunnel", count_per_city=1000,
            depth_m=0.0, temp_swing_daily_c=20.0, temp_swing_seasonal_c=40.0,
            pressure_cycling_bar=0.0, vibration_hz=3.0, vibration_g=0.03,
            water_flow=False, transducer_cost_usd=75,
            install_method="bolt to pier during inspection cycle",
        ),
    ]


# =============================================================================
# CITY MODEL — aggregate across all infrastructure
# =============================================================================

@dataclass
class CityGrid:
    """A city's magnomechanical grid deployment."""
    city_name: str
    population: int = 1_000_000
    elements: List[InfraElement] = field(default_factory=list)

    def total_power_w(self) -> float:
        return sum(e.city_total_w() for e in self.elements)

    def total_cost_m(self) -> float:
        return sum(e.city_total_cost_m() for e in self.elements)

    def total_nodes(self) -> int:
        return sum(e.count_per_city for e in self.elements)

    def watts_per_person(self) -> float:
        return self.total_power_w() / max(1, self.population)

    def phase_summary(self) -> Dict[str, Dict]:
        """Aggregate by deployment phase."""
        phases = {
            "pipe": {"name": "Phase 1: Water/Sewer", "years": "1-3"},
            "basement": {"name": "Phase 2: Buildings", "years": "2-5"},
            "garage": {"name": "Phase 3: Garages", "years": "3-7"},
            "tunnel": {"name": "Phase 3: Tunnels", "years": "3-7"},
        }
        result = {}
        for phase_type, meta in phases.items():
            elems = [e for e in self.elements if e.element_type == phase_type]
            if elems:
                power = sum(e.city_total_w() for e in elems)
                cost = sum(e.city_total_cost_m() for e in elems)
                nodes = sum(e.count_per_city for e in elems)
                result[phase_type] = {
                    "name": meta["name"],
                    "years": meta["years"],
                    "nodes": nodes,
                    "power_w": round(power, 4),
                    "cost_m": round(cost, 2),
                }
        return result

    def data_capabilities(self) -> List[str]:
        """What the network can measure (the real product)."""
        capabilities = []
        has_pipe = any(e.element_type == "pipe" for e in self.elements)
        has_basement = any(e.element_type == "basement" for e in self.elements)
        has_garage = any(e.element_type == "garage" for e in self.elements)
        has_tunnel = any(e.element_type == "tunnel" for e in self.elements)

        if has_pipe:
            capabilities.extend([
                "Water leak detection (pressure anomaly, 2-4 week lead time)",
                "Water quality monitoring (temperature + conductivity proxy)",
                "Pipe stress state (predict burst before it happens)",
                "Aquifer level tracking (aggregate pressure trends)",
            ])
        if has_basement:
            capabilities.extend([
                "Subsidence detection (foundation movement, weeks early)",
                "Groundwater intrusion alert (temperature anomaly)",
                "HVAC optimization (real ground temperature, not estimate)",
                "Structural health monitoring (vibration signature changes)",
            ])
        if has_garage or has_tunnel:
            capabilities.extend([
                "Seismic early warning (P-wave detection, 20-30 second lead)",
                "Traffic flow sensing (vibration patterns = congestion)",
                "Structural fatigue monitoring (crack propagation signature)",
                "Air quality proxy (thermal plume from ventilation patterns)",
            ])
        return capabilities


# =============================================================================
# SCALING MODEL — from 1 city to global
# =============================================================================

def scale_deployment(city: CityGrid, num_cities: int) -> Dict:
    """Scale one city model to N cities globally."""
    return {
        "cities": num_cities,
        "total_nodes": city.total_nodes() * num_cities,
        "total_power_kw": round(city.total_power_w() * num_cities / 1000, 3),
        "total_cost_b": round(city.total_cost_m() * num_cities / 1000, 2),
        "population_covered": city.population * num_cities,
    }


# =============================================================================
# REPORT
# =============================================================================

def print_report():
    elements = build_infrastructure()
    city = CityGrid(city_name="Madison WI (reference)", elements=elements)

    print(f"\n{'='*65}")
    print(f"  URBAN MAGNOMECHANICAL GRID")
    print(f"  The city is already a geothermal transducer")
    print(f"{'='*65}")

    # Per-element breakdown
    print(f"\n  INFRASTRUCTURE ELEMENTS (per unit):")
    for e in elements:
        bd = e.power_breakdown()
        print(f"\n    {e.name}")
        print(f"      Type: {e.element_type}  Depth: {e.depth_m}m  Cost: ${e.transducer_cost_usd}")
        print(f"      Install: {e.install_method}")
        print(f"      Power: {bd['total_uW']:.3f} uW  "
              f"(thermo={bd['thermoelectric_uW']:.3f}  "
              f"stream={bd['streaming_uW']:.3f}  "
              f"vibe={bd['vibration_uW']:.3f})")

    # Phase summary
    print(f"\n  DEPLOYMENT PHASES (1M-person city):")
    phases = city.phase_summary()
    for phase_type, data in phases.items():
        power_w = data['power_w']
        print(f"\n    {data['name']} (years {data['years']})")
        print(f"      Nodes: {data['nodes']:,}  "
              f"Power: {power_w:.1f} W  "
              f"Cost: ${data['cost_m']:.2f}M")

    # City totals
    total_w = city.total_power_w()
    print(f"\n  CITY TOTAL:")
    print(f"    Nodes: {city.total_nodes():,}")
    print(f"    Power: {total_w:.1f} W ({total_w/1000:.2f} kW)")
    print(f"    Cost: ${city.total_cost_m():.2f}M")
    print(f"    Watts/person: {city.watts_per_person()*1000:.2f} mW")

    # What the power covers
    wpp_mw = city.watts_per_person() * 1000  # milliwatts
    print(f"\n  WHAT {wpp_mw:.2f} mW/PERSON COVERS:")
    if wpp_mw > 0.25:
        print(f"    LoRa mesh (per person): {wpp_mw / 0.25:.0f}x sustained")
    if wpp_mw > 1:
        print(f"    Sensor network: {wpp_mw / 0.5:.0f} always-on sensors/person")
    print(f"    Primary value is DATA, not power")

    # Data capabilities
    caps = city.data_capabilities()
    if caps:
        print(f"\n  DATA CAPABILITIES (the real product):")
        for cap in caps:
            print(f"    - {cap}")

    # Scaling
    print(f"\n  SCALING:")
    for n, label in [(10, "10 cities"), (100, "100 cities"), (1000, "1000 cities")]:
        s = scale_deployment(city, n)
        power_kw = s['total_power_kw']
        print(f"    {label:12s}: {power_kw:.0f} kW  "
              f"${s['total_cost_b']:.1f}B  "
              f"{s['population_covered']/1e9:.1f}B people  "
              f"{s['total_nodes']/1e6:.1f}M nodes")

    # Transition timeline
    print(f"\n  HONEST TRANSITION TIMELINE:")
    timeline = [
        ("2026-2030", "Phase 1: Water pipes",
         "Prove concept. Detect leaks. Save money immediately."),
        ("2030-2035", "Phase 2: Buildings",
         "Basement systems in new construction. Retrofit at renovation."),
        ("2035-2045", "Phase 3: Garages + tunnels",
         "Seismic early warning. Traffic optimization. Grid stabilization."),
        ("2045+", "Distributed grid emerges",
         "Buildings generate baseline power. Grid becomes balancing system."),
    ]
    for years, phase, desc in timeline:
        print(f"    {years}: {phase}")
        print(f"      {desc}")

    # The conversation
    print(f"\n{'='*65}")
    print(f"  THE HONEST CONVERSATION")
    print(f"{'='*65}")
    print("""
  Not: "replace the grid with rocks"
  But: "the infrastructure you already built can do more work"

  Water pipes already carry pressure cycling = energy.
  Basements already have thermal gradients = energy.
  Garages already vibrate from traffic = energy.
  Tunnels already conduct heat = sensing.

  The power is small. The data is enormous.

  Detect a water main break 2 weeks before it happens:
  saves $500K per incident. One break pays for 10,000 nodes.

  Detect foundation subsidence before the building cracks:
  saves lives. No dollar value.

  Detect a seismic P-wave 20 seconds before shaking starts:
  enough time to stop elevators, open fire station doors,
  alert hospitals to brace.

  The network pays for itself on data alone.
  The power is a bonus.
""")


if __name__ == "__main__":
    print_report()
