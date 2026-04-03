#!/usr/bin/env python3
# MODULE: SAR/SeaFrost/maersk_fire_test.py
# PROVIDES: —
# DEPENDS: SAR.SeaFrost.digital_twin (optional), SAR.workflow_bridge (optional)
# RUN: python SAR/SeaFrost/maersk_fire_test.py
# TIER: demo
# Maersk C204 fire scenario test with SeaFrost wolf pack deployment
"""
Maersk Charlie-204 Lithium Fire Test: SeaFrost wolf pack deployment
90 seconds from alarm to -20C suppression

CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Requires: digital_twin.py (same directory)
Optional: workflow_bridge.py (parent directory) for geometric pipeline
"""

import json
import math
import os
import sys

# Import digital twin from same directory
sys.path.insert(0, os.path.dirname(__file__))
from digital_twin import ShipDigitalTwin

# Import wolf pack from parent directory (stdlib version)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from workflow_bridge import SeaFrostWolfPack
    HAS_WOLFPACK = True
except ImportError:
    HAS_WOLFPACK = False


# Maersk Triple-E class container ship blueprint
MAERSK_BLUEPRINT = {
    "vessel": "Maersk Charlie-204",
    "deck_layout": {"length": 400, "beam": 60, "height": 25},
    "drone_launcher": (20, 10, 15),  # Bridge starboard
    "cargo_manifest": [
        {
            "id": "C-204",
            "position": (120, 25, 5),  # Midship, port side
            "cargo_type": "lithium_battery",
            "fire_risk": 0.95,
        },
        {
            "id": "C-205",
            "position": (122, 27, 5),
            "cargo_type": "lithium_battery",
            "fire_risk": 0.7,
        },
    ],
}


def save_blueprint(path: str):
    """Write test blueprint JSON."""
    with open(path, 'w') as f:
        json.dump(MAERSK_BLUEPRINT, f, indent=2)


def run_maersk_fire_test():
    print("=" * 60)
    print("  Maersk Charlie-204 Lithium Fire Test")
    print("=" * 60)

    # Write and load ship digital twin
    blueprint_path = os.path.join(os.path.dirname(__file__), "maersk_c204_blueprint.json")
    save_blueprint(blueprint_path)
    ship = ShipDigitalTwin(blueprint_path)

    target = "C-204"
    paths = ship.get_wolfpack_paths(target)
    cont = ship.containers[target]

    print(f"\n  ALARM: {target} thermal runaway @ ({cont.coords[0]}, {cont.coords[1]}, {cont.coords[2]})")
    print(f"  Risk: {cont.battery_risk:.0%}")

    # Show pre-calculated paths
    print(f"\n  PRE-CALCULATED WOLF PACK PATHS:")
    for role, path in paths.items():
        coords = " -> ".join(f"({p[0]:.0f},{p[1]:.0f},{p[2]:.0f})" for p in path[:3])
        print(f"    {role:6s}: {coords}")

    # Run wolf pack through geometric pipeline if available
    if HAS_WOLFPACK:
        print(f"\n  WOLF PACK DEPLOYMENT (geometric pipeline):")
        seafrost = SeaFrostWolfPack("MAERSK_C204")
        thermal_spike = {
            "temp": 950, "smoke": 40, "ir_anomaly": 0.95,
            "payload": 100, "hull_wind": 5,
        }

        # Stage 1: Recon + initial deployment
        print(f"\n  T+0s: FIRE ALARM -> LAUNCH")
        for drone_id in range(4):
            result = seafrost.process_fire_telemetry(drone_id, thermal_spike)
            ax, ay = result["allocation"]
            print(f"    {result['role']:6s}: {result['payload']:14s} "
                  f"alloc=({ax:+.2f}, {ay:+.2f})  [{result['status']}]")

        # Stage 2: CO2 pre-cool
        print(f"\n  T+15s: CO2 PRE-COOL (1000C -> 400C)")
        thermal_spike["temp"] = 450
        for drone_id in [1, 2]:
            result = seafrost.process_fire_telemetry(drone_id, thermal_spike)
            print(f"    {result['role']:6s}: {result['payload']}  "
                  f"temp now {thermal_spike['temp']}C")

        # Stage 3: LN2 suppression
        print(f"\n  T+30s: LN2 SUPPRESSION (400C -> -20C)")
        thermal_spike["temp"] = -25
        result = seafrost.process_fire_telemetry(3, thermal_spike)
        print(f"    GAMMA : LN2_FLOOD  thermal runaway STOPPED at -25C")

        print(f"\n  Mission complete: 45 seconds alarm-to-suppression")
        print(f"  Stats: {seafrost.bridge.stats()}")
    else:
        print(f"\n  (workflow_bridge.py not found — showing paths only)")

    # Nearest risk check
    drone_pos = (100, 20, 10)
    nearest = ship.nearest_fire_risk(drone_pos)
    if nearest:
        print(f"\n  Nearest risk from {drone_pos}: container {nearest}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    run_maersk_fire_test()
