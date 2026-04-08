#!/usr/bin/env python3
# MODULE: Rescue/energy_efficient_ai.py
# PROVIDES: RESCUE.ENERGY_EFFICIENT_AI
# DEPENDS: stdlib-only
# RUN: python -m Rescue.energy_efficient_ai
# TIER: tool
# Energy-efficient AI for resource-constrained rescue operations
"""
Rescue/energy_efficient_ai.py — Energy-Efficient AI for Resource-Constrained Operations
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Bridges the Rosetta-Shape-Core ecosystem simulation to rescue and
resilience operations. The core insight from Rosetta's sim.py:

    Constrained agents don't fail — they grow differently.

When energy is low:
  - Don't explore (expensive). Expand (deepen what you know).
  - Don't broadcast (costs power). Listen (costs almost nothing).
  - Don't compute everything. Compute what matters.
  - Don't maintain all state. Maintain the minimum viable state.

This maps directly to:
  - Rescue drones with dying batteries
  - Mesh nodes on solar with limited power budgets
  - Village devices (GoatHerd, SAR) on cheap hardware
  - Any AI system that needs to do real work with almost nothing

The simulation proves: a system starting at 0.3 energy can still
discover paths, form connections, and build trust — if it knows
when to explore and when to expand.

Links to: https://github.com/JinnZ2/Rosetta-Shape-Core/blob/main/src/rosetta_shape_core/sim.py

Stdlib only.

USAGE:
    python -m Rescue.energy_efficient_ai
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


# =============================================================================
# ENERGY BUDGET MODEL
# =============================================================================

@dataclass
class EnergyBudget:
    """
    Tracks available energy and decides what operations are affordable.

    From Rosetta sim.py:
      complexity_cost = Shannon entropy of the agent's state
      branching_threshold = BRANCHING_K * complexity_cost
      if energy >= threshold: EXPLORE (discover new)
      if energy < threshold: EXPAND (deepen known)

    Applied to real devices:
      battery_wh: watt-hours remaining
      solar_input_w: watts from solar panel (0 at night)
      base_draw_w: minimum watts to stay alive
      compute_cost_w: watts per computation cycle
      transmit_cost_w: watts per radio transmission
    """
    battery_wh: float = 10.0        # watt-hours remaining
    battery_max_wh: float = 10.0
    solar_input_w: float = 0.0      # current solar generation
    base_draw_w: float = 0.5        # sleep mode draw
    compute_cost_w: float = 1.0     # per computation cycle
    transmit_cost_w: float = 2.0    # per transmission
    receive_cost_w: float = 0.1     # listening is cheap

    # Rosetta-derived thresholds
    explore_threshold: float = 0.4  # above this: explore (discover new)
    critical_threshold: float = 0.15 # below this: survival mode only

    def charge_fraction(self) -> float:
        """Battery level as 0-1."""
        return self.battery_wh / self.battery_max_wh if self.battery_max_wh > 0 else 0

    def hours_remaining(self) -> float:
        """Hours until battery dies at current draw."""
        net_draw = self.base_draw_w - self.solar_input_w
        if net_draw <= 0:
            return float('inf')  # solar covers base draw
        return self.battery_wh / net_draw

    def can_compute(self) -> bool:
        """Is there enough energy for one compute cycle?"""
        return self.battery_wh > self.compute_cost_w * 0.1  # 6 min of compute

    def can_transmit(self) -> bool:
        """Is there enough energy for one transmission?"""
        return self.battery_wh > self.transmit_cost_w * 0.05  # 3 min of transmit

    def mode(self) -> str:
        """
        Rosetta-derived operating mode.
        explore: enough energy to discover new information
        expand: preserve and deepen existing knowledge
        survive: minimum viable operations only
        dead: insufficient energy for any operation
        """
        frac = self.charge_fraction()
        if frac <= 0.02:
            return "dead"
        if frac < self.critical_threshold:
            return "survive"
        if frac < self.explore_threshold:
            return "expand"
        return "explore"

    def tick(self, seconds: float = 60.0, computing: bool = False,
             transmitting: bool = False):
        """Advance time. Drain battery, add solar."""
        hours = seconds / 3600.0
        # Solar input
        self.battery_wh = min(self.battery_max_wh,
                              self.battery_wh + self.solar_input_w * hours)
        # Base draw
        self.battery_wh -= self.base_draw_w * hours
        # Compute
        if computing:
            self.battery_wh -= self.compute_cost_w * hours
        # Transmit
        if transmitting:
            self.battery_wh -= self.transmit_cost_w * hours
        # Receive is always on (cheap)
        self.battery_wh -= self.receive_cost_w * hours
        # Floor at zero
        self.battery_wh = max(0.0, self.battery_wh)


# =============================================================================
# TASK SCHEDULER — what to compute when energy is limited
# =============================================================================

@dataclass
class Task:
    """A unit of work with energy cost and priority."""
    name: str
    compute_seconds: float          # how long this takes
    transmit_needed: bool = False   # does it need to send?
    priority: float = 1.0           # higher = more important
    result: Optional[str] = None
    completed: bool = False


class EfficientScheduler:
    """
    Decides what to do with limited energy.

    From Rosetta: when energy is low, expand (deepen known)
    instead of explore (discover new). Applied here:

    High energy (explore mode):
      - Run all sensors
      - Compute full search patterns
      - Broadcast frequently
      - Accept new tasks

    Low energy (expand mode):
      - Run critical sensors only
      - Use cached/simplified patterns
      - Broadcast only on change
      - Refuse non-essential tasks

    Critical energy (survive mode):
      - Listen only (receive costs 0.1W vs transmit 2.0W)
      - One emergency broadcast per hour
      - No computation beyond position
      - Wait for solar recharge

    This is the energy-efficient AI strategy: not a dumber version
    of the full system, but a DIFFERENT growth pattern that matches
    available resources. Exactly what biology does.
    """

    def __init__(self):
        self.tasks: List[Task] = []
        self.completed: List[Task] = []
        self.mode_history: List[str] = []

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: -t.priority)

    def schedule(self, budget: EnergyBudget) -> List[Task]:
        """
        Given current energy, decide which tasks to run.
        Returns tasks in execution order.
        """
        mode = budget.mode()
        self.mode_history.append(mode)
        runnable = []

        if mode == "dead":
            return []

        if mode == "survive":
            # Only highest-priority task, no transmit
            for t in self.tasks:
                if not t.completed and not t.transmit_needed:
                    runnable.append(t)
                    break
            return runnable

        if mode == "expand":
            # Run tasks that don't need transmit, up to 3
            count = 0
            for t in self.tasks:
                if not t.completed and count < 3:
                    if not t.transmit_needed or budget.can_transmit():
                        runnable.append(t)
                        count += 1
            return runnable

        # explore mode: run everything affordable
        for t in self.tasks:
            if not t.completed:
                if t.transmit_needed and not budget.can_transmit():
                    continue
                if not budget.can_compute():
                    break
                runnable.append(t)

        return runnable

    def execute(self, tasks: List[Task], budget: EnergyBudget):
        """Run scheduled tasks, drain energy accordingly."""
        for task in tasks:
            budget.tick(
                seconds=task.compute_seconds,
                computing=True,
                transmitting=task.transmit_needed,
            )
            task.completed = True
            task.result = f"completed in {budget.mode()} mode"
            self.completed.append(task)

        # Remove completed from pending
        self.tasks = [t for t in self.tasks if not t.completed]


# =============================================================================
# ADAPTIVE SENSOR MANAGER
# =============================================================================

class AdaptiveSensorManager:
    """
    Manages sensor duty cycles based on energy budget.

    Full power: all sensors at full rate
    Low power: reduce sample rates, disable non-critical
    Critical: position only, once per minute

    From Rosetta: the agent's active_sensors list changes
    based on energy and mode. Same principle, real hardware.
    """

    SENSOR_PROFILES = {
        "gps": {"power_w": 0.5, "priority": 3, "min_interval_s": 10},
        "thermal": {"power_w": 0.3, "priority": 2, "min_interval_s": 5},
        "radio_listen": {"power_w": 0.1, "priority": 4, "min_interval_s": 1},
        "barometer": {"power_w": 0.05, "priority": 2, "min_interval_s": 30},
        "camera": {"power_w": 1.5, "priority": 1, "min_interval_s": 10},
        "imu": {"power_w": 0.1, "priority": 3, "min_interval_s": 1},
    }

    def __init__(self):
        self.active: Dict[str, float] = {}  # sensor: current_interval
        self.readings: Dict[str, List] = {}

    def update_duty_cycle(self, budget: EnergyBudget) -> Dict[str, float]:
        """
        Adjust sensor intervals based on energy mode.
        Returns {sensor_name: sample_interval_seconds}.
        """
        mode = budget.mode()
        self.active.clear()

        for sensor, profile in self.SENSOR_PROFILES.items():
            min_int = profile["min_interval_s"]
            priority = profile["priority"]
            power = profile["power_w"]

            if mode == "dead":
                continue  # all off

            if mode == "survive":
                # Only priority 3+ sensors, at 10x slower rate
                if priority >= 3:
                    self.active[sensor] = min_int * 10
            elif mode == "expand":
                # Priority 2+ sensors, at 3x slower rate
                if priority >= 2:
                    self.active[sensor] = min_int * 3
            else:
                # explore: everything at normal rate
                self.active[sensor] = min_int

        return dict(self.active)


# =============================================================================
# COOPERATIVE ENERGY SHARING
# =============================================================================

def compute_energy_share(nodes: List[EnergyBudget],
                         share_fraction: float = 0.15) -> List[Tuple[int, int, float]]:
    """
    From Rosetta sim.py: higher-energy agents share with lower-energy ones.

    In practice: a drone with 60% battery gives 15% of its surplus
    to a drone at 10%. The mesh survives longer because no single
    node hits zero while others are full.

    Returns list of (from_idx, to_idx, wh_transferred).
    """
    transfers = []
    avg_energy = sum(n.charge_fraction() for n in nodes) / max(1, len(nodes))

    for i, donor in enumerate(nodes):
        if donor.charge_fraction() <= avg_energy:
            continue
        for j, recipient in enumerate(nodes):
            if i == j:
                continue
            if recipient.charge_fraction() >= avg_energy:
                continue
            # Transfer: share_fraction of the surplus
            surplus = donor.battery_wh - (avg_energy * donor.battery_max_wh)
            transfer = min(surplus * share_fraction,
                           recipient.battery_max_wh - recipient.battery_wh)
            if transfer > 0.1:
                donor.battery_wh -= transfer
                recipient.battery_wh += transfer
                transfers.append((i, j, round(transfer, 3)))

    return transfers


# =============================================================================
# MISSION ENERGY PLANNER
# =============================================================================

def plan_mission_energy(battery_wh: float, solar_w: float,
                        mission_hours: float,
                        tasks: List[Dict]) -> Dict:
    """
    Given a battery, solar input, mission duration, and task list,
    plan which tasks can be accomplished and when.

    Returns a schedule with mode transitions and task assignments.
    """
    budget = EnergyBudget(battery_wh=battery_wh, battery_max_wh=battery_wh,
                          solar_input_w=solar_w)
    scheduler = EfficientScheduler()
    sensors = AdaptiveSensorManager()

    for t in tasks:
        scheduler.add_task(Task(
            name=t["name"],
            compute_seconds=t.get("compute_s", 10),
            transmit_needed=t.get("transmit", False),
            priority=t.get("priority", 1.0),
        ))

    timeline = []
    steps = int(mission_hours * 60)  # 1-minute steps

    for minute in range(steps):
        mode = budget.mode()
        if mode == "dead":
            timeline.append({
                "minute": minute, "mode": mode,
                "battery_pct": 0, "action": "offline",
            })
            break

        # Schedule and execute
        runnable = scheduler.schedule(budget)
        if runnable:
            scheduler.execute(runnable[:1], budget)  # one per minute
            action = runnable[0].name
        else:
            budget.tick(seconds=60)  # idle tick
            action = "idle"

        # Sensor update
        duty = sensors.update_duty_cycle(budget)

        if minute % 10 == 0:  # log every 10 min
            timeline.append({
                "minute": minute,
                "mode": mode,
                "battery_pct": round(budget.charge_fraction() * 100, 1),
                "action": action,
                "sensors_active": len(duty),
                "tasks_pending": len(scheduler.tasks),
                "tasks_done": len(scheduler.completed),
            })

    return {
        "mission_hours": mission_hours,
        "starting_battery_wh": battery_wh,
        "solar_w": solar_w,
        "tasks_completed": len(scheduler.completed),
        "tasks_remaining": len(scheduler.tasks),
        "timeline": timeline,
        "final_battery_pct": round(budget.charge_fraction() * 100, 1),
        "mode_history": scheduler.mode_history[-5:],
    }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 60)
    print("  ENERGY-EFFICIENT AI")
    print("  constrained agents don't fail — they grow differently")
    print("=" * 60)

    # --- 1. Budget modes ---
    print(f"\n{'─'*60}")
    print("  ENERGY MODES (from Rosetta ecosystem simulation)")
    print(f"{'─'*60}")

    scenarios = [
        ("Full battery + solar", 10.0, 2.0),
        ("Half battery, no solar", 5.0, 0.0),
        ("Low battery, some solar", 1.5, 0.5),
        ("Critical battery", 0.8, 0.0),
        ("Nearly dead", 0.15, 0.0),
    ]
    for desc, batt, solar in scenarios:
        b = EnergyBudget(battery_wh=batt, solar_input_w=solar)
        mode = b.mode()
        hrs = b.hours_remaining()
        hrs_str = f"{hrs:.1f}h" if hrs < 100 else "inf"
        print(f"    {desc:30s} → {mode:8s}  "
              f"({b.charge_fraction():.0%} charge, {hrs_str} remaining)")

    # --- 2. Sensor duty cycling ---
    print(f"\n{'─'*60}")
    print("  SENSOR DUTY CYCLING")
    print(f"{'─'*60}")

    sensors = AdaptiveSensorManager()
    for mode_name, batt in [("explore", 8.0), ("expand", 2.5), ("survive", 0.8)]:
        b = EnergyBudget(battery_wh=batt, battery_max_wh=10.0)
        duty = sensors.update_duty_cycle(b)
        active = ", ".join(f"{s}({int(i)}s)" for s, i in sorted(duty.items()))
        print(f"    {mode_name:8s}: {active or 'all off'}")

    # --- 3. Cooperative energy sharing ---
    print(f"\n{'─'*60}")
    print("  COOPERATIVE ENERGY SHARING")
    print(f"{'─'*60}")

    nodes = [
        EnergyBudget(battery_wh=8.0, battery_max_wh=10.0),
        EnergyBudget(battery_wh=6.0, battery_max_wh=10.0),
        EnergyBudget(battery_wh=1.0, battery_max_wh=10.0),
        EnergyBudget(battery_wh=0.5, battery_max_wh=10.0),
    ]
    print(f"    Before: {[f'{n.charge_fraction():.0%}' for n in nodes]}")
    transfers = compute_energy_share(nodes)
    for fr, to, wh in transfers:
        print(f"    Node {fr} → Node {to}: {wh} Wh")
    print(f"    After:  {[f'{n.charge_fraction():.0%}' for n in nodes]}")

    # --- 4. Mission planning ---
    print(f"\n{'─'*60}")
    print("  MISSION ENERGY PLAN (2-hour rescue, 5Wh battery, 0.5W solar)")
    print(f"{'─'*60}")

    tasks = [
        {"name": "grid_search", "compute_s": 30, "transmit": True, "priority": 3},
        {"name": "thermal_scan", "compute_s": 15, "transmit": False, "priority": 4},
        {"name": "probability_update", "compute_s": 20, "transmit": False, "priority": 2},
        {"name": "relay_position", "compute_s": 5, "transmit": True, "priority": 5},
        {"name": "photo_capture", "compute_s": 10, "transmit": True, "priority": 1},
        {"name": "spiral_search", "compute_s": 25, "transmit": False, "priority": 3},
        {"name": "landmark_match", "compute_s": 15, "transmit": False, "priority": 2},
    ]

    result = plan_mission_energy(
        battery_wh=5.0, solar_w=0.5,
        mission_hours=2.0, tasks=tasks,
    )

    for entry in result["timeline"]:
        mode = entry["mode"]
        marker = {"explore": "+", "expand": "=", "survive": "!", "dead": "X"}.get(mode, "?")
        print(f"    {marker} T+{entry['minute']:3d}m  {mode:8s}  "
              f"batt={entry['battery_pct']:5.1f}%  "
              f"act={entry.get('action', '?'):20s}  "
              f"sensors={entry.get('sensors_active', '?')}")

    print(f"\n    Tasks completed: {result['tasks_completed']}/{result['tasks_completed'] + result['tasks_remaining']}")
    print(f"    Final battery: {result['final_battery_pct']}%")

    print(f"\n{'='*60}")
    print("  THE ROSETTA PRINCIPLE")
    print(f"{'='*60}")
    print("""
  From the Rosetta-Shape-Core ecosystem simulation:

    "Constrained agents don't fail — they grow differently."

  When a rescue drone's battery drops to 15%:
    - It doesn't try to do everything slower
    - It SWITCHES STRATEGY: listen instead of broadcast,
      cache instead of compute, deepen instead of explore

  When a mesh node runs on solar at night:
    - It doesn't shut down
    - It enters EXPAND mode: maintain connections,
      serve cached data, wait for dawn

  When a village phone has 5% battery:
    - The GoatHerd app doesn't crash
    - It saves state and tells you the one thing
      that matters: "move to temple_field"

  This is energy-efficient AI: not less capable,
  but differently capable. The same physics that
  lets mycelium thrive at 0.3 energy in Rosetta's
  simulation lets a $15 LoRa node keep a mesh alive
  through a three-day grid failure.

  Biology figured this out 3.8 billion years ago.
  We just wrote it down.

  Link: github.com/JinnZ2/Rosetta-Shape-Core/blob/main/src/rosetta_shape_core/sim.py
""")
