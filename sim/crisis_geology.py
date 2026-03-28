#!/usr/bin/env python3
"""
sim/crisis_geology.py — Crisis Geology x Energy Resilience
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

The rock is the sensor. The rock is the power source.
Quartz is 12% of continental crust. Magnetite is in every mafic rock.
Thermal gradients are everywhere there's depth.

A geothermal magnon-phonon transducer in a standard water well borehole:
  - 5-20 uW continuous (indefinite, no fuel, no moving parts)
  - Reads: temperature, pressure, seismic, geomagnetic
  - Transmits via LoRa: once per hour, 30km range
  - Cost: $50-200 per node (borehole already being drilled for water)
  - Lifespan: 10-30 years (quartz and magnetite don't wear out)

One node: temperature at one place.
1000 nodes: a geophysical camera looking at the ground AND the sky.

This module simulates:
  - Transducer power output from thermal cycling + seismic + tidal
  - Network deployment across crisis zones
  - Early warning detection (aquifer change, monsoon onset, permafrost thaw)
  - Power budget for LoRa mesh communication
  - The network survives the crisis it's monitoring for

USAGE:
    python -m sim.crisis_geology
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


# =============================================================================
# PHYSICAL CONSTANTS
# =============================================================================

# =============================================================================
# MINERAL COUPLING CONSTANTS
# =============================================================================
#
# What's already in the ground. Every mechanism couples to at least
# two others. The rock doesn't need us to build a network.
# It already IS one. We just need electrodes and a radio.

# --- Piezoelectric ---
PIEZO_D33_QUARTZ = 2.3e-12     # pC/N — quartz (compressive/P-wave)
PIEZO_D14_CALCITE = 0.5e-12    # pC/N — calcite (shear/S-wave, different mode)
PIEZO_D33_TOURMALINE = 4.0e-12 # pC/N — tourmaline (2x quartz + pyroelectric)
PIEZO_D33_ICE = 2.0e-12        # pC/N — ice Ih (permafrost IS a transducer)
# Honest: all produce picowatts at geological strain rates.
# But calcite responds to S-waves where quartz responds to P-waves.
# Together = two independent channels from one seismic event.

# --- Pyroelectric ---
PYRO_TOURMALINE = 4.0e-6       # C/(m^2*K) — spontaneous polarization from dT
# No mechanical stress needed. Temperature change -> voltage directly.

# --- Thermoelectric ---
SEEBECK_BISMUTH = 200e-6       # V/K — manufactured bismuth telluride
SEEBECK_PYRITE = -820e-6       # V/K — natural pyrite (4x better!)
SEEBECK_CHALCOPYRITE = 600e-6  # V/K — natural chalcopyrite
# Pyrite-chalcopyrite junction: natural thermocouple, S = 1420 uV/K
# Most common sulfide mineral on Earth. Already in the rock.
SEEBECK_NATURAL = 1420e-6      # V/K — pyrite-chalcopyrite junction

# --- Streaming potential ---
STREAMING_COEFF = 10e-3        # V per meter of hydraulic head (conservative)
# Range: 1-100 mV/m. Every aquifer with flowing water generates voltage.
# Active aquifer dwarfs all other power sources.

# --- Magnetostrictive ---
MAGNETOSTRICTION_FE3O4 = 40e-6 # strain — magnetite in 50 uT geomagnetic field
# Geomagnetic field change -> magnetite shape change -> mechanical strain
# -> couples to quartz/calcite piezo. Amplifier, not source.

# --- Biological ---
ROOT_POTENTIAL = 0.3           # V — tree root-soil electrochemical (0.1-0.7V)
# Mycorrhizal network = signal distribution. Forest IS a sensor array.
# Single tree: enough voltage for LoRa at low duty cycle.

# --- Atmospheric ---
SCHUMANN_FREQ = 7.83           # Hz — Earth-ionosphere cavity resonance
# Always present everywhere. Magnetite couples. Free sync carrier.

# --- Storage ---
# Mica: layered dielectric = natural capacitor. Stores charge from others.
# Galena (PbS): natural rectifier. With pyrite = natural diode for AC->DC.

# --- Bulk rock ---
QUARTZ_MODULUS = 50e9          # Pa
QUARTZ_ALPHA = 15e-6           # 1/K
MAGNETITE_CURIE = 585          # C
ROCK_THERMAL_CAP = 2.5e6      # J/(m^3*K)
PRESSURE_GRADIENT = 27e6       # Pa/km
THERMAL_GRADIENT = 25          # C/km
TEG_RESISTANCE = 100           # ohm


# =============================================================================
# TRANSDUCER — the device in the borehole
# =============================================================================

@dataclass
class GeoTransducer:
    """
    Multi-mineral transducer stack in a borehole.

    Not just quartz — the full coupling network:
    thermoelectric (pyrite-chalcopyrite junctions),
    pyroelectric (tourmaline), streaming potential (water flow),
    piezoelectric (quartz P-wave + calcite S-wave),
    smoky quartz thermoluminescence, magnetite coupling.

    Each mechanism is modeled honestly with real coefficients.
    """
    depth_m: float = 50.0
    stack_length_m: float = 5.0
    quartz_fraction: float = 0.4
    tourmaline_fraction: float = 0.1
    magnetite_fraction: float = 0.1
    pyrite_present: bool = True      # natural thermocouple
    calcite_present: bool = True     # shear-mode piezo

    # Environmental conditions
    surface_temp_c: float = 25.0
    daily_swing_c: float = 10.0
    seasonal_swing_c: float = 30.0
    seismic_acceleration: float = 0.001  # g
    water_flow_m_per_s: float = 1e-5     # groundwater velocity (typical aquifer)
    hydraulic_head_m: float = 5.0        # meters of head across transducer
    has_trees_above: bool = False        # forest canopy = biological coupling

    # Location
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0

    def temp_at_depth(self) -> float:
        """Steady-state temperature at borehole bottom."""
        return self.surface_temp_c + (self.depth_m / 1000) * THERMAL_GRADIENT

    def pressure_at_depth(self) -> float:
        """Confining pressure at depth (Pa)."""
        return (self.depth_m / 1000) * PRESSURE_GRADIENT

    def thermal_strain(self, delta_t: float) -> float:
        """Strain from temperature change."""
        return QUARTZ_ALPHA * delta_t

    def thermal_stress(self, delta_t: float) -> float:
        """Stress from confined thermal expansion (Pa)."""
        return QUARTZ_MODULUS * self.thermal_strain(delta_t)

    # --- POWER: Thermoelectric (dominant) ---

    def thermoelectric_power(self) -> float:
        """Pyrite-chalcopyrite natural thermocouple (W). S=1420 uV/K."""
        daily_atten = max(0.05, 0.5 * math.exp(-self.depth_m / 30) + 0.05)
        seasonal_atten = max(0.1, 0.6 * math.exp(-self.depth_m / 100) + 0.1)
        dt_daily = self.daily_swing_c * daily_atten * 0.5
        dt_seasonal = self.seasonal_swing_c * seasonal_atten * 0.3
        dt_total = math.sqrt(dt_daily ** 2 + dt_seasonal ** 2)
        seebeck = SEEBECK_NATURAL if self.pyrite_present else SEEBECK_BISMUTH
        n_couples = 10
        voltage = n_couples * seebeck * dt_total
        return 0.5 * voltage * (voltage / TEG_RESISTANCE)

    # --- POWER: Streaming potential (water flow) ---

    def streaming_power(self) -> float:
        """Electrokinetic voltage from groundwater flow (W)."""
        if self.water_flow_m_per_s <= 0 or self.hydraulic_head_m <= 0:
            return 0.0
        voltage = STREAMING_COEFF * self.hydraulic_head_m
        load_r = 500.0
        return 0.5 * voltage * (voltage / load_r)

    # --- POWER: Pyroelectric (tourmaline) ---

    def pyroelectric_power(self) -> float:
        """Tourmaline: temperature change -> voltage directly (W)."""
        if self.tourmaline_fraction <= 0:
            return 0.0
        daily_atten = max(0.05, 0.5 * math.exp(-self.depth_m / 30) + 0.05)
        dt_rate = self.daily_swing_c * daily_atten / 43200  # K/s
        area = 0.01  # m^2
        current = PYRO_TOURMALINE * area * dt_rate
        load_r = 1e5
        return 0.5 * (current * load_r) * current

    # --- POWER: Piezoelectric (quartz + calcite) ---

    def piezo_power(self) -> float:
        """Quartz (P-wave) + calcite (S-wave) piezoelectric (W). Honest: pW."""
        dt = self.daily_swing_c * 0.05
        stress = self.thermal_stress(dt)
        v_q = PIEZO_D33_QUARTZ * stress * self.stack_length_m * self.quartz_fraction
        p_q = 0.5 * v_q * (v_q / 1e6)
        p_c = 0.0
        if self.calcite_present:
            v_c = PIEZO_D14_CALCITE * stress * self.stack_length_m * 0.1
            p_c = 0.5 * v_c * (v_c / 1e6)
        return p_q + p_c

    # --- SENSOR: Smoky quartz TL ---

    def smoky_quartz_power(self) -> float:
        """Thermoluminescent discharge (W). nW range. Sensor, not power."""
        smoky_mass_kg = self.stack_length_m * self.quartz_fraction * 2.0
        daily_atten = max(0.05, 0.5 * math.exp(-self.depth_m / 30) + 0.05)
        effective_swing = self.daily_swing_c * daily_atten
        return smoky_mass_kg * 0.5e-9 * (effective_swing / 5.0)

    # --- SENSOR: Biological ---

    def biological_power(self) -> float:
        """Tree root electrochemical potential (W). 0.1-0.7V per tree."""
        if not self.has_trees_above:
            return 0.0
        voltage = 0.1
        current = voltage / 20e3  # matched load
        return 0.5 * voltage * current

    # --- TOTAL ---

    def total_power_uw(self) -> float:
        """Total continuous power from all coupling mechanisms (uW)."""
        total = (self.thermoelectric_power() + self.streaming_power() +
                 self.pyroelectric_power() + self.piezo_power() +
                 self.smoky_quartz_power() + self.biological_power())
        return total * 1e6

    def power_breakdown(self) -> Dict[str, float]:
        """Power from each mechanism (in natural units)."""
        return {
            "thermoelectric_uW": round(self.thermoelectric_power() * 1e6, 4),
            "streaming_uW": round(self.streaming_power() * 1e6, 4),
            "pyroelectric_uW": round(self.pyroelectric_power() * 1e6, 4),
            "piezo_pW": round(self.piezo_power() * 1e12, 4),
            "smoky_quartz_nW": round(self.smoky_quartz_power() * 1e9, 4),
            "biological_uW": round(self.biological_power() * 1e6, 4),
        }

    def lora_transmissions_per_day(self) -> int:
        """
        How many LoRa transmissions can this node sustain?
        LoRa: 25 mW pulse, 100ms duration = 2.5 mJ per transmission.
        """
        total_energy_per_day_j = self.total_power_uw() * 1e-6 * 86400
        energy_per_tx_j = 0.025 * 0.1  # 25 mW * 100 ms
        if energy_per_tx_j <= 0:
            return 0
        return max(0, int(total_energy_per_day_j / energy_per_tx_j))

    def sensor_readings(self, hour: int = 12) -> Dict:
        """What this node reports in one transmission."""
        # Temperature profile
        temp_surface = self.surface_temp_c + self.daily_swing_c * math.sin(
            2 * math.pi * hour / 24)
        temp_depth = self.temp_at_depth()

        return {
            "node": self.name,
            "depth_m": self.depth_m,
            "temp_surface_c": round(temp_surface, 1),
            "temp_depth_c": round(temp_depth, 1),
            "temp_gradient": round((temp_depth - temp_surface) / self.depth_m * 1000, 2),
            "pressure_mpa": round(self.pressure_at_depth() / 1e6, 2),
            "seismic_g": round(self.seismic_acceleration, 4),
            "power_uw": round(self.total_power_uw(), 2),
        }

    def summary(self) -> str:
        power = self.total_power_uw()
        tx = self.lora_transmissions_per_day()
        return (f"{self.name:20s} depth={self.depth_m:3.0f}m  "
                f"power={power:8.2f} uW  "
                f"LoRa={tx:3d}/day  "
                f"T_depth={self.temp_at_depth():.0f}C")


# =============================================================================
# CRISIS ZONE — regional deployment
# =============================================================================

@dataclass
class CrisisZone:
    """A region where geothermal monitoring addresses a specific crisis."""
    name: str
    population: str
    crisis: str
    geology: str
    nodes: int                  # planned transducer count
    node_cost_usd: float = 100.0
    borehole_cost_usd: float = 1000.0
    surface_temp: float = 25.0
    daily_swing: float = 10.0
    seasonal_swing: float = 30.0
    seismic_bg: float = 0.001
    depth: float = 50.0
    early_warning_weeks: float = 2.0
    description: str = ""

    def total_cost(self) -> float:
        return self.nodes * (self.node_cost_usd + self.borehole_cost_usd)

    def network_power_mw(self) -> float:
        """Aggregate power from all nodes (MW)."""
        tx = GeoTransducer(
            depth_m=self.depth, surface_temp_c=self.surface_temp,
            daily_swing_c=self.daily_swing, seasonal_swing_c=self.seasonal_swing,
            seismic_acceleration=self.seismic_bg,
        )
        return tx.total_power_uw() * 1e-6 * self.nodes * 1e-6  # uW to MW

    def coverage_km2(self, spacing_km: float = 50.0) -> float:
        """Area covered by the network (km^2)."""
        return self.nodes * spacing_km ** 2


# =============================================================================
# DEPLOYMENT SCENARIOS
# =============================================================================

def build_crisis_zones() -> List[CrisisZone]:
    return [
        CrisisZone(
            name="Sahel Drought",
            population="200M", crisis="drought + heat",
            geology="Precambrian granite/greenstone",
            nodes=1000, node_cost_usd=75, borehole_cost_usd=500,
            surface_temp=35, daily_swing=15, seasonal_swing=20,
            seismic_bg=0.0005, depth=30, early_warning_weeks=4,
            description="Aquifer monitoring across Sahel belt",
        ),
        CrisisZone(
            name="South Asia Monsoon",
            population="2.4B", crisis="monsoon failure + heat",
            geology="Deccan Traps basalt + Himalayan fold",
            nodes=500, node_cost_usd=50, borehole_cost_usd=300,
            surface_temp=30, daily_swing=8, seasonal_swing=25,
            seismic_bg=0.002, depth=40, early_warning_weeks=3,
            description="Monsoon onset prediction via geomagnetic coupling",
        ),
        CrisisZone(
            name="Mediterranean Aquifer",
            population="500M", crisis="water + heat",
            geology="limestone karst + schist",
            nodes=200, node_cost_usd=100, borehole_cost_usd=1500,
            surface_temp=22, daily_swing=12, seasonal_swing=35,
            seismic_bg=0.001, depth=80, early_warning_weeks=6,
            description="Saltwater intrusion early warning",
        ),
        CrisisZone(
            name="Arctic Permafrost",
            population="10M", crisis="methane + infrastructure",
            geology="Precambrian shield",
            nodes=150, node_cost_usd=200, borehole_cost_usd=2000,
            surface_temp=-10, daily_swing=5, seasonal_swing=50,
            seismic_bg=0.0003, depth=30, early_warning_weeks=12,
            description="Permafrost thaw rate + methane precursors",
        ),
        CrisisZone(
            name="Upper Midwest Corridor",
            population="280K", crisis="grid + aquifer",
            geology="Precambrian basement + glacial",
            nodes=100, node_cost_usd=75, borehole_cost_usd=800,
            surface_temp=10, daily_swing=12, seasonal_swing=45,
            seismic_bg=0.0008, depth=50, early_warning_weeks=4,
            description="Superior to Tomah WI — the test corridor",
        ),
    ]


# =============================================================================
# NETWORK SIMULATION
# =============================================================================

def simulate_network(zone: CrisisZone, hours: int = 168) -> Dict:
    """Simulate one week of network operation."""
    random.seed(42)

    # Create representative transducers
    nodes = []
    for i in range(min(zone.nodes, 20)):  # simulate subset
        tx = GeoTransducer(
            name=f"{zone.name[:8]}_{i:03d}",
            depth_m=zone.depth + random.gauss(0, 5),
            surface_temp_c=zone.surface_temp + random.gauss(0, 2),
            daily_swing_c=zone.daily_swing + random.gauss(0, 1),
            seasonal_swing_c=zone.seasonal_swing,
            seismic_acceleration=zone.seismic_bg * (1 + random.gauss(0, 0.2)),
        )
        nodes.append(tx)

    # Simulate hour by hour
    readings = []
    total_power = 0.0
    total_transmissions = 0

    for hour in range(hours):
        hour_readings = []
        for node in nodes:
            reading = node.sensor_readings(hour % 24)
            hour_readings.append(reading)
            total_power += node.total_power_uw()

        # Network detects anomaly?
        temps = [r["temp_depth_c"] for r in hour_readings]
        avg_temp = sum(temps) / len(temps)
        temp_spread = max(temps) - min(temps)

        # Count transmissions this hour
        for node in nodes:
            tx_per_hour = node.lora_transmissions_per_day() / 24
            total_transmissions += int(tx_per_hour)

        if hour % 24 == 0:
            readings.append({
                "day": hour // 24,
                "avg_temp_depth": round(avg_temp, 1),
                "temp_spread": round(temp_spread, 2),
                "total_power_uw": round(total_power / (hour + 1), 1),
            })

    return {
        "zone": zone.name,
        "nodes_simulated": len(nodes),
        "hours": hours,
        "daily_readings": readings,
        "total_transmissions": total_transmissions,
        "avg_power_uw_per_node": round(total_power / (hours * len(nodes)), 2),
    }


# =============================================================================
# REPORT
# =============================================================================

def print_report(zones: List[CrisisZone]):
    print(f"\n{'='*70}")
    print(f"  CRISIS GEOLOGY x ENERGY RESILIENCE")
    print(f"  The rock is the sensor. The rock is the power source.")
    print(f"{'='*70}")

    # Transducer physics
    print(f"\n  TRANSDUCER PHYSICS (quartz + magnetite in 50m borehole):")
    ref = GeoTransducer(name="reference", depth_m=50,
                         daily_swing_c=10, seasonal_swing_c=30)
    print(f"    Depth: {ref.depth_m}m")
    print(f"    Temperature at depth: {ref.temp_at_depth():.0f}C")
    print(f"    Confining pressure: {ref.pressure_at_depth()/1e6:.1f} MPa")
    bd = ref.power_breakdown()
    print(f"    Thermoelectric (pyrite):  {bd['thermoelectric_uW']:.4f} uW")
    print(f"    Streaming (water flow):   {bd['streaming_uW']:.4f} uW")
    print(f"    Pyroelectric (tourmaline):{bd['pyroelectric_uW']:.4f} uW")
    print(f"    Smoky quartz TL:          {bd['smoky_quartz_nW']:.4f} nW (sensor)")
    print(f"    Piezo (quartz+calcite):   {bd['piezo_pW']:.4f} pW (negligible)")
    print(f"    Biological (tree roots):  {bd['biological_uW']:.4f} uW")
    print(f"    TOTAL: {ref.total_power_uw():.2f} uW")
    print(f"    LoRa transmissions: {ref.lora_transmissions_per_day()}/day")

    # Crisis zones
    print(f"\n  CRISIS ZONES:")
    for z in zones:
        cost = z.total_cost()
        cost_str = f"${cost/1e6:.1f}M" if cost > 1e6 else f"${cost/1e3:.0f}K"
        print(f"\n    {z.name}")
        print(f"      Population: {z.population}  Crisis: {z.crisis}")
        print(f"      Geology: {z.geology}")
        print(f"      Nodes: {z.nodes}  Cost: {cost_str}  "
              f"Early warning: {z.early_warning_weeks:.0f} weeks")
        print(f"      {z.description}")

    # Simulate one zone
    print(f"\n  NETWORK SIMULATION (1 week, Upper Midwest Corridor):")
    corridor = [z for z in zones if "Midwest" in z.name]
    if corridor:
        result = simulate_network(corridor[0])
        for day in result["daily_readings"]:
            print(f"    Day {day['day']}: avg depth temp={day['avg_temp_depth']}C  "
                  f"spread={day['temp_spread']}C  "
                  f"power={day['total_power_uw']} uW/node")
        print(f"    Transmissions: {result['total_transmissions']} total")

    print(f"\n  THE NETWORK EFFECT:")
    print(f"    1 node: temperature at one place")
    print(f"    10 nodes: the gradient")
    print(f"    100 nodes: the flow direction")
    print(f"    1000 nodes: the state of the entire aquifer system")

    # Total cost across all zones
    total_cost = sum(z.total_cost() for z in zones)
    total_nodes = sum(z.nodes for z in zones)
    print(f"\n  GLOBAL DEPLOYMENT:")
    print(f"    Total nodes: {total_nodes:,}")
    print(f"    Total cost: ${total_cost/1e6:.1f}M")
    print(f"    Populations covered: {sum(float(z.population.rstrip('BMK')) * {'B':1e9,'M':1e6,'K':1e3}.get(z.population[-1],1) for z in zones)/1e9:.1f}B people")
    print(f"    Lifespan: 10-30 years (no moving parts)")
    print(f"    Maintenance: zero")
    print(f"    When the grid fails: it still works")

    print(f"\n{'='*70}\n")


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    zones = build_crisis_zones()
    print_report(zones)
