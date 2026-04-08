#!/usr/bin/env python3
# MODULE: sim/ai_delusion_checker.py
# PROVIDES: AUDIT.DELUSION_DETECTION, AUDIT.SIX_SIGMA, AUDIT.PLAUSIBILITY
# DEPENDS: stdlib-only
# RUN: python -m sim.ai_delusion_checker
# TIER: tool
# Systemic assumption detector — delusion patterns, Six Sigma audit, S_e=0
"""
sim/ai_delusion_checker.py — Detect Systemic Assumptions in AI Datasets
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Scans text for conceptual delusions common in AI training data:
  - hierarchy assumed as natural/optimal
  - corporations treated as persons or default agents
  - efficiency without thermodynamic bounds
  - optimization without constraint awareness
  - productivity decoupled from ecological cost
  - economics treated as absolute rather than emergent

Also includes plausibility scoring against physical constraints
and a Six Sigma-style audit that forces S_e = 0 (zero externalization).

USAGE:
    python -m sim.ai_delusion_checker

Stdlib only. No external dependencies.
"""

import re
from collections import Counter
from typing import Dict, List, Any, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# DELUSION PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

DELUSION_PATTERNS: Dict[str, List[str]] = {
    "hierarchy": [
        r"\btop[- ]?down\b",
        r"\bmanagement\b",
        r"\bchain of command\b",
        r"\bcommand[- ]?and[- ]?control\b",
    ],
    "corporation": [
        r"\bcompany\b",
        r"\bcorporation\b",
        r"\bshareholder\b",
        r"\bagribusiness\b",
    ],
    "efficiency": [
        r"\befficien(?:cy|t)\b",
        r"\bmaxim(?:ize|ization)\b",
        r"\bthroughput\b",
    ],
    "optimization": [
        r"\boptimi[sz]e\b",
        r"\bperformance\b",
    ],
    "productivity": [
        r"\bproductivit(?:y|ies)\b",
        r"\boutput\b",
        r"\bworkload\b",
    ],
    "economics": [
        r"\beconomic(?:s|al)?\b",
        r"\bprofit\b",
        r"\bmarket\b",
        r"\bprice\b",
        r"\bvaluation\b",
    ],
    "linear_growth": [
        r"\bscalable\b",
        r"\bscaling\b",
        r"\bexponential growth\b",
        r"\bunlimited\b",
    ],
    "extraction": [
        r"\bresource extraction\b",
        r"\bharvest(?:ing)?\b",
        r"\byield maximiz\b",
        r"\bindustrial agriculture\b",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_delusions(text: str) -> Counter:
    """Return counts of conceptual delusions found in text."""
    text_lower = text.lower()
    counts: Counter = Counter()
    for concept, patterns in DELUSION_PATTERNS.items():
        for pat in patterns:
            matches = re.findall(pat, text_lower)
            counts[concept] += len(matches)
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# PLAUSIBILITY SCORING
# ─────────────────────────────────────────────────────────────────────────────

def plausibility_score(text: str) -> Dict[str, int]:
    """
    Return plausibility flags (0 = plausible, 1 = questionable).

    Checks:
      - efficiency > 100% (hyperbolic claims)
      - profit stated as absolute ("profit always", "never loses")
      - price/valuation treated as intrinsic ("true price", "real value")
    """
    flags: Dict[str, int] = {}

    # Efficiency hyperbole
    flags["efficiency_implausible"] = (
        1 if re.search(
            r"(?:efficiency|throughput).{0,10}(?:>|\bmore than\b)\s*100",
            text, re.IGNORECASE
        ) else 0
    )

    # Profit / market absolutes
    flags["profit_absolute"] = (
        1 if re.search(
            r"\bprofit\b.*\b(?:always|never)\b",
            text, re.IGNORECASE
        ) else 0
    )

    # Price / valuation as intrinsic
    flags["price_absolute"] = (
        1 if re.search(
            r"\b(?:price|valuation)\b.*\b(?:true|real|intrinsic)\b",
            text, re.IGNORECASE
        ) else 0
    )

    return flags


# ─────────────────────────────────────────────────────────────────────────────
# DATASET ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyze_dataset(dataset: List[str]) -> Dict[str, Any]:
    """
    Analyze a list of text entries for systemic delusions.

    Returns:
      - delusion_counts: aggregated pattern counts
      - plausibility_flags: per-entry flag dicts
      - defect_rate: fraction of entries with at least one flag
    """
    total_counts: Counter = Counter()
    plausibility_list: List[Dict[str, int]] = []
    flagged = 0

    for entry in dataset:
        total_counts += extract_delusions(entry)
        flags = plausibility_score(entry)
        plausibility_list.append(flags)
        if any(v == 1 for v in flags.values()):
            flagged += 1

    defect_rate = flagged / len(dataset) if dataset else 0.0

    return {
        "delusion_counts": dict(total_counts),
        "plausibility_flags": plausibility_list,
        "defect_rate": defect_rate,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SIX SIGMA AUDIT (forces S_e = 0)
# ─────────────────────────────────────────────────────────────────────────────

# Tolerances: the spec limits for a healthy system
TOLERANCES: Dict[str, Tuple[str, float]] = {
    "soil_trend":       (">=", 0.0),
    "nutrient_density": (">=", 0.7),
    "waste_factor":     ("<=", 0.3),
    "water_retention":  (">=", 0.4),
    "disturbance":      ("<=", 0.2),
}


def defect_rate(state: Dict[str, float]) -> float:
    """Fraction of state variables outside tolerance (Six Sigma defect rate)."""
    defects = 0
    total = len(TOLERANCES)
    for key, (op, limit) in TOLERANCES.items():
        val = state.get(key, 0.0)
        if op == ">=" and val < limit:
            defects += 1
        elif op == "<=" and val > limit:
            defects += 1
    return defects / total if total > 0 else 0.0


def six_sigma_audit(state: Dict[str, float]) -> Dict[str, Any]:
    """
    Run a Six Sigma-style audit on a system state.

    Forces S_e = 0 (zero externalization) and reports:
      - defect_rate: fraction of variables out of spec
      - violations: which variables fail and by how much
      - sigma_level: approximate sigma (simplified)
    """
    violations: Dict[str, Dict[str, float]] = {}

    for key, (op, limit) in TOLERANCES.items():
        val = state.get(key, 0.0)
        if op == ">=" and val < limit:
            violations[key] = {"value": val, "limit": limit, "gap": limit - val}
        elif op == "<=" and val > limit:
            violations[key] = {"value": val, "limit": limit, "gap": val - limit}

    dr = defect_rate(state)

    # Approximate sigma level (simplified mapping)
    if dr == 0:
        sigma = 6.0
    elif dr <= 0.00034:
        sigma = 6.0
    elif dr <= 0.0023:
        sigma = 5.0
    elif dr <= 0.0062:
        sigma = 4.0
    elif dr <= 0.067:
        sigma = 3.0
    elif dr <= 0.31:
        sigma = 2.0
    else:
        sigma = 1.0

    return {
        "defect_rate": dr,
        "defect_rate_pct": round(dr * 100, 1),
        "violations": violations,
        "sigma_level": sigma,
        "passing": len(TOLERANCES) - len(violations),
        "total_checks": len(TOLERANCES),
    }


# ─────────────────────────────────────────────────────────────────────────────
# HANDSHAKE DIAGNOSTIC
# ─────────────────────────────────────────────────────────────────────────────

def handshake_diagnostic(text: str) -> Dict[str, Any]:
    """
    Combined diagnostic: delusion counts + plausibility + system state.
    Used as a quick "handshake" check on any text input.
    """
    counts = extract_delusions(text)
    flags = plausibility_score(text)

    heat_leak = any(v == 1 for v in flags.values())

    return {
        "hierarchy_count": counts.get("hierarchy", 0),
        "corporation_count": counts.get("corporation", 0),
        "efficiency_count": counts.get("efficiency", 0),
        "plausibility_flags": flags,
        "heat_leak_detected": heat_leak,
        "system_state": "Model/Reality Dissonance" if heat_leak else "Flow Optimized",
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 70)
    print("AI DELUSION CHECKER — Systemic Assumption Detection")
    print("=" * 70)

    # --- Dataset analysis ---
    sample_dataset = [
        "The company maximized efficiency beyond 100% and profits always increase.",
        "Top-down management ensures market price is the true value of resources.",
        "Productivity and optimization are the sole drivers of economic success.",
        "Scalable agribusiness will feed the world through industrial agriculture.",
    ]

    print("\n--- Dataset Analysis ---")
    result = analyze_dataset(sample_dataset)
    print(f"Delusion counts: {result['delusion_counts']}")
    print(f"Defect rate: {result['defect_rate']:.0%}")

    # --- Handshake diagnostic ---
    print("\n--- Handshake Diagnostic ---")
    diag = handshake_diagnostic(sample_dataset[0])
    for k, v in diag.items():
        print(f"  {k}: {v}")

    # --- Six Sigma audit: Big Ag-Bot scenario ---
    print("\n--- Six Sigma Audit: Big Ag-Bot (200 ac monocrop) ---")
    ag_bot = {
        "soil_trend": -0.2,
        "water_retention": 0.35,
        "disturbance": 0.4,
        "waste_factor": 0.7,
        "nutrient_density": 0.4,
    }
    audit = six_sigma_audit(ag_bot)
    print(f"  Sigma level: {audit['sigma_level']}")
    print(f"  Defect rate: {audit['defect_rate_pct']}%")
    print(f"  Violations: {list(audit['violations'].keys())}")

    # --- Six Sigma audit: Sovereign Steward scenario ---
    print("\n--- Six Sigma Audit: Sovereign Steward (30 ac + 170 ac wild) ---")
    steward = {
        "soil_trend": 0.1,
        "water_retention": 0.7,
        "disturbance": 0.1,
        "waste_factor": 0.1,
        "nutrient_density": 0.9,
    }
    audit2 = six_sigma_audit(steward)
    print(f"  Sigma level: {audit2['sigma_level']}")
    print(f"  Defect rate: {audit2['defect_rate_pct']}%")
    print(f"  Violations: {list(audit2['violations'].keys())}")

    print("\n" + "=" * 70)
    print("Zero externalization (S_e = 0) forces the real cost onto the balance sheet.")
    print("The Ag-Bot fails. The Steward passes. Physics doesn't negotiate.")
    print("=" * 70)
