# SAR Swarm Deployment Guide

Practical guide for search and rescue departments evaluating or deploying
geometric swarm coordination. Written for operational staff, not software
engineers.

CC0 public domain.

---

## What This System Does

This is a coordination framework for drone swarms during search and rescue
operations. It solves three problems:

1. **Formation recovery after dropout.** When a drone loses comms or power
   in a blizzard, the swarm reforms around the gap instead of cascading
   into failure. Commercial systems lose ~20% of the swarm on a single
   dropout. This system recovers because it maintains geometric state
   checkpoints and rolls back when it detects inconsistency.

2. **Survivor detection without GPS.** Thermal anomaly detection triggers
   automatic spiral tightening around hot zones. The coordination math
   works on local geometry, not satellite fixes. When smoke kills GPS,
   the icosahedral state machine still tracks valid transitions.

3. **Resource allocation under load.** The golden-angle spiral ensures
   uniform coverage without overlap. As wind load increases, the spiral
   contracts to keep drones closer together. As battery drains, patrol
   density scales down gracefully.

## What This System Does Not Do

- It does not fly drones. It computes coordination logic. You still
  need flight controllers (ArduPilot, Betaflight, etc).
- It does not replace trained SAR operators. It assists with formation
  management and resource allocation.
- It does not require internet, cloud services, or cell coverage.
- It has not been tested in live SAR operations. It has been validated
  in simulation only.

---

## System Tiers

### Tier 1: Simulation Only (Cost: $0)

Run the coordination logic on any computer with Python 3 to evaluate
whether the approach fits your operational needs.

**Requirements:**
- Any computer with Python 3.6+
- No internet required
- No packages to install

**What you get:**
- 50-drone blizzard simulation with configurable dropout rates
- Survivor detection with thermal vector processing
- Formation recovery metrics
- Spiral allocation visualization data

**How to run:**
```
python SAR/workflow_bridge.py
```

**What to look at:**
- Node allocation count (did drones get assigned positions?)
- Backtrack count (how many recoveries happened?)
- Survivor hit count (how many thermal anomalies detected?)

---

### Tier 2: Bench Test (Cost: ~$50-200)

Run the coordination logic on a Raspberry Pi connected to simulated
or real drone telemetry via serial/radio.

**Hardware:**
| Item                    | Approximate Cost | Source              |
|-------------------------|-----------------|---------------------|
| Raspberry Pi 4 (2GB)   | $35             | Any electronics shop |
| LoRa radio module       | $10-15          | HopeRF RFM95W       |
| SD card (16GB+)        | $5              | Any                  |
| Power bank              | $10             | Any USB-C bank       |

**Software:**
- Raspbian Lite (headless)
- Python 3 (pre-installed)
- Copy `SAR/workflow_bridge.py` to the Pi

**What you get:**
- Coordination logic running on field-deployable hardware
- Serial input for telemetry (adaptable to any radio)
- Decision output for waypoint commands

---

### Tier 3: SITL Test (Cost: ~$200)

Run against ArduPilot's Software-In-The-Loop simulator to test with
realistic flight physics before purchasing drones.

**Additional requirements:**
- ArduPilot development environment
- `pymavlink` Python package
- Desktop or laptop (SITL is compute-heavy)

**What you get:**
- 4-drone simulated missions with realistic physics
- MAVLink telemetry parsing
- Waypoint command output to simulated flight controllers

---

### Tier 4: Flight Test (Cost: ~$500-2000)

Deploy on actual drones for controlled outdoor testing.

**This tier requires:**
- FAA Part 107 certification (or your country's equivalent)
- Appropriate airspace authorization
- Trained pilot(s) with manual override capability
- Insurance
- Written safety procedures and risk assessment

**Do not skip directly to this tier.**

---

## Hardware Build Plan (Tier 2+)

### Coordination Node

The coordination node runs the geometric pipeline and communicates
with drones via radio.

```
┌─────────────────────────────┐
│  Raspberry Pi               │
│  ┌───────────────────────┐  │
│  │ workflow_bridge.py     │  │
│  │ (coordination logic)   │  │
│  └───────┬───────────────┘  │
│          │ serial/SPI        │
│  ┌───────┴───────────────┐  │
│  │ LoRa Radio Module      │  │
│  │ (RFM95W or similar)    │  │
│  └───────────────────────┘  │
│                              │
│  Power: USB-C battery pack   │
└─────────────────────────────┘
```

### Telemetry Format

Each drone sends a 5-value vector every cycle:

| Value | Field     | What to Measure               | How                          |
|-------|-----------|-------------------------------|------------------------------|
| 0     | Health    | Overall drone status (0-1)    | Battery + IMU + motor status |
| 1     | Altitude  | Normalized altitude (0-1)     | Barometer / max_alt          |
| 2     | Battery   | Remaining charge (0-1)        | Voltage / full_voltage       |
| 3     | Thermal   | Heat signature (0-1)          | IR sensor / max_temp         |
| 4     | Wind      | Wind load estimate (0-1)      | Groundspeed deviation / max  |

These five values are all the coordination node needs. The mapping from
your specific hardware to these five numbers is the integration work.

---

## Operational Concepts

### Formation Recovery

When a drone drops out:
1. The coordination node detects the gap via parity check failure
2. After 3 consecutive failures, the node rolls back to the last
   known good state
3. Remaining drones receive updated allocations that close the gap
4. The spiral contracts slightly to maintain coverage density

This happens automatically. The operator sees the node count drop and
the backtrack count increment.

### Survivor Detection

When a drone's thermal sensor reads above the threshold (default 0.7):
1. The coordination node flags a "survivor hit"
2. The spiral allocation boosts local density (2x default)
3. Nearby drones receive tighter waypoints around the hot zone
4. The hit is logged with drone ID and allocation coordinates

### Battery Management

As batteries drain:
- The spiral contracts (shorter patrol distances)
- Wind load tolerance decreases
- Below 10% charge, the drone health drops to 0 (treated as dropout)

This is handled by the telemetry vector, not special logic. The
geometric pipeline naturally adapts to changing input values.

---

## SeaFrost: Maritime Fire Suppression

A specialized configuration for lithium battery fires on ships.

### The Problem

Lithium batteries in shipping containers reach 1000C during thermal
runaway. Cell-to-cell propagation happens in 30-60 seconds.
Container-to-container in 5-15 minutes. Traditional suppression
(water, CO2 alone) is ineffective. Coast Guard response is 15-60
minutes.

### The Approach

Staged cryogenic cooling delivered by a 4-drone wolf pack:

| Time  | Stage     | Action                     | Result        |
|-------|-----------|---------------------------|---------------|
| T+0s  | Recon     | Alpha thermal scan         | Epicenter fix |
| T+15s | Pre-cool  | Beta1+Beta2 CO2 burst      | 1000C -> 400C |
| T+30s | Kill      | Gamma LN2 flood            | 400C -> -20C  |
| T+45s | Confirm   | Alpha thermal re-scan      | Runaway stopped |

### Why Staged

Direct LN2 on a 1000C surface causes explosive thermal shock (steam
explosion from trapped moisture, material fracture from extreme
gradient). CO2 pre-cooling brings the temperature into a range where
LN2 can be applied safely.

### Ship Integration

The digital twin (`SeaFrost/digital_twin.py`) pre-calculates flight
paths from ship blueprints:

1. Upload vessel blueprint JSON (deck layout + cargo manifest)
2. System identifies lithium battery containers automatically
3. Wolf pack attack angles computed for each container
4. On alarm: one-button launch, zero navigation delay

### SeaFrost Build (Prototype)

**Bill of materials for a garage-scale test system:**

| Component              | Qty | Cost Each | Notes                     |
|------------------------|-----|-----------|---------------------------|
| 90mm whoop frame       | 4   | $2-10     | Crash-resistant micro quad |
| 1103 10000kv motors    | 16  | $3        | Salvage from broken quads  |
| Flight controller      | 4   | $15-30    | Matek H743 mini or equiv  |
| 450mAh 1S battery      | 8   | $5        | 2 per drone (hot swap)     |
| MLX90614 IR sensor     | 1   | $2-8      | Alpha scout thermal        |
| 20g CO2 cartridge      | 12  | $1        | BB gun supply; 6 per Beta  |
| Solenoid valve         | 2   | $5        | One per Beta drone         |
| LN2 syringe pump       | 1   | $10       | Arduino peristaltic        |
| Crossfire Nano RX      | 4   | $15-25    | Smoke-penetrating range    |
| Arduino Nano           | 4   | $2        | Payload controller per drone |
| PVC launch cage        | 1   | $15       | 4" dia x 24" + plywood base |

**Total: approximately $200-400 for a test system.**

LN2 is available from welding supply shops. CO2 cartridges from
sporting goods. Everything else from hobby electronics.

### SeaFrost Test Sequence (Garage Scale)

Test against a controlled small fire (phone battery) in a safe,
ventilated space with fire extinguisher backup.

1. Set up PVC launch cage on stable surface
2. Load 4 drones with payloads
3. Start controlled thermal source
4. Manual launch sequence:
   - Alpha confirms thermal lock
   - Beta1 + Beta2 CO2 burst (2 second activation)
   - Gamma LN2 application
5. Verify temperature drop with thermocouple

**Expected results at garage scale (1kW source):**
- CO2 stage: 700C -> 350C in ~8 seconds
- LN2 stage: 350C -> -15C in ~10 seconds
- Total mission: ~25 seconds

---

## Decision Matrix

Use this to determine whether this system fits your needs.

| Question                                      | If Yes                    | If No                      |
|-----------------------------------------------|---------------------------|----------------------------|
| Do you operate in GPS-denied environments?    | This helps significantly  | Standard systems may suffice |
| Do you lose drones to weather regularly?       | Formation recovery helps  | Less critical               |
| Do you need thermal search patterns?           | Spiral allocation helps   | Manual patterns may work    |
| Do you have Python experience on staff?        | Faster integration        | Plan for learning curve     |
| Do you need certified/supported software?      | This is not that          | Look at commercial options  |
| Is your budget under $1000?                    | This is designed for that | More options available      |

---

## Limitations

- **Not certified.** This software carries no warranty, certification,
  or regulatory approval. It is a research tool released to the public
  domain.
- **Simulation only.** All results are from computational simulation.
  No live SAR deployment has been conducted.
- **No autopilot.** This handles coordination logic, not flight control.
  Integration with ArduPilot or equivalent is required for flight.
- **Parity rates vary.** The dodecahedral parity check returns low pass
  rates when inputs are uniform. This is mathematically correct (identical
  inputs produce identical walks that don't close), not a defect. Real
  deployments with spatially diverse drones produce meaningful parity.
- **2D allocation.** The spiral is planar. Altitude coordination requires
  additional logic.
- **SeaFrost is untested at ship scale.** The physics model is sound
  (Stefan-Boltzmann + forced convection), but no full-scale maritime
  test has been conducted. The garage-scale test validates the approach
  at 1kW; scaling to ship-scale (50kW+) is projected, not measured.

---

## Regulatory Notes

### Drone Operations (US)
- FAA Part 107 certification required for commercial drone use
- Waivers may be needed for beyond-visual-line-of-sight operations
- Emergency operations may qualify for COA (Certificate of Authorization)
- Contact your local FSDO (Flight Standards District Office) early

### Maritime (SeaFrost)
- IMO SOLAS Chapter II-2 covers fire protection on ships
- Flag state approval required for vessel installations
- Port authority coordination for emergency protocols
- Consult maritime safety counsel before any vessel deployment

### General
- This is a CC0 public domain tool. There is no vendor to call.
  Your department assumes full responsibility for deployment.
- Start with simulation (Tier 1). Progress through bench test (Tier 2)
  and SITL (Tier 3) before any flight test (Tier 4).
- Document everything. Your data helps the next department.

---

## Contact and Contribution

This project is maintained at:
https://github.com/JinnZ2/Resilience

To report issues or contribute improvements:
https://github.com/JinnZ2/Resilience/issues

There is no commercial entity behind this project. It was built by
a long-haul truck driver observing the systems being modeled, and
released to the public domain because the people who need these tools
the most are the ones least likely to be able to pay for them.
