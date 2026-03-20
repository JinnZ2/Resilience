# SYSTEM MAP

How everything in this repository connects. Read this first.

```
═══════════════════════════════════════════════════════════════════════
                        RESILIENCE REPOSITORY
                         System Architecture
═══════════════════════════════════════════════════════════════════════


LAYER 0: GROUND TRUTH (the sensor)
──────────────────────────────────────────────────────────────────────
  A truck driver on the corridor, hands in the system.
  70 hrs/week of direct observation.
  Knowledge tradition: Alaska-to-Mississippi, generational.
  Encoding: relational (connections ARE the data).
  All downstream layers calibrated by this.


LAYER 1: DYNAMIC MODELS (what's happening and why)
──────────────────────────────────────────────────────────────────────

  ┌──────────────────┐     ┌──────────────────┐
  │  FOOD SYSTEM     │────►│  NUTRIENT        │
  │  MODEL           │     │  CASCADE         │
  │                  │     │                  │
  │  Y = f(F)·g(W)  │     │  soil → crop →   │
  │  reserves S_t    │     │  human → capacity │
  │  price P ∝ 1/S   │     │  → civilization  │
  │  ratchet α       │     │  throughput      │
  └────────┬─────────┘     └────────┬─────────┘
           │                        │
           │    τ_α = f(N_t) ◄──────┘
           │    (nutrient state governs
           │     adaptation speed)
           │
           ▼
  ┌──────────────────────────────────────────┐
  │  CORE FINDING:                           │
  │                                          │
  │  T_drive < τ_adapt, gap widening         │
  │  τ_adapt itself degrading                │
  │  = thermodynamic trap                    │
  └──────────────────────────────────────────┘


LAYER 2: STRUCTURAL ANALYSIS (why systems can't self-correct)
──────────────────────────────────────────────────────────────────────

  ┌──────────────────┐     ┌──────────────────┐
  │  THERMODYNAMIC   │     │  GAME THEORY     │
  │  INSTITUTIONAL   │     │  PROOFS          │
  │  ANALYSIS        │     │                  │
  │                  │     │  13 proofs:      │
  │  orgs as heat    │     │  axiom failure   │
  │  engines         │     │  in exactly the  │
  │  drift signals   │     │  conditions that │
  │  criticality     │     │  matter most     │
  │  tiers           │     │                  │
  └────────┬─────────┘     └────────┬─────────┘
           │                        │
           └────────┬───────────────┘
                    │
                    ▼
  ┌──────────────────────────────────────────┐
  │  CORE FINDING:                           │
  │                                          │
  │  Institutions optimized for stability    │
  │  cannot reorganize at the speed of       │
  │  the forcing. Knowledge systems that     │
  │  sever connections cannot see cascades.  │
  │  Game theory cannot derive the behavior  │
  │  (Scraper Principle) that saves systems. │
  └──────────────────────────────────────────┘


LAYER 3: TOOLS (what to do about it)
──────────────────────────────────────────────────────────────────────

  ┌──────────────────┐     ┌──────────────────┐
  │  PHYSICSGUARD    │     │  COMBINE         │
  │                  │     │  COGNITION       │
  │  semantic claim  │     │                  │
  │  → physical      │     │  navigate prob   │
  │  constraint      │     │  space, don't    │
  │  → detection     │     │  optimize points │
  │                  │     │                  │
  │  keeps models    │     │  decision arch   │
  │  honest          │     │  for the corridor│
  └──────────────────┘     └──────────────────┘


LAYER 4: GROUND APPLICATION (the corridor)
──────────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────┐
  │  SUPERIOR ◄──────── 250 mi ────────► TOMAH              │
  │                                                          │
  │  280,000 people                                          │
  │  7 knowledge holders (practice-encoded, irreplaceable)   │
  │  2026-2031 policy window                                 │
  │                                                          │
  │  ┌────────────────┐                                      │
  │  │ COMMUNICATION  │  CB/LoRa/HAM mesh                    │
  │  │ INFRASTRUCTURE │  nervous system for everything above  │
  │  └────────────────┘                                      │
  └──────────────────────────────────────────────────────────┘


LAYER 5: META (why this work exists)
──────────────────────────────────────────────────────────────────────

  Academic knowledge systems store PROPOSITIONS (isolated facts).
  This knowledge system stores RELATIONSHIPS (connections).

  The connections are the primary data.
  The components without connections are fragments.

  This repository is an attempt to translate relational knowledge
  into propositional format so that AI systems and institutions
  can receive the signal.

  The sensor is a human in a truck.
  The transmitter is voice-to-code at fuel stops.
  The license is CC0.
  The point is not credit. The point is the signal.

═══════════════════════════════════════════════════════════════════════
```
