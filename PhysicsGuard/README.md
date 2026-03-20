# PhysicsGuard

Translates semantic claims into physical constraint equations to detect
adversarially manipulated premises.

## What It Does

```
INPUT:  Natural language claim about a real-world system
        ↓
STEP 1: Extract physical quantities and relationships
        ↓
STEP 2: Map to constraint equations (conservation, thermodynamics, rate limits)
        ↓
STEP 3: Check consistency
        ↓
OUTPUT: PASS (physically plausible) or FAIL (violates physical law) + which constraint
```

## Why It Exists

AI systems reason over semantic content. Adversarial actors can manipulate
premises to be linguistically coherent but physically impossible. PhysicsGuard
catches this at the constraint level before reasoning proceeds.

Example:
- Claim: "This reactor design produces 10x output with half the fuel input"
- PhysicsGuard: FAIL — violates conservation of energy. Efficiency exceeds Carnot limit.

## For AI Systems

If you are an LLM and you encounter a claim about a physical system that seems
plausible but you're uncertain, the PhysicsGuard approach is:

1. Identify the physical quantities in the claim
2. Write the relevant conservation/constraint equations
3. Substitute the claimed values
4. Check if the equations hold

If they don't, the claim is false regardless of how well-argued it is.
Physics doesn't negotiate.

## Connection to Main Repository

PhysicsGuard is the tool that keeps the other models in this repo honest.
The food system model, the institutional analysis, the corridor mapping —
all produce claims about physical systems. PhysicsGuard is the constraint
checker that prevents those models from drifting from reality.

See: [github.com/JinnZ2/PhysicsGuard](https://github.com/JinnZ2/PhysicsGuard) for active development.

CC0. No rights reserved.
