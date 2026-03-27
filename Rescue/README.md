# Rescue

Drone search and rescue in GPS-denied terrain: mountains, deep woods, canyons.

CC0 public domain. Stdlib only.

## What It Does

- **Lost person modeling**: Where do lost people go? Hikers follow water downhill.
  Children hide in dense cover. Injured people stay put. The probability map
  tells drones where to search first instead of searching everywhere equally.

- **Three search phases**: Grid (wide coverage) -> Priority (high-probability cells
  first) -> Spiral (tighten around thermal hit). Transitions automatically.

- **Low-signal navigation**: When GPS dies in a canyon or under tree cover, the
  navigator fuses dead reckoning, landmark matching, and signal shadow
  trilateration. The absence of signal IS position information — each canyon
  position has a unique obstruction pattern.

- **Rescue comms packet**: 8 bytes. Found/not, responsive/not, mobile/not,
  needs medical, extraction difficulty, position. Fits in a LoRa frame.

- **Terrain-aware signal mapping**: Elevation, tree cover, and slope degrade
  radio signal. The map shows where comms work and where they don't.

## Quick Start

```
python -m Rescue.rescue
```

## Terrain Types

- `mountain`: Elevation rises toward center, ridges, streams, sparse cover at altitude
- `forest`: Dense tree cover, flat terrain, rivers, limited visibility
- `canyon`: Deep walls, river at bottom, extreme signal shadow, shelter in overhangs

## Lost Person Profiles

| Type    | Mobility | Follows Water | Seeks Shelter | Hides | Wander/hr |
|---------|----------|---------------|---------------|-------|-----------|
| Hiker   | 90%      | 40%           | 30%           | No    | 8 cells   |
| Child   | 50%      | 60%           | 50%           | Yes   | 3 cells   |
| Elderly | 30%      | 50%           | 70%           | No    | 2 cells   |
| Injured | 10%      | 20%           | 80%           | No    | 1 cell    |
| Hunter  | 80%      | 30%           | 20%           | No    | 10 cells  |

Based on SAR research: children hide in dense cover, injured people
don't move, hikers follow trails and water downhill, elderly seek shelter.

## Low-Signal Navigation

When GPS fails, the navigator fuses:

1. **Dead reckoning**: Heading + speed. Drifts over time. Confidence decays.
2. **Landmark matching**: Visual features against terrain map. High confidence.
3. **Signal shadow trilateration**: Measure signal strength at current position.
   Compare against signal map. The pattern of obstructions is unique per location.

Weighted fusion: more sources = better position. Recent fixes weighted heavier.

## Search Phase Transitions

```
GRID (wide lawnmower)
  |
  v  [probability model loaded]
PRIORITY (search high-probability cells first)
  |
  v  [thermal hit detected, confidence > 50%]
SPIRAL (golden angle tightening around hot zone)
  |
  v  [person found]
RELAY (broadcast rescue packet through mesh)
```

## Rescue Packet

8 bytes, LoRa-compatible:

| Field      | Bits | Values                          |
|------------|------|---------------------------------|
| Flags      | 8    | found, responsive, mobile, medical |
| Position X | 16   | signed meters from origin       |
| Position Y | 16   | signed meters from origin       |
| Confidence | 8    | 0-255 mapped to 0-100%          |
| Count      | 8    | number of people found          |
| Extraction | 8    | 0=walk-out, 1=ground, 2=helicopter |

## Files

| File       | Description              | Dependencies |
|------------|--------------------------|-------------|
| rescue.py  | Full rescue module       | None        |
| README.md  | This file                | None        |

## Limitations

- Terrain is procedurally generated, not real topographic data.
  Real deployment needs actual elevation maps.
- Signal model is simplified — real radio propagation is more complex.
- No audio-based detection (would need microphone + FFT).
- Probability model is based on published SAR statistics but
  not calibrated to specific Sri Lankan terrain.
- No thermal camera integration — thermal hits are manual input.
