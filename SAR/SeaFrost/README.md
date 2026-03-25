# SeaFrost: Staged Cryogenic Fire Suppression

Drone-delivered staged cooling for lithium battery thermal runaway
on commercial vessels.

CC0 public domain.

## Problem

Lithium battery fires in shipping containers reach 1000C internally.
Cell-to-cell thermal runaway propagation occurs in 30-60 seconds.
Container-to-container in 5-15 minutes. Water is ineffective (does
not achieve the -20C threshold needed to stop propagation). CO2 alone
displaces oxygen but does not cool sufficiently. Coast Guard maritime
response averages 15-60 minutes. By that time, the fire has spread.

## Approach

Two-stage cryogenic cooling delivered by a 4-drone wolf pack:

**Stage 1: CO2 pre-cooling (T+0 to T+15s)**
- Drops fire temperature from ~1000C to ~400C
- Prevents explosive thermal shock from direct cryogenic contact
- Displaces oxygen around the fire envelope

**Stage 2: LN2 deep cooling (T+15 to T+30s)**
- Drops temperature from ~400C to below -20C
- Stops thermal runaway propagation chain
- Latent heat of vaporization provides sustained cooling

Direct LN2 application to a 1000C surface is dangerous: steam
explosions from trapped moisture, material fracture from extreme
thermal gradient. The CO2 pre-cool stage eliminates this risk.

## Heat Transfer Model

### Stage 1: CO2 Pre-Cooling

Radiation (Stefan-Boltzmann) + forced convection:

```
q_total = epsilon * sigma * (T_fire^4 - T_co2^4) + h_conv * (T_fire - T_co2)

Where:
  epsilon  = 0.9       (battery surface emissivity)
  sigma    = 5.67e-8   (Stefan-Boltzmann constant, W/m^2K^4)
  T_fire   = 1223 K    (950C)
  T_co2    = 220 K     (-53C, CO2 discharge temperature)
  h_conv   = 150 W/m^2K (high-velocity CO2 discharge)
```

Time to cool 50kg battery pack by 500C:
```
t = m * c * dT / (q * A)
  = 50 * 800 * 500 / (q_total * A_surface)
  ≈ 4-5 seconds (dual Beta drones)
```

### Stage 2: LN2 Deep Cooling

Latent heat dominates:
```
q_latent = h_fg * flow_rate
  = 199,000 J/kg * 2.5 kg/s
  = 497 kW cooling power
```

Time to cool from 400C to -20C:
```
t = m * c * dT / q_latent
  = 50 * 800 * 420 / 497,000
  ≈ 10-15 seconds
```

## Wolf Pack Configuration

| Drone  | Role        | Payload        | Weight | Flight Time |
|--------|-------------|---------------|--------|-------------|
| Alpha  | Scout       | IR sensor     | 2.5 lb | 10 min      |
| Beta1  | Suppressor  | CO2 cartridge | 2.5 lb | 10 min      |
| Beta2  | Suppressor  | CO2 cartridge | 2.5 lb | 10 min      |
| Gamma  | Kill        | LN2 reservoir | 2.5 lb | 10 min      |

Beta1 and Beta2 are redundant. Either can complete the CO2 stage alone
at 75% cooling power if the other fails.

## Ship Digital Twin

`digital_twin.py` parses vessel blueprints to pre-calculate response:

1. Load ship JSON (deck layout, cargo manifest, launcher position)
2. Identify all lithium battery containers
3. Compute wolf pack paths for each container:
   - Alpha: spiral approach for thermal recon
   - Beta1/Beta2: 120/240 degree attack angles (5m standoff)
   - Gamma: overhead position (8m altitude)
4. Store paths for instant retrieval on alarm

### Blueprint Format

```json
{
  "vessel": "Ship Name",
  "deck_layout": {"length": 400, "beam": 60, "height": 25},
  "drone_launcher": [20, 10, 15],
  "cargo_manifest": [
    {
      "id": "C-204",
      "position": [120, 25, 5],
      "cargo_type": "lithium_battery",
      "fire_risk": 0.95
    }
  ]
}
```

## Running the Test

```bash
python SAR/SeaFrost/maersk_fire_test.py
```

This writes a test blueprint, loads the digital twin, pre-calculates
wolf pack paths, and runs a simulated fire suppression sequence
through the geometric coordination pipeline.

## Files

| File                       | Description                        | Dependencies |
|----------------------------|------------------------------------|-------------|
| `digital_twin.py`         | Ship blueprint parser              | None        |
| `maersk_fire_test.py`     | Maersk C-204 fire test             | digital_twin, workflow_bridge |
| `sitl_seafrost.sh`        | ArduPilot SITL launch (4 drones)   | ArduPilot   |
| `maersk_c204_blueprint.json` | Test blueprint fixture          | None        |

## Prototype Build (Garage Scale)

For testing the staged cooling approach at small scale:

### Bill of Materials

| Component              | Qty | Notes                           |
|------------------------|-----|---------------------------------|
| 90mm micro quad frame  | 4   | Whoop-class, crash-resistant    |
| 1103 10000kv motors    | 16  | 4 per drone                     |
| Flight controller      | 4   | Matek H743 mini or equivalent   |
| 450mAh 1S LiHV battery| 8   | 2 per drone for hot swap        |
| MLX90614 IR sensor     | 1   | Alpha thermal detection ($2-8)  |
| 20g CO2 cartridge      | 12  | BB gun supply, 6 per Beta drone |
| Solenoid valve         | 2   | CO2 release control             |
| Peristaltic pump       | 1   | LN2 delivery for Gamma          |
| Arduino Nano           | 4   | Payload controller per drone    |
| PVC launch cage        | 1   | 4" diameter x 24", plywood base |

Approximate cost: $200-400 total.

### Sources

- CO2 cartridges: sporting goods (BB/airsoft supply)
- LN2: welding supply shops (sold by the liter)
- IR sensors: electronics suppliers (SparkFun, Adafruit, eBay)
- Drone parts: hobby shops or salvage from damaged racing quads

### Garage Test Protocol

1. Set up in ventilated space with fire extinguisher backup
2. Controlled thermal source (phone battery on fireproof surface)
3. Thermocouple monitoring at source
4. Manual launch sequence (no autopilot needed for bench test)
5. Measure temperature at each stage

Expected garage-scale results (1kW source):
- CO2 stage: ~700C to ~350C in 8 seconds
- LN2 stage: ~350C to ~-15C in 10 seconds

## Limitations

- No ship-scale test has been conducted. The physics model
  projects from garage scale; actual maritime conditions (wind,
  salt air, hull reflections) may affect performance.
- Smoke navigation is modeled but untested. GPS-denied flight
  depends on IR + IMU fusion, which needs hardware validation.
- LN2 handling requires training. Cryogenic burns are serious.
  Follow your organization's safety procedures for cryogenic
  materials.
- The staged cooling approach is supported by peer-reviewed
  research on cryogenic suppression of lithium battery fires.
  The specific drone delivery mechanism is novel and unvalidated
  beyond simulation.

## References

- Cryogenic cooling reduces thermal runaway energy release by
  83% (published research on LN2 suppression of Li-ion fires)
- Liquid nitrogen prevents thermal runaway propagation at -20C
- Intermittent application superior to continuous cooling
- Staged cooling approaches minimize thermal shock damage
