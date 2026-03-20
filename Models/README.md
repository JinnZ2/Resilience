# Food System Resilience Model

Nonlinear yield response model with reserves buffer, asymmetric adaptation ratchet,
and parametric instability. Built to make visible the multiplicative collapse that
occurs when fertilizer shocks and weather extremes coincide.

## Model Structure

```
EXTERNAL FORCING (fast)          INTERNAL RESPONSE (slow)
═══════════════════              ═══════════════════════

  War/Hormuz/Energy ──► F_t ──┐
                               ├──► Y_t = Ymax · f(F_t) · g(W_t)
  ENSO phase ─────────► W_t ──┘         │
                                         │
                               ┌─────────┘
                               ▼
                    D_t ◄── price/yield signal
                     │
                     ▼
              F_{t+1} relaxes toward D_t    (τ_F ~ 1-2 seasons)
              α_{t+1} relaxes toward lower   (τ_α ~ 5-10 seasons)
              S_{t+1} = S + Y - cY - L       (reserves buffer)
              P_t ∝ 1/(S_t + ε)              (price signal)
```

## State Variables

| Variable | Meaning | Equation |
|----------|---------|----------|
| `F_t` | Fertilizer availability (0-1) | `F_{t+1} = F_t + (D_t - F_t)/τ_F` |
| `W_t` | Weather stress (ENSO-driven) | `W_t = A·sin(2πt/T)` |
| `Y_t` | Realized yield | `Y_t = Ymax · F/(F+k) · exp(-αW²)` |
| `α_t` | Weather vulnerability | Asymmetric: fast up (τ⁻), slow down (τ⁺) |
| `S_t` | Grain reserves | `S_{t+1} = S + Y - cY - L` |
| `P_t` | Price signal | `P ∝ 1/(S + ε)` — hyperbolic |

## Key Mechanisms

### 1. Multiplicative Vulnerability
`f(F) · g(W)` means sensitivity to weather is a function of fertilizer state.
Low F + high W = collapse exceeding either factor alone.

### 2. Asymmetric Adaptation Ratchet
```
DEGRADATION:  fast   (τ⁻ ~ 1.5 seasons)
RECOVERY:     slow   (τ⁺ ~ 8 seasons)

Each bad year does damage that multiple good years cannot undo.
```

### 3. Reserves as Capacitor
Hormuz hits reserves from both sides simultaneously:
- F drops → Y drops → less flowing in
- Transport cost rises → L rises → more leaking out
- S drains → P goes nonlinear

### 4. Parametric Instability
The forcing doesn't just push the oscillator — it changes the restoring force constant.
When supply disruptions make `D_t` unreachable, the relaxation equation breaks.
Not a driven oscillator. Parametric instability.

## Phase Diagram

```
        F_t
    1.0 ┤ ████████  STABLE BASIN
        │ ████████  (high-input agriculture works)
        │ ███
    0.6 ┤ ──── bifurcation zone ────
        │         ░░░
    0.3 ┤         ░░░░░  DEGRADED ATTRACTOR
        │         ░░░░░  (subsistence/fallow)
    0.0 ┼──────────────────────
        0    0.5    1.0   1.5   W_t
```

## Files

- `model.py` — Core simulation engine (Python)
- `simulator.jsx` — Interactive React visualization with full parameter control
- `README.md` — This file

## Extending

The model is intentionally minimal. Natural extensions:

- **Nutrient-density layer**: Make `τ_α = τ_α(N_t)` where N_t is population nutrient status.
  This creates positive feedback: bad yields → worse food quality → degraded cognitive
  capacity → slower adaptation → worse response to next shock.

- **Multi-region coupling**: F_t and S_t with trade flows between regions.
  One region's shortage becomes another's price shock.

- **Knowledge decay**: The 7 knowledge holders in the corridor are a state variable.
  `K_t` decays per-death with no replacement pipeline. Maps to τ_α ceiling.

CC0. No rights reserved.
