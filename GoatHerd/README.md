# GoatHerd

Village goat herding assistant. No internet, no cloud, just Python.

CC0 public domain.

## What It Does

- Tracks your goats (health, weight, breeding, age)
- Tracks your grazing zones (grass level, water, predator risk)
- Tells you when to move (grass depleting)
- Tells you where to move (best zone scored by grass + water + safety)
- Alerts on sick goats, predators, low water
- Tracks daily food and water needs
- Shows which goats are ready for market
- Saves everything in CSV files you can open anywhere

## What It Needs

- Python 3 (install Termux on Android, it's free)
- No internet
- No account
- No money

## Quick Start

```
python GoatHerd/herd.py
```

Commands:
```
s = show status
d = advance one day
m = move to zone
a = add a goat
z = add a grazing zone
b = record breeding
v = save
q = quit
```

## How Grazing Zones Work

Each zone has grass that regrows over time. When you graze goats,
they eat the grass. When you move them, the grass recovers.

The math is logistic growth:
```
new_grass = grass + rate * grass * (1 - grass / max_grass)
```

This means:
- Grass grows slowly when there's very little (hard to start from nothing)
- Grass grows fastest in the middle (nature's sweet spot)
- Grass stops growing when it reaches full capacity

The system tells you when grass is low (below 30%) and recommends
the best zone to move to based on:
- Grass level (more grass = better)
- Water nearby (goats need water every day)
- Predator risk (lower = safer)
- Terrain difficulty (flat = easier)
- How long since you grazed there (longer rest = more regrowth)

## How Health Works

Each goat's health changes daily based on:
- Good grazing + water = slow recovery (+2% per day)
- No water = fast decline (-15% per day)
- Poor grazing = slow decline (-5% per day)

Lactating goats need 80% more food. Pregnant goats need 30% more.
The system tracks this and tells you total daily needs.

## Market Readiness

The system flags goats ready to sell:
- Males over 8 months and 20+ kg
- Surplus females only if herd has more than 10 does

It won't recommend selling pregnant or sick goats.

## Data Storage

Everything saves to simple CSV files:
- `data/goats.csv` — all your goats
- `data/zones.csv` — all your grazing zones
- `data/state.json` — current zone and day count

Open these in any spreadsheet app on your phone.

## Adding Your Own Zones

When you start, add your real grazing areas:

```
> z
Zone name: river_bank
Water nearby? (y/n) [y]: y
Predator risk (0-1) [0]: 0.1
Added zone river_bank
```

Set predator risk higher for areas near forest (leopards, wild dogs).
Set it low for areas near the village.

## Adding Your Goats

```
> a
ID (number): 1
Name: Lakshmi
Sex (M/F): F
Age months [12]: 36
Weight kg [25]: 32
Added Lakshmi
```

## What the Math Does

You don't need to understand the math. But if you're curious:

- **Logistic growth** models grass recovery. Same equation that
  describes how fish populations recover after harvesting.
- **Zone scoring** multiplies grass, water, safety, and terrain
  factors together. A zone with great grass but no water
  still scores low.
- **Health model** uses the same kind of equation that models
  how batteries charge and discharge. Conditions determine the rate.
- **Golden angle** (137.5 degrees) ensures that if you rotate
  through zones in order, you get maximum rest time between visits.
  Same angle that sunflower seeds use to pack efficiently.

## Limitations

- No GPS tracking (would need hardware)
- No predator detection (would need sensors)
- Weather awareness is not built in yet
- Market prices are not tracked (would need connectivity)
- The grass model is simplified — real regrowth depends on
  rainfall, soil type, and season. Adjust `regrowth_rate`
  for your local conditions.

## For Developers

The grazing model uses the same substrate properties as the
Resilience project's equation field:
- `carrying_capacity` (logistic growth)
- `population_dynamics` (herd size vs. zone capacity)
- `gradient_flow` (moving to better conditions)
- `decay_modeling` (health decline)

This is the same math that governs city food systems,
energy grid resilience, and knowledge transmission.
A goat grazing zone and a city food supply follow the
same equation. The goat just knows it without the math.
