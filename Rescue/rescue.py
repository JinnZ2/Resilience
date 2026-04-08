#!/usr/bin/env python3
# MODULE: Rescue/rescue.py
# PROVIDES: RESCUE.PROTOCOL, RESCUE.RESOURCE_ALLOCATION
# DEPENDS: stdlib-only
# RUN: python -m Rescue.rescue
# TIER: bridge
# Drone rescue operations in GPS-denied environments
"""
Rescue/rescue.py — Drone Rescue Operations (Non-Lithium Fire)
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Person rescue in GPS-denied environments: mountains, deep woods,
canyons. Low-signal navigation, lost person behavior modeling,
thermal search patterns, and comms relay.

Stdlib only. Runs on a phone.

USAGE:
    python -m Rescue.rescue
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# =============================================================================
# TERRAIN + SIGNAL MODEL
# =============================================================================

@dataclass
class TerrainCell:
    """One grid cell of the search area."""
    x: int
    y: int
    elevation_m: float = 0.0
    tree_cover: float = 0.0        # 0-1 (0=open, 1=dense forest)
    water: bool = False            # stream/river
    shelter: bool = False          # cave, overhang, structure
    slope: float = 0.0             # degrees
    signal_strength: float = 1.0   # 0-1 (derived from terrain)

    def compute_signal(self, tx_elevation: float = 100.0):
        """
        Signal strength degrades with:
        - Tree cover (foliage absorbs radio)
        - Canyon depth (elevation below transmitter)
        - Slope (multipath reflection)
        """
        # Elevation shadow: deeper = weaker signal
        elev_factor = min(1.0, 0.3 + 0.7 * (self.elevation_m / max(tx_elevation, 1)))
        # Foliage absorption: dense trees kill signal
        tree_factor = 1.0 - (self.tree_cover * 0.7)
        # Slope causes multipath
        slope_factor = 1.0 - (min(self.slope, 45) / 90.0) * 0.3
        self.signal_strength = round(elev_factor * tree_factor * slope_factor, 3)
        return self.signal_strength


@dataclass
class SearchArea:
    """Grid-based terrain map for search operations."""
    width: int
    height: int
    cell_size_m: float = 50.0      # meters per grid cell
    cells: Dict[Tuple[int, int], TerrainCell] = field(default_factory=dict)
    last_known_position: Tuple[int, int] = (0, 0)

    def build_terrain(self, terrain_type: str = "mountain"):
        """Generate realistic terrain. Supports mountain, forest, canyon."""
        for x in range(self.width):
            for y in range(self.height):
                cell = TerrainCell(x=x, y=y)

                if terrain_type == "mountain":
                    # Elevation rises toward center with ridges
                    cx, cy = self.width / 2, self.height / 2
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    cell.elevation_m = max(0, 500 - dist * 20 + random.gauss(0, 30))
                    cell.slope = min(60, abs(random.gauss(15, 10)))
                    cell.tree_cover = max(0, min(1, 0.6 - cell.elevation_m / 800))
                    cell.water = (y == self.height // 3) and (x > 2)  # stream
                    cell.shelter = random.random() < 0.03

                elif terrain_type == "forest":
                    cell.elevation_m = random.gauss(200, 20)
                    cell.tree_cover = max(0.3, min(1.0, random.gauss(0.8, 0.15)))
                    cell.slope = abs(random.gauss(5, 5))
                    cell.water = (x == self.width // 2) and random.random() < 0.7
                    cell.shelter = random.random() < 0.05

                elif terrain_type == "canyon":
                    cx = self.width / 2
                    canyon_dist = abs(x - cx)
                    cell.elevation_m = canyon_dist * 40 + random.gauss(0, 10)
                    cell.slope = min(70, canyon_dist * 8)
                    cell.tree_cover = max(0, 0.4 - canyon_dist * 0.05)
                    cell.water = canyon_dist < 2  # river at bottom
                    cell.shelter = random.random() < 0.04 and canyon_dist < 3

                cell.compute_signal(tx_elevation=300)
                self.cells[(x, y)] = cell

    def signal_map(self) -> List[str]:
        """ASCII signal strength map for display."""
        chars = " .:-=+*#@"
        lines = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                cell = self.cells.get((x, y))
                if cell:
                    idx = int(cell.signal_strength * (len(chars) - 1))
                    row += chars[idx]
                else:
                    row += "?"
            lines.append(row)
        return lines


# =============================================================================
# LOST PERSON BEHAVIOR MODEL
# =============================================================================

@dataclass
class LostPersonProfile:
    """
    How lost people move. Based on search and rescue research:
    - People follow water downhill
    - They seek shelter as temp drops
    - Children hide, adults wander
    - Injured people don't move far
    - Hikers follow trails even when lost
    """
    person_type: str               # hiker, child, elderly, injured, hunter
    mobility: float = 1.0         # 0-1 (0=immobile, 1=full mobility)
    follows_water: float = 0.5    # tendency to follow streams
    seeks_shelter: float = 0.3    # tendency to move toward shelter
    follows_downhill: float = 0.6 # tendency to go downhill
    wander_radius_cells: int = 5  # max cells from last known per hour
    hides: bool = False           # children and some elderly hide


PERSON_PROFILES = {
    "hiker": LostPersonProfile(
        person_type="hiker", mobility=0.9,
        follows_water=0.4, seeks_shelter=0.3,
        follows_downhill=0.7, wander_radius_cells=8,
    ),
    "child": LostPersonProfile(
        person_type="child", mobility=0.5,
        follows_water=0.6, seeks_shelter=0.5,
        follows_downhill=0.3, wander_radius_cells=3, hides=True,
    ),
    "elderly": LostPersonProfile(
        person_type="elderly", mobility=0.3,
        follows_water=0.5, seeks_shelter=0.7,
        follows_downhill=0.5, wander_radius_cells=2,
    ),
    "injured": LostPersonProfile(
        person_type="injured", mobility=0.1,
        follows_water=0.2, seeks_shelter=0.8,
        follows_downhill=0.1, wander_radius_cells=1,
    ),
    "hunter": LostPersonProfile(
        person_type="hunter", mobility=0.8,
        follows_water=0.3, seeks_shelter=0.2,
        follows_downhill=0.4, wander_radius_cells=10,
    ),
}


def compute_probability_map(area: SearchArea, profile: LostPersonProfile,
                            hours_missing: int) -> Dict[Tuple[int, int], float]:
    """
    Where is the lost person likely to be?

    Probability spreads from last known position based on:
    - Mobility and time elapsed
    - Terrain features (water, shelter, slope)
    - Person type behavior
    """
    lkp = area.last_known_position
    prob = {}
    max_radius = min(profile.wander_radius_cells * hours_missing,
                     max(area.width, area.height))

    for (x, y), cell in area.cells.items():
        dist = math.sqrt((x - lkp[0])**2 + (y - lkp[1])**2)

        if dist > max_radius:
            prob[(x, y)] = 0.0
            continue

        # Base: distance decay from last known
        base = math.exp(-dist / max(1, max_radius * 0.4))

        # Water attraction
        water_pull = profile.follows_water if cell.water else 0.0

        # Shelter attraction
        shelter_pull = profile.seeks_shelter if cell.shelter else 0.0

        # Downhill preference (lower elevation = higher probability)
        lkp_cell = area.cells.get(lkp)
        if lkp_cell:
            elev_diff = lkp_cell.elevation_m - cell.elevation_m
            downhill = profile.follows_downhill * max(0, elev_diff / 200)
        else:
            downhill = 0.0

        # Children hide: boost dense cover
        hide_factor = 0.0
        if profile.hides and cell.tree_cover > 0.6:
            hide_factor = 0.3

        total = base + water_pull + shelter_pull + downhill + hide_factor
        prob[(x, y)] = total

    # Normalize
    max_prob = max(prob.values()) if prob else 1
    if max_prob > 0:
        prob = {k: v / max_prob for k, v in prob.items()}

    return prob


# =============================================================================
# SEARCH PATTERNS — grid to spiral transition
# =============================================================================

PHI = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE = 2 * math.pi * (1 - 1 / PHI)


def grid_search_waypoints(area: SearchArea, altitude_m: float = 30.0,
                          spacing_cells: int = 2) -> List[Tuple[float, float, float]]:
    """
    Initial wide grid search. Covers maximum area quickly.
    Lawnmower pattern — simple, effective, proven.
    """
    waypoints = []
    for y in range(0, area.height, spacing_cells):
        xs = range(0, area.width) if (y // spacing_cells) % 2 == 0 else range(area.width - 1, -1, -1)
        for x in xs:
            wx = x * area.cell_size_m
            wy = y * area.cell_size_m
            cell = area.cells.get((x, y))
            # Adjust altitude for terrain
            ground = cell.elevation_m if cell else 0
            waypoints.append((wx, wy, ground + altitude_m))
    return waypoints


def spiral_search_waypoints(center_x: float, center_y: float,
                            ground_elev: float = 0.0,
                            altitude_m: float = 20.0,
                            num_points: int = 30,
                            spacing_m: float = 15.0) -> List[Tuple[float, float, float]]:
    """
    Tightening spiral around a hot zone (thermal hit or high probability).
    Golden angle spacing ensures no gaps.
    """
    waypoints = []
    for i in range(num_points):
        r = math.sqrt(i) * spacing_m
        theta = i * GOLDEN_ANGLE
        x = center_x + r * math.cos(theta)
        y = center_y + r * math.sin(theta)
        waypoints.append((x, y, ground_elev + altitude_m))
    return waypoints


def priority_search_waypoints(area: SearchArea, prob_map: Dict[Tuple[int, int], float],
                              altitude_m: float = 25.0,
                              top_n: int = 20) -> List[Tuple[float, float, float]]:
    """
    Search high-probability cells first. Skip low-probability areas.
    This is the efficiency gain from the lost person model —
    instead of searching everywhere equally, search where they likely are.
    """
    sorted_cells = sorted(prob_map.items(), key=lambda x: -x[1])
    waypoints = []
    for (x, y), prob in sorted_cells[:top_n]:
        if prob < 0.1:
            break
        cell = area.cells.get((x, y))
        ground = cell.elevation_m if cell else 0
        wx = x * area.cell_size_m
        wy = y * area.cell_size_m
        waypoints.append((wx, wy, ground + altitude_m))
    return waypoints


# =============================================================================
# LOW-SIGNAL NAVIGATION
# =============================================================================

@dataclass
class NavFix:
    """A position fix from whatever source is available."""
    source: str        # gps, landmark, dead_reckoning, signal_trilateration
    x: float
    y: float
    confidence: float  # 0-1
    timestamp: str = ""


class LowSignalNavigator:
    """
    Navigate when GPS is unreliable or dead.

    Fuses multiple weak signals:
    1. Last GPS fix (decays in confidence over time)
    2. Dead reckoning from IMU (heading + speed, drifts)
    3. Landmark matching (known features on terrain map)
    4. Signal strength trilateration (use signal shadows as position info)

    The key insight: in a canyon, GPS is useless but the signal
    shadow pattern IS position information. If you know where
    the signal is weak, you know where you are.
    """

    def __init__(self):
        self.fixes: List[NavFix] = []
        self.current_heading: float = 0.0    # degrees
        self.current_speed: float = 5.0      # m/s
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.confidence: float = 1.0

    def add_gps_fix(self, x: float, y: float, accuracy_m: float = 5.0):
        """GPS fix when available. Confidence based on accuracy."""
        conf = max(0.1, 1.0 - accuracy_m / 50.0)
        self.fixes.append(NavFix("gps", x, y, conf, datetime.now().isoformat()))
        self._fuse()

    def add_dead_reckoning(self, heading: float, speed: float, dt_seconds: float):
        """
        Estimate position from heading and speed.
        Drifts over time — confidence decays.
        """
        rad = math.radians(heading)
        dx = speed * math.sin(rad) * dt_seconds
        dy = speed * math.cos(rad) * dt_seconds
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        # Confidence decays with distance traveled
        dr_conf = max(0.05, self.confidence * 0.95)
        self.fixes.append(NavFix("dead_reckoning", new_x, new_y, dr_conf))
        self._fuse()

    def add_landmark_fix(self, x: float, y: float, landmark_name: str = ""):
        """
        Visual landmark match against terrain map.
        High confidence — you can see where you are.
        """
        self.fixes.append(NavFix("landmark", x, y, 0.85))
        self._fuse()

    def add_signal_fix(self, area: SearchArea, measured_signals: Dict[Tuple[int, int], float]):
        """
        Trilateration from signal strength pattern.
        Compare measured signal at current position to signal map.
        The cell with best match is likely position.

        In a canyon: GPS says nothing. But the signal shadow
        pattern says exactly where you are because each position
        has a unique combination of obstructions.
        """
        best_match = None
        best_score = float('inf')

        for (cx, cy), cell in area.cells.items():
            score = 0.0
            for (mx, my), measured in measured_signals.items():
                expected = cell.signal_strength
                score += (measured - expected) ** 2
            if score < best_score:
                best_score = score
                best_match = (cx * area.cell_size_m, cy * area.cell_size_m)

        if best_match:
            conf = max(0.1, 1.0 - best_score)
            self.fixes.append(NavFix("signal_trilateration",
                                      best_match[0], best_match[1], conf))
            self._fuse()

    def _fuse(self):
        """
        Weighted average of recent fixes.
        Higher confidence fixes pull harder.
        Older fixes decay in weight.
        """
        if not self.fixes:
            return

        # Use last 5 fixes
        recent = self.fixes[-5:]
        total_weight = 0.0
        wx, wy = 0.0, 0.0

        for i, fix in enumerate(recent):
            # Recency weight: more recent = heavier
            recency = (i + 1) / len(recent)
            weight = fix.confidence * recency
            wx += fix.x * weight
            wy += fix.y * weight
            total_weight += weight

        if total_weight > 0:
            self.position = (wx / total_weight, wy / total_weight)
            self.confidence = min(1.0, max(f.confidence for f in recent))

    def get_position(self) -> Tuple[float, float, float]:
        """Current best position estimate and confidence."""
        return (self.position[0], self.position[1], self.confidence)


# =============================================================================
# RESCUE COMMS PACKET
# =============================================================================

@dataclass
class RescuePacket:
    """
    Minimal rescue relay packet. Fits in a LoRa frame.

    When someone is found, this gets relayed back through the mesh.
    """
    found: bool = False
    position_x: float = 0.0
    position_y: float = 0.0
    position_confidence: float = 0.0
    responsive: bool = True        # person is conscious
    mobile: bool = True            # person can walk
    count: int = 1                 # number of people
    needs_medical: bool = False
    extraction_difficulty: int = 0 # 0=easy (walk out), 1=moderate, 2=helicopter
    timestamp: str = ""

    def to_bytes(self) -> bytes:
        """Pack to ~12 bytes for LoRa."""
        import struct
        flags = (
            (1 if self.found else 0) |
            (2 if self.responsive else 0) |
            (4 if self.mobile else 0) |
            (8 if self.needs_medical else 0)
        )
        return struct.pack(">BhhBBB",
                           flags,
                           int(self.position_x),
                           int(self.position_y),
                           int(self.position_confidence * 255),
                           min(255, self.count),
                           self.extraction_difficulty)

    def summary(self) -> str:
        status = "FOUND" if self.found else "searching"
        responsive = "responsive" if self.responsive else "UNRESPONSIVE"
        mobile = "mobile" if self.mobile else "IMMOBILE"
        medical = "NEEDS MEDICAL" if self.needs_medical else "no medical"
        extract = ["walk-out", "ground team", "helicopter"][min(2, self.extraction_difficulty)]
        return (f"[{status}] {self.count} person(s), {responsive}, {mobile}, "
                f"{medical}, extraction: {extract}, "
                f"pos=({self.position_x:.0f},{self.position_y:.0f}) "
                f"conf={self.position_confidence:.0%}")


# =============================================================================
# RESCUE MISSION
# =============================================================================

class RescueMission:
    """
    Coordinates a drone search and rescue operation.
    Manages terrain, probability, search patterns, navigation.
    """

    def __init__(self, terrain_type: str = "mountain",
                 grid_width: int = 20, grid_height: int = 20,
                 cell_size_m: float = 50.0):
        self.area = SearchArea(width=grid_width, height=grid_height,
                               cell_size_m=cell_size_m)
        self.area.build_terrain(terrain_type)
        self.navigator = LowSignalNavigator()
        self.person_profile: Optional[LostPersonProfile] = None
        self.prob_map: Dict[Tuple[int, int], float] = {}
        self.search_phase: str = "grid"  # grid -> priority -> spiral
        self.thermal_hits: List[Tuple[float, float, float]] = []  # x, y, confidence
        self.packets: List[RescuePacket] = []

    def set_lost_person(self, person_type: str = "hiker",
                         last_known: Tuple[int, int] = (10, 10),
                         hours_missing: int = 4):
        """Configure the lost person profile and compute probability map."""
        self.person_profile = PERSON_PROFILES.get(person_type,
                                                   PERSON_PROFILES["hiker"])
        self.area.last_known_position = last_known
        self.prob_map = compute_probability_map(
            self.area, self.person_profile, hours_missing)

    def get_waypoints(self) -> List[Tuple[float, float, float]]:
        """Get waypoints for current search phase."""
        if self.search_phase == "grid":
            return grid_search_waypoints(self.area)
        elif self.search_phase == "priority":
            return priority_search_waypoints(self.area, self.prob_map)
        elif self.search_phase == "spiral" and self.thermal_hits:
            hit = self.thermal_hits[-1]
            cell = self.area.cells.get(
                (int(hit[0] / self.area.cell_size_m),
                 int(hit[1] / self.area.cell_size_m)))
            ground = cell.elevation_m if cell else 0
            return spiral_search_waypoints(hit[0], hit[1], ground)
        return []

    def report_thermal_hit(self, x: float, y: float, confidence: float = 0.7):
        """Thermal anomaly detected — transition to spiral search."""
        self.thermal_hits.append((x, y, confidence))
        if confidence > 0.5:
            self.search_phase = "spiral"

    def report_found(self, x: float, y: float, responsive: bool = True,
                      mobile: bool = True, count: int = 1,
                      needs_medical: bool = False):
        """Person found. Generate rescue packet."""
        extract = 0 if mobile else (1 if responsive else 2)
        packet = RescuePacket(
            found=True, position_x=x, position_y=y,
            position_confidence=self.navigator.confidence,
            responsive=responsive, mobile=mobile,
            count=count, needs_medical=needs_medical,
            extraction_difficulty=extract,
            timestamp=datetime.now().isoformat(),
        )
        self.packets.append(packet)
        return packet

    def print_status(self):
        """Print mission status."""
        print(f"\n{'='*55}")
        print(f"  RESCUE MISSION — {self.search_phase.upper()} phase")
        print(f"{'='*55}")

        if self.person_profile:
            p = self.person_profile
            print(f"\n  Lost person: {p.person_type}")
            print(f"  Mobility: {p.mobility:.0%}  "
                  f"Follows water: {p.follows_water:.0%}  "
                  f"Seeks shelter: {p.seeks_shelter:.0%}")
            lkp = self.area.last_known_position
            print(f"  Last known: cell ({lkp[0]}, {lkp[1]})")

        # Signal map
        print(f"\n  SIGNAL MAP (stronger = more chars):")
        for line in self.area.signal_map():
            print(f"    {line}")

        # Probability hot spots
        if self.prob_map:
            top = sorted(self.prob_map.items(), key=lambda x: -x[1])[:5]
            print(f"\n  TOP PROBABILITY CELLS:")
            for (x, y), prob in top:
                cell = self.area.cells[(x, y)]
                features = []
                if cell.water:
                    features.append("water")
                if cell.shelter:
                    features.append("shelter")
                if cell.tree_cover > 0.6:
                    features.append("dense cover")
                feat_str = f" [{', '.join(features)}]" if features else ""
                print(f"    ({x:2d},{y:2d}) {prob:5.0%}  "
                      f"elev={cell.elevation_m:.0f}m  "
                      f"signal={cell.signal_strength:.0%}{feat_str}")

        # Waypoints
        waypoints = self.get_waypoints()
        print(f"\n  WAYPOINTS: {len(waypoints)} ({self.search_phase} pattern)")

        # Navigation
        pos = self.navigator.get_position()
        print(f"  NAV: ({pos[0]:.0f}, {pos[1]:.0f}) conf={pos[2]:.0%}")
        if self.navigator.fixes:
            last = self.navigator.fixes[-1]
            print(f"  Last fix: {last.source} conf={last.confidence:.0%}")

        # Thermal hits
        if self.thermal_hits:
            print(f"\n  THERMAL HITS:")
            for x, y, conf in self.thermal_hits:
                print(f"    ({x:.0f}, {y:.0f}) conf={conf:.0%}")

        # Found
        if self.packets:
            print(f"\n  RESCUE PACKETS:")
            for pkt in self.packets:
                print(f"    {pkt.summary()}")

        print(f"\n{'='*55}\n")


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 55)
    print("  RESCUE — drone search in GPS-denied terrain")
    print("  mountains, deep woods, canyons")
    print("=" * 55)

    # Mountain rescue scenario
    mission = RescueMission(terrain_type="mountain",
                            grid_width=20, grid_height=15)
    mission.set_lost_person("hiker", last_known=(10, 7), hours_missing=6)

    # Phase 1: Grid search
    print("\n  PHASE 1: Grid search")
    mission.print_status()

    # Simulate GPS fix then loss
    mission.navigator.add_gps_fix(500, 350, accuracy_m=3.0)
    print("  GPS fix acquired: (500, 350) accuracy 3m")

    # GPS lost in canyon — switch to dead reckoning
    mission.navigator.add_dead_reckoning(heading=180, speed=8.0, dt_seconds=30)
    print("  GPS lost. Dead reckoning: heading 180, 8 m/s")

    # Landmark fix
    mission.navigator.add_landmark_fix(480, 580, "rocky_outcrop")
    print("  Landmark match: rocky outcrop at (480, 580)")

    # Phase 2: Priority search (use probability model)
    mission.search_phase = "priority"
    waypoints = mission.get_waypoints()
    print(f"\n  PHASE 2: Priority search ({len(waypoints)} waypoints)")

    # Thermal hit
    mission.report_thermal_hit(450, 320, confidence=0.8)
    print("  THERMAL HIT at (450, 320) conf 80%")

    # Phase 3: Spiral around thermal hit
    spiral = mission.get_waypoints()
    print(f"\n  PHASE 3: Spiral search ({len(spiral)} waypoints)")

    # Found
    packet = mission.report_found(
        x=455, y=318, responsive=True, mobile=False,
        count=1, needs_medical=True)
    print(f"\n  {packet.summary()}")
    print(f"  Packet size: {len(packet.to_bytes())} bytes")

    mission.print_status()

    # Canyon scenario
    print(f"\n{'─'*55}")
    print("  CANYON RESCUE — signal shadow navigation")
    print(f"{'─'*55}")

    canyon = RescueMission(terrain_type="canyon",
                           grid_width=20, grid_height=10)
    canyon.set_lost_person("child", last_known=(10, 5), hours_missing=3)
    canyon.print_status()

    print(f"\n{'='*55}")
    print("  LOW-SIGNAL NAVIGATION")
    print(f"{'='*55}")
    print("""
  When GPS dies:
  1. Dead reckoning (heading + speed, drifts over time)
  2. Landmark matching (visual features on terrain map)
  3. Signal shadow trilateration (the ABSENCE of signal
     is position information — each canyon position has
     a unique obstruction pattern)

  The navigator fuses all available fixes weighted by
  confidence. More sources = better position.

  In a canyon, GPS says nothing. But the signal shadow
  says exactly where you are.
""")
