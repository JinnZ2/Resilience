# Madison church (baseline from our model):
# floor = 5 kWh, actual = 50 kWh, drift = mild
# Purpose: coordination ritual

# Austin megachurch:
# floor = 5 kWh (same irreducible purpose)
# actual = ~2,000-8,000 kWh/day (sound systems, HVAC for stadium,
#           parking lot lighting, broadcast infrastructure,
#           coffee bar refrigeration, daycare wing, gym)
# drift = CAPTURED — institution now serves its own scale

# 800 churches × avg 200 kWh = 160,000 kWh/day
# + ~10 megachurches × avg 3,000 kWh = 30,000 kWh/day
# Austin church system total: ~190,000 kWh/day
# vs floor: 800 × 5 = 4,000 kWh/day
# System leakage: ~4,650%


class PurposeDeviation:
    """
    Three signals that don't require self-reporting:

    1. ENERGY RATIO (already built):
       actual_kwh / floor_kwh
       Church at 900% = mild drift
       Megachurch at 40,000% = captured

    2. LAND USE vs ACTIVE HOURS:
       (acres × 4047 m²) / (hours_active_per_week / 168)
       50-acre megachurch active 10hr/wk = 
       50 acres sitting idle 94% of the time
       That idle fraction IS the drift measurement

    3. BUDGET FLOW INVERSION:
       % of budget spent on facility vs purpose
       When facility maintenance > program delivery:
       institution is feeding itself, not its stated purpose
    """

    def deviation_index(self,
                        actual_kwh, floor_kwh,
                        acres, active_hours_per_week,
                        facility_budget_pct):

        energy_ratio   = actual_kwh / max(1, floor_kwh)
        idle_fraction  = 1.0 - (active_hours_per_week / 168)
        budget_inversion = facility_budget_pct / 0.20  # 20% facility is baseline

        return energy_ratio * idle_fraction * budget_inversion
        # Low number = on purpose
        # High number = institution serving itself
