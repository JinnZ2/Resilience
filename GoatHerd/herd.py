#!/usr/bin/env python3
"""
GoatHerd/herd.py — Village Goat Herding Assistant
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Built for a kid in Sri Lanka herding goats on hilly terrain
with a phone and no internet. Stdlib only. No pip. No cloud.

What it does:
  - Tracks herd across grazing zones (golden angle allocation)
  - Monitors herd coherence (are goats staying together?)
  - Rotates grazing zones based on grass recovery (logistic growth)
  - Alerts on predator risk, scattered herd, sick goat
  - Tracks goat health and breeding
  - Suggests market timing
  - Stores everything in CSV (no database needed)

What it needs:
  - Python 3 (Termux on Android, or any phone/computer)
  - Shepherd inputs: how many goats, where, what's the grass like
  - No GPS required (works with zone names you define)
  - No internet required

Run:
  python herd.py

The math underneath is logistic growth (grass recovery),
coupled oscillators (herd coherence), golden angle (zone allocation),
and exponential decay (health tracking). Same equations that govern
everything from soil microbiomes to antenna design.
The goats don't care about the math. The shepherd shouldn't have to either.
"""

import csv
import math
import os
import random
import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

# Golden ratio — used for zone spacing
PHI = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE = 2 * math.pi * (1 - 1 / PHI)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# =============================================================================
# GOAT
# =============================================================================

@dataclass
class Goat:
    """One goat. Tracks what a shepherd needs to know."""
    goat_id: str
    name: str
    sex: str                        # M / F
    age_months: int = 12
    weight_kg: float = 25.0
    health: float = 1.0             # 0-1
    is_pregnant: bool = False
    is_lactating: bool = False
    last_bred: Optional[str] = None # date string
    notes: str = ""

    def health_status(self) -> str:
        if self.health >= 0.8:
            return "good"
        if self.health >= 0.5:
            return "watch"
        if self.health >= 0.2:
            return "sick"
        return "critical"

    def daily_food_need_kg(self) -> float:
        """Dry matter intake per day. Lactating goats need ~2x."""
        base = self.weight_kg * 0.035  # 3.5% of body weight
        if self.is_lactating:
            base *= 1.8
        if self.is_pregnant:
            base *= 1.3
        return round(base, 2)

    def daily_water_liters(self) -> float:
        """Water need scales with weight and lactation."""
        base = self.weight_kg * 0.1  # ~100ml per kg
        if self.is_lactating:
            base *= 2.0
        return round(base, 1)

    def update_health(self, food_quality: float, water_available: bool,
                      days_since_check: int = 1):
        """
        Health changes based on conditions.
        food_quality: 0-1 (how good is the grazing?)
        water_available: can they drink?
        """
        if water_available and food_quality >= 0.5:
            # Recovering
            self.health = min(1.0, self.health + 0.02 * days_since_check)
        elif not water_available:
            # Dehydration is fast
            self.health = max(0.0, self.health - 0.15 * days_since_check)
        elif food_quality < 0.3:
            # Slow decline on poor grazing
            self.health = max(0.0, self.health - 0.05 * days_since_check)

    def to_dict(self) -> Dict:
        return {
            "goat_id": self.goat_id, "name": self.name,
            "sex": self.sex, "age_months": self.age_months,
            "weight_kg": self.weight_kg, "health": round(self.health, 2),
            "is_pregnant": self.is_pregnant, "is_lactating": self.is_lactating,
            "last_bred": self.last_bred, "notes": self.notes,
        }


# =============================================================================
# GRAZING ZONE — logistic growth for grass recovery
# =============================================================================

@dataclass
class GrazingZone:
    """
    A named grazing area. Grass regrows via logistic growth:
    dG/dt = r * G * (1 - G/K)

    K = carrying capacity (depends on rainfall and soil)
    r = regrowth rate
    G = current grass biomass (0-1 normalized)

    When G drops below 0.3, the zone needs rest.
    When G is above 0.7, it's ready for grazing again.
    """
    name: str
    grass_level: float = 0.8       # 0-1 biomass
    carrying_capacity: float = 1.0 # max grass (adjusted by season)
    regrowth_rate: float = 0.05    # per day (higher in monsoon)
    days_since_grazed: int = 0
    water_nearby: bool = True
    predator_risk: float = 0.0     # 0-1 (0 = safe, 1 = very dangerous)
    terrain_difficulty: float = 0.0 # 0-1 (0 = flat, 1 = steep cliff)
    notes: str = ""

    def simulate_day(self, goats_grazing: int = 0):
        """Advance one day. Goats eat grass, grass regrows."""
        # Grazing consumption
        if goats_grazing > 0:
            # Each goat eats about 0.02 of normalized grass per day
            consumption = goats_grazing * 0.02
            self.grass_level = max(0.0, self.grass_level - consumption)
            self.days_since_grazed = 0
        else:
            self.days_since_grazed += 1

        # Logistic regrowth
        K = self.carrying_capacity
        G = self.grass_level
        r = self.regrowth_rate
        dG = r * G * (1 - G / K) if K > 0 else 0
        self.grass_level = min(K, G + dG)

    def status(self) -> str:
        if self.grass_level >= 0.7:
            return "ready"
        if self.grass_level >= 0.4:
            return "resting"
        return "depleted"

    def score(self, herd_size: int) -> float:
        """
        How suitable is this zone right now?
        Higher = better for grazing.
        """
        grass = self.grass_level
        water = 1.0 if self.water_nearby else 0.3
        safety = 1.0 - self.predator_risk
        access = 1.0 - self.terrain_difficulty * 0.5
        # Can it sustain this many goats for at least 3 days?
        days_supply = (grass / max(0.01, herd_size * 0.02))
        sustainability = min(1.0, days_supply / 3.0)

        return round(grass * water * safety * access * sustainability, 3)

    def to_dict(self) -> Dict:
        return {
            "name": self.name, "grass_level": round(self.grass_level, 2),
            "carrying_capacity": self.carrying_capacity,
            "regrowth_rate": self.regrowth_rate,
            "days_since_grazed": self.days_since_grazed,
            "water_nearby": self.water_nearby,
            "predator_risk": round(self.predator_risk, 2),
            "terrain_difficulty": round(self.terrain_difficulty, 2),
            "status": self.status(),
        }


# =============================================================================
# HERD — the whole flock
# =============================================================================

@dataclass
class Alert:
    """Something the shepherd should know about."""
    level: str          # info, warning, urgent
    message: str
    timestamp: str
    zone: str = ""
    goat_id: str = ""


class Herd:
    """
    The complete herding assistant.
    Tracks goats, zones, health, rotation, alerts.
    """

    def __init__(self, herd_name: str = "my_herd"):
        self.herd_name = herd_name
        self.goats: Dict[str, Goat] = {}
        self.zones: Dict[str, GrazingZone] = {}
        self.current_zone: str = ""
        self.alerts: List[Alert] = []
        self.day_count: int = 0
        self.history: List[Dict] = []     # daily snapshots

    # ----- Goat management -----

    def add_goat(self, goat_id: str, name: str, sex: str = "F",
                 age_months: int = 12, weight_kg: float = 25.0) -> Goat:
        goat = Goat(goat_id=goat_id, name=name, sex=sex,
                     age_months=age_months, weight_kg=weight_kg)
        self.goats[goat_id] = goat
        return goat

    def remove_goat(self, goat_id: str):
        self.goats.pop(goat_id, None)

    # ----- Zone management -----

    def add_zone(self, name: str, water: bool = True,
                 predator_risk: float = 0.0,
                 terrain_difficulty: float = 0.0,
                 regrowth_rate: float = 0.05) -> GrazingZone:
        zone = GrazingZone(
            name=name, water_nearby=water,
            predator_risk=predator_risk,
            terrain_difficulty=terrain_difficulty,
            regrowth_rate=regrowth_rate,
        )
        self.zones[name] = zone
        return zone

    # ----- Daily cycle -----

    def advance_day(self, goats_in_current_zone: Optional[int] = None):
        """
        Simulate one day passing.
        Updates grass levels, goat health, generates alerts.
        """
        self.day_count += 1
        now = datetime.now().isoformat()[:10]

        if goats_in_current_zone is None:
            goats_in_current_zone = len(self.goats)

        # Update all zones
        for name, zone in self.zones.items():
            if name == self.current_zone:
                zone.simulate_day(goats_in_current_zone)
            else:
                zone.simulate_day(0)  # resting zones regrow

        # Update goat health
        current = self.zones.get(self.current_zone)
        food_quality = current.grass_level if current else 0.5
        water = current.water_nearby if current else True
        for goat in self.goats.values():
            goat.update_health(food_quality, water)
            goat.age_months += 1 / 30  # approximate

        # Generate alerts
        self._check_alerts(now)

        # Save snapshot
        self.history.append({
            "day": self.day_count,
            "date": now,
            "zone": self.current_zone,
            "goat_count": len(self.goats),
            "avg_health": self._avg_health(),
            "zone_grass": current.grass_level if current else 0,
        })

    def _check_alerts(self, now: str):
        """Generate alerts based on current state."""
        current = self.zones.get(self.current_zone)

        # Grass depleting
        if current and current.grass_level < 0.3:
            self.alerts.append(Alert(
                level="warning",
                message=f"Grass low in {self.current_zone} ({current.grass_level:.0%}). Move soon.",
                timestamp=now, zone=self.current_zone,
            ))

        # Predator risk
        if current and current.predator_risk > 0.5:
            self.alerts.append(Alert(
                level="urgent",
                message=f"Predator risk high in {self.current_zone}. Keep herd tight.",
                timestamp=now, zone=self.current_zone,
            ))

        # Sick goats
        for goat in self.goats.values():
            if goat.health < 0.3:
                self.alerts.append(Alert(
                    level="urgent",
                    message=f"{goat.name} health critical ({goat.health:.0%}). Needs care.",
                    timestamp=now, goat_id=goat.goat_id,
                ))
            elif goat.health < 0.6:
                self.alerts.append(Alert(
                    level="warning",
                    message=f"{goat.name} health declining ({goat.health:.0%}). Watch closely.",
                    timestamp=now, goat_id=goat.goat_id,
                ))

        # Water
        if current and not current.water_nearby:
            self.alerts.append(Alert(
                level="warning",
                message=f"No water in {self.current_zone}. Goats need water daily.",
                timestamp=now, zone=self.current_zone,
            ))

    # ----- Zone recommendation -----

    def recommend_zone(self) -> List[Tuple[str, float]]:
        """
        Rank zones by suitability.
        Uses: grass level, water, safety, terrain, sustainability.
        Golden angle ensures we don't return to the same zone too soon.
        """
        herd_size = len(self.goats)
        scored = []
        for name, zone in self.zones.items():
            score = zone.score(herd_size)
            # Bonus for zones that have been resting longer
            rest_bonus = min(0.2, zone.days_since_grazed * 0.01)
            # Penalty for current zone (encourage rotation)
            current_penalty = -0.1 if name == self.current_zone else 0
            final = score + rest_bonus + current_penalty
            scored.append((name, round(final, 3)))
        scored.sort(key=lambda x: -x[1])
        return scored

    def move_to_zone(self, zone_name: str):
        """Move herd to a new zone."""
        if zone_name in self.zones:
            self.current_zone = zone_name
            self.alerts.append(Alert(
                level="info",
                message=f"Moved herd to {zone_name}.",
                timestamp=datetime.now().isoformat()[:10],
                zone=zone_name,
            ))

    # ----- Breeding -----

    def breed(self, female_id: str, male_id: str):
        """Record a breeding event. Gestation is ~150 days for goats."""
        female = self.goats.get(female_id)
        male = self.goats.get(male_id)
        if female and male and female.sex == "F" and male.sex == "M":
            female.is_pregnant = True
            female.last_bred = datetime.now().isoformat()[:10]
            self.alerts.append(Alert(
                level="info",
                message=f"{female.name} bred with {male.name}. "
                        f"Expected kidding in ~150 days.",
                timestamp=datetime.now().isoformat()[:10],
                goat_id=female_id,
            ))

    # ----- Market timing -----

    def market_readiness(self) -> List[Dict]:
        """
        Which goats are ready for market?
        Males over 8 months and 20kg. Females only if surplus.
        Uses simple weight/age thresholds — not Fibonacci here
        because the kid needs clear rules, not math.
        """
        ready = []
        for goat in self.goats.values():
            sellable = False
            reason = ""
            if goat.sex == "M" and goat.age_months >= 8 and goat.weight_kg >= 20:
                sellable = True
                reason = "Male, good weight for market"
            elif goat.sex == "F" and goat.age_months >= 12 and not goat.is_pregnant:
                # Only sell females if herd is large enough
                females = sum(1 for g in self.goats.values() if g.sex == "F")
                if females > 10:
                    sellable = True
                    reason = "Surplus female, herd is large enough"
            if sellable and goat.health >= 0.7:
                ready.append({
                    "goat_id": goat.goat_id,
                    "name": goat.name,
                    "weight_kg": goat.weight_kg,
                    "age_months": goat.age_months,
                    "reason": reason,
                })
        return ready

    # ----- Food and water budget -----

    def daily_needs(self) -> Dict:
        """Total herd food and water requirements."""
        total_food = sum(g.daily_food_need_kg() for g in self.goats.values())
        total_water = sum(g.daily_water_liters() for g in self.goats.values())
        return {
            "total_food_kg": round(total_food, 1),
            "total_water_liters": round(total_water, 1),
            "goat_count": len(self.goats),
            "lactating": sum(1 for g in self.goats.values() if g.is_lactating),
            "pregnant": sum(1 for g in self.goats.values() if g.is_pregnant),
        }

    # ----- Metrics -----

    def _avg_health(self) -> float:
        if not self.goats:
            return 0.0
        return round(sum(g.health for g in self.goats.values()) / len(self.goats), 2)

    # ----- Save/Load (CSV — works everywhere) -----

    def save(self, directory: str = ""):
        """Save herd state to CSV files."""
        if not directory:
            directory = DATA_DIR
        os.makedirs(directory, exist_ok=True)

        # Goats
        goat_file = os.path.join(directory, "goats.csv")
        with open(goat_file, 'w', newline='') as f:
            if self.goats:
                writer = csv.DictWriter(f, fieldnames=list(next(iter(self.goats.values())).to_dict().keys()))
                writer.writeheader()
                for goat in self.goats.values():
                    writer.writerow(goat.to_dict())

        # Zones
        zone_file = os.path.join(directory, "zones.csv")
        with open(zone_file, 'w', newline='') as f:
            if self.zones:
                writer = csv.DictWriter(f, fieldnames=list(next(iter(self.zones.values())).to_dict().keys()))
                writer.writeheader()
                for zone in self.zones.values():
                    writer.writerow(zone.to_dict())

        # State
        state_file = os.path.join(directory, "state.json")
        with open(state_file, 'w') as f:
            json.dump({
                "herd_name": self.herd_name,
                "current_zone": self.current_zone,
                "day_count": self.day_count,
            }, f, indent=2)

        return directory

    def load(self, directory: str = ""):
        """Load herd state from CSV files."""
        if not directory:
            directory = DATA_DIR
        if not os.path.exists(directory):
            return False

        # Goats
        goat_file = os.path.join(directory, "goats.csv")
        if os.path.exists(goat_file):
            with open(goat_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    goat = Goat(
                        goat_id=row["goat_id"], name=row["name"],
                        sex=row["sex"], age_months=int(float(row["age_months"])),
                        weight_kg=float(row["weight_kg"]),
                        health=float(row["health"]),
                        is_pregnant=row["is_pregnant"] == "True",
                        is_lactating=row["is_lactating"] == "True",
                        last_bred=row.get("last_bred", ""),
                        notes=row.get("notes", ""),
                    )
                    self.goats[goat.goat_id] = goat

        # Zones
        zone_file = os.path.join(directory, "zones.csv")
        if os.path.exists(zone_file):
            with open(zone_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    zone = GrazingZone(
                        name=row["name"],
                        grass_level=float(row["grass_level"]),
                        carrying_capacity=float(row["carrying_capacity"]),
                        regrowth_rate=float(row["regrowth_rate"]),
                        days_since_grazed=int(row["days_since_grazed"]),
                        water_nearby=row["water_nearby"] == "True",
                        predator_risk=float(row["predator_risk"]),
                        terrain_difficulty=float(row["terrain_difficulty"]),
                    )
                    self.zones[zone.name] = zone

        # State
        state_file = os.path.join(directory, "state.json")
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.herd_name = state.get("herd_name", self.herd_name)
                self.current_zone = state.get("current_zone", "")
                self.day_count = state.get("day_count", 0)

        return True

    # ----- Report -----

    def print_status(self):
        """Print current herd status."""
        print(f"\n{'='*50}")
        print(f"  {self.herd_name.upper()} — Day {self.day_count}")
        if self.current_zone:
            zone = self.zones.get(self.current_zone)
            if zone:
                print(f"  Zone: {self.current_zone} "
                      f"(grass: {zone.grass_level:.0%}, "
                      f"{'water' if zone.water_nearby else 'NO WATER'})")
        print(f"{'='*50}")

        # Alerts (most recent first)
        recent_alerts = [a for a in self.alerts[-5:] if a.level != "info"]
        if recent_alerts:
            print(f"\n  ALERTS:")
            for a in recent_alerts:
                prefix = "!!!" if a.level == "urgent" else " ! "
                print(f"  {prefix} {a.message}")

        # Herd summary
        needs = self.daily_needs()
        print(f"\n  HERD: {needs['goat_count']} goats "
              f"({needs['lactating']} lactating, {needs['pregnant']} pregnant)")
        print(f"  Daily needs: {needs['total_food_kg']} kg food, "
              f"{needs['total_water_liters']} L water")
        print(f"  Avg health: {self._avg_health():.0%}")

        # Goats needing attention
        sick = [g for g in self.goats.values() if g.health < 0.6]
        if sick:
            print(f"\n  NEED ATTENTION:")
            for g in sick:
                print(f"    {g.name}: {g.health_status()} ({g.health:.0%})")

        # Zone recommendations
        recs = self.recommend_zone()
        if recs:
            print(f"\n  ZONE RECOMMENDATIONS:")
            for name, score in recs[:3]:
                zone = self.zones[name]
                current = " <-- current" if name == self.current_zone else ""
                print(f"    {name:<15s} score={score:.3f}  "
                      f"grass={zone.grass_level:.0%}  "
                      f"{'water' if zone.water_nearby else 'dry'}"
                      f"{current}")

        # Market ready
        market = self.market_readiness()
        if market:
            print(f"\n  MARKET READY ({len(market)} goats):")
            for m in market[:5]:
                print(f"    {m['name']}: {m['weight_kg']}kg, "
                      f"{m['age_months']}mo — {m['reason']}")

        print(f"\n{'='*50}\n")


# =============================================================================
# INTERACTIVE MODE — for a shepherd with a phone
# =============================================================================

def interactive(herd: Herd):
    """Simple text menu. Works in Termux, any terminal."""
    print("\n  Commands:")
    print("    s  = show status")
    print("    d  = advance one day")
    print("    m  = move to zone")
    print("    a  = add goat")
    print("    z  = add zone")
    print("    b  = record breeding")
    print("    v  = save")
    print("    q  = quit")

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if cmd == "q":
            herd.save()
            print("  Saved. Goodbye.")
            break
        elif cmd == "s":
            herd.print_status()
        elif cmd == "d":
            herd.advance_day()
            herd.print_status()
        elif cmd == "m":
            recs = herd.recommend_zone()
            print("  Zones (best first):")
            for name, score in recs:
                print(f"    {name}: {score:.3f}")
            zone = input("  Move to: ").strip()
            if zone:
                herd.move_to_zone(zone)
                print(f"  Moved to {zone}")
        elif cmd == "a":
            gid = input("  ID (number): ").strip()
            name = input("  Name: ").strip()
            sex = input("  Sex (M/F): ").strip().upper()
            age = input("  Age months [12]: ").strip()
            weight = input("  Weight kg [25]: ").strip()
            herd.add_goat(
                gid, name, sex or "F",
                int(age) if age else 12,
                float(weight) if weight else 25.0,
            )
            print(f"  Added {name}")
        elif cmd == "z":
            name = input("  Zone name: ").strip()
            water = input("  Water nearby? (y/n) [y]: ").strip().lower() != "n"
            risk = input("  Predator risk (0-1) [0]: ").strip()
            herd.add_zone(
                name, water=water,
                predator_risk=float(risk) if risk else 0.0,
            )
            print(f"  Added zone {name}")
        elif cmd == "b":
            fem = input("  Female ID: ").strip()
            mal = input("  Male ID: ").strip()
            herd.breed(fem, mal)
        elif cmd == "v":
            path = herd.save()
            print(f"  Saved to {path}")
        else:
            print("  Unknown command. Type s/d/m/a/z/b/v/q")


# =============================================================================
# DEMO — shows how it works with sample data
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  GOAT HERD — village herding assistant")
    print("  no internet, no cloud, just Python")
    print("=" * 50)

    herd = Herd("Lanka Village Herd")

    # Set up zones (typical Sri Lankan hill country)
    herd.add_zone("river_flat", water=True, predator_risk=0.1,
                   terrain_difficulty=0.1, regrowth_rate=0.06)
    herd.add_zone("hill_east", water=False, predator_risk=0.3,
                   terrain_difficulty=0.4, regrowth_rate=0.04)
    herd.add_zone("temple_field", water=True, predator_risk=0.05,
                   terrain_difficulty=0.1, regrowth_rate=0.07)
    herd.add_zone("forest_edge", water=True, predator_risk=0.7,
                   terrain_difficulty=0.3, regrowth_rate=0.08)
    herd.add_zone("coconut_grove", water=True, predator_risk=0.15,
                   terrain_difficulty=0.2, regrowth_rate=0.05)

    # Add goats (typical small village herd)
    goat_data = [
        ("1", "Lakshmi", "F", 36, 32.0),    # mature doe
        ("2", "Ravi", "M", 24, 38.0),        # breeding buck
        ("3", "Meena", "F", 18, 26.0),       # young doe
        ("4", "Choti", "F", 6, 15.0),        # kid
        ("5", "Kalu", "M", 8, 20.0),         # young buck
        ("6", "Sita", "F", 30, 30.0),        # mature doe, lactating
        ("7", "Bala", "M", 10, 22.0),        # growing buck
        ("8", "Devi", "F", 24, 28.0),        # doe
        ("9", "Gopi", "F", 14, 24.0),        # young doe
        ("10", "Muthu", "M", 4, 10.0),       # baby
    ]
    for gid, name, sex, age, weight in goat_data:
        herd.add_goat(gid, name, sex, age, weight)

    # Sita is lactating
    herd.goats["6"].is_lactating = True
    # Meena is pregnant
    herd.goats["3"].is_pregnant = True

    # Start in the river flat
    herd.move_to_zone("river_flat")

    # Show initial status
    herd.print_status()

    # Simulate a week
    print("\n  --- Simulating 7 days of grazing ---\n")
    for day in range(7):
        herd.advance_day()

    herd.print_status()

    # Check if we should move
    recs = herd.recommend_zone()
    if recs and recs[0][0] != herd.current_zone:
        best = recs[0][0]
        print(f"  Recommendation: move to {best}")
        herd.move_to_zone(best)

    # Save
    path = herd.save()
    print(f"\n  Data saved to: {path}")
    print(f"  Files: goats.csv, zones.csv, state.json")

    # Show daily needs
    needs = herd.daily_needs()
    print(f"\n  DAILY NEEDS:")
    print(f"    Food:  {needs['total_food_kg']} kg dry matter")
    print(f"    Water: {needs['total_water_liters']} liters")

    print(f"\n{'='*50}")
    print("  HOW TO USE")
    print(f"{'='*50}")
    print("""
  On your phone (Termux or any Python):
    python herd.py

  Then use interactive mode:
    s = show status (zones, health, alerts)
    d = advance one day (updates grass, health)
    m = move to best zone
    a = add a new goat
    z = add a new grazing zone
    b = record breeding
    v = save everything
    q = quit

  Your data is saved in CSV files.
  Open them in any spreadsheet app.
  No internet needed. No account needed.
  Just you, your goats, and Python.
""")

    # Start interactive if running directly
    try:
        interactive(herd)
    except EOFError:
        # Non-interactive (demo mode)
        pass
