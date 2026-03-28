#!/usr/bin/env python3
"""
Resilience — Entry Point
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Start here. This shows everything available and lets you run it.

    python run.py

No dependencies. No pip. No internet (except Living Intelligence fetch).
"""

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

MODULES = {
    # --- Core simulation ---
    "1": {
        "name": "City Resilience Simulation",
        "cmd": [sys.executable, "-m", "sim.run"],
        "desc": "Madison WI grid failure scenario. Zone-by-zone survival windows.",
    },
    "2": {
        "name": "Coupled Domain Cascade",
        "cmd": [sys.executable, "-m", "sim.cities.coupling"],
        "desc": "Cross-domain shock propagation. Knowledge decay countdown clocks.",
    },

    # --- Seed protocol + mesh ---
    "3": {
        "name": "Seed Protocol (mesh networking)",
        "cmd": [sys.executable, "-m", "sim.seed_protocol"],
        "desc": "Octahedral seed encoding, 21-byte packets, mesh convergence. Stdlib only.",
    },
    "4": {
        "name": "Seed Mesh (grid failure bridge)",
        "cmd": [sys.executable, "-m", "sim.seed_mesh"],
        "desc": "Mesh network activation during 72-hour grid failure. Cascade mitigation.",
    },

    # --- SAR / Rescue ---
    "5": {
        "name": "SAR Workflow Bridge (drone swarm)",
        "cmd": [sys.executable, os.path.join("SAR", "workflow_bridge.py")],
        "desc": "50-drone blizzard SAR + SeaFrost wolf pack. Per-drone state, 3D altitude, waypoint export.",
    },
    "6": {
        "name": "Rescue (GPS-denied search)",
        "cmd": [sys.executable, "-m", "Rescue.rescue"],
        "desc": "Lost person modeling, low-signal navigation, thermal search patterns.",
    },
    "7": {
        "name": "Energy-Efficient AI",
        "cmd": [sys.executable, "-m", "Rescue.energy_efficient_ai"],
        "desc": "Constrained agents don't fail — they grow differently. Rosetta principle.",
    },

    # --- Knowledge DNA ---
    "8": {
        "name": "Knowledge DNA (ancestry + field propagation)",
        "cmd": [sys.executable, "-m", "KnowledgeDNA.knowledge_dna"],
        "desc": "Channel coupling, dormancy decay, typed edges. Knowledge as physics.",
    },
    "9": {
        "name": "Equation Field Overlap",
        "cmd": [sys.executable, "-m", "KnowledgeDNA.equation_field"],
        "desc": "14 equations x 15 domains. Multi-purpose reuse. Phi at 7x efficiency.",
    },
    "10": {
        "name": "Substrate Reasoner",
        "cmd": [sys.executable, "-m", "KnowledgeDNA.substrate"],
        "desc": "Physics up, not domains sideways. Vector synthesis from corpus.",
    },
    "11": {
        "name": "GEIS Bridge (geometric encoding)",
        "cmd": [sys.executable, "-m", "KnowledgeDNA.geobin_bridge"],
        "desc": "Octahedral vertex bits to substrate properties. Derived mappings.",
    },
    "12": {
        "name": "Living Intelligence (the teachers)",
        "cmd": [sys.executable, "-m", "KnowledgeDNA.living_intelligence"],
        "desc": "38 living intelligences from GitHub. Bee, mycelium, quartz, decay.",
    },

    # --- Crisis Geology ---
    "14": {
        "name": "Crisis Geology (geothermal transduction)",
        "cmd": [sys.executable, "-m", "sim.crisis_geology"],
        "desc": "Borehole transducers: 6 mineral coupling paths. The rock is the sensor.",
    },
    "15": {
        "name": "Urban Grid (infrastructure retrofit)",
        "cmd": [sys.executable, "-m", "sim.urban_grid"],
        "desc": "Water pipes, basements, garages as transducer network. Data > power.",
    },
    "16": {
        "name": "Crisis Topology (interface problems)",
        "cmd": [sys.executable, "-m", "sim.crisis_topology"],
        "desc": "8 crisis interfaces, leverage ranking, corridor deployment plan.",
    },

    # --- GoatHerd ---
    "13": {
        "name": "GoatHerd (village herding assistant)",
        "cmd": [sys.executable, os.path.join("GoatHerd", "herd.py")],
        "desc": "Grazing rotation, health tracking, market timing. For a kid in Sri Lanka.",
    },
}


def main():
    print(f"\n{'='*60}")
    print(f"  RESILIENCE — simulation framework for systemic resilience")
    print(f"  CC0 public domain. No dependencies. Free.")
    print(f"{'='*60}")
    print(f"\n  Modules available:\n")

    sections = [
        ("Core Simulation", ["1", "2"]),
        ("Mesh Networking", ["3", "4"]),
        ("Search and Rescue", ["5", "6", "7"]),
        ("Knowledge + Reasoning", ["8", "9", "10", "11", "12"]),
        ("Crisis Geology", ["14", "15", "16"]),
        ("Field Tools", ["13"]),
    ]

    for section_name, keys in sections:
        print(f"  {section_name}:")
        for key in keys:
            mod = MODULES[key]
            print(f"    [{key:>2s}] {mod['name']}")
            print(f"         {mod['desc']}")
        print()

    print(f"  [q]  Quit")
    print(f"  [a]  Run all demos (non-interactive)")
    print()

    while True:
        try:
            choice = input("  Choose module (1-14, a, q):").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "q":
            break
        elif choice == "a":
            print(f"\n  Running all demos...\n")
            for key in sorted(MODULES.keys(), key=int):
                mod = MODULES[key]
                print(f"\n{'─'*60}")
                print(f"  [{key}] {mod['name']}")
                print(f"{'─'*60}")
                try:
                    subprocess.run(
                        mod["cmd"], cwd=ROOT,
                        timeout=30,
                        input=b"",  # no interactive input
                    )
                except subprocess.TimeoutExpired:
                    print(f"  (timed out after 30s)")
                except Exception as e:
                    print(f"  Error: {e}")
            print(f"\n  All demos complete.")
            break
        elif choice in MODULES:
            mod = MODULES[choice]
            print(f"\n  Running: {mod['name']}...\n")
            try:
                subprocess.run(mod["cmd"], cwd=ROOT)
            except KeyboardInterrupt:
                print(f"\n  Stopped.")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  Unknown choice. Enter 1-13, a, or q.")


if __name__ == "__main__":
    main()
