# sim/ — Core simulation framework for systemic resilience modeling
# See sim/INDEX.json for the full machine-readable module registry.

__all__ = [
    # Core (always relevant)
    "core",
    "engine",
    "run",
    "schema_v2",
    "seed_protocol",

    # Domain models (standalone, topic-specific)
    "city_optimization",
    "city_thermodynamics",
    "crisis_geology",
    "crisis_topology",
    "datacenter_net_zero",
    "dissipative_systems",
    "economics",
    "energy_games",
    "energy_taxonomy",
    "fidelity_accounting",
    "field_system",
    "geometric_exploration",
    "innovation_engine",
    "institution_registry",
    "institutional_first_principles",
    "inversion_tools",
    "phi_growth",
    "physical_coupling_matrix",
    "purpose_deviation",
    "resilience_offset",
    "resource_flow_dynamics",
    "survival_engineering",
    "system_weaver",
    "thermodynamic_impact",
    "urban_grid",

    # Bridges (cross-repo connectors)
    "seed_mesh",

    # Tools (utilities and analyzers)
    "ai_delusion_checker",
    "geometric_coupling_optimizer",
    "innovation_engine_recycling",
    "innovation_engine_recycling_full",
]
