#!/usr/bin/env python3
# MODULE: sim/cities/madison_wi.py
# PROVIDES: build_madison
# DEPENDS: sim.core
# RUN: —
# TIER: demo
# Madison WI city model — build_madison() with real infrastructure data
"""
sim/cities/madison_wi.py — first populated city
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Data sources: on-route observation (Kavik, 2024-2026),
UW-Madison public records, MMSD infrastructure reports,
Perplexity independent validation (March 2026).

Empty slots marked: # [POPULATE] — add real data when available.
"""

from sim.core import *

def build_madison() -> CityNode:
    city = CityNode(
        name="Madison_WI",
        population=269_000,
        density=DensityType.URBAN,
        area_sq_miles=77.0,
        season=Season.WINTER,
    )

    # ── LAYER ZERO: THREE ZONES ──────────────────────────────────────────────

    inner_city = ResilienceFoundation(
        zone="inner_city",
        zone_type=ZoneType.INNER_CITY,
        population=40_000,
        social_trust_index=0.75,
        mutual_aid_networks_active=True,
        mutual_aid_network_names=["neighborhood_mutual_aid","faith_networks"],
        knowledge_holders_present=True,
        knowledge_holders_mobile=True,
        knowledge_domains=["medical_triage","food_distribution","building_access"],
        cognition=CognitiveReadinessLayer(
            zone="inner_city",
            constraint_gradient=0.70,
            failure_mode_scanning=0.65,
            abundance_assumption=0.25,
            institutional_mediation_default=0.35,
            adaptation_hours_low=4,
            adaptation_hours_high=12,
        ),
        social_trust=SocialTrustLayer(
            zone="inner_city",
            gratitude_network_active=True,
            obligation_type="gratitude",
            money_penetration=0.40,
            # absentee ownership injects transaction logic
            # into otherwise-functional gratitude network
            mirror_neuron_triggers=[
                "witnessed_need","shared_hardship","kinship","place_attachment"
            ],
        ),
        decision_authority=DecisionAuthorityNode(
            zone="inner_city",
            owner_resident_same=False,
            decision_maker_present_in_crisis=False,
            absentee_ownership_percent=0.70,
            corporate_ownership_percent=0.40,
            community_council_exists=True,
            crisis_decision_protocol="community",
            estimated_decision_lag_hours=4.0,
            community_override_likely=True,
            post_crisis_legal_risk="moderate",
        ),
    )

    suburban = ResilienceFoundation(
        zone="suburban_sprawl",
        zone_type=ZoneType.SUBURBAN,
        population=160_000,
        social_trust_index=0.25,
        mutual_aid_networks_active=False,
        mutual_aid_network_names=[],
        knowledge_holders_present=False,
        knowledge_holders_mobile=False,
        knowledge_domains=[],
        cognition=CognitiveReadinessLayer(
            zone="suburban_sprawl",
            constraint_gradient=0.15,
            failure_mode_scanning=0.10,
            abundance_assumption=0.90,
            institutional_mediation_default=0.95,
            adaptation_hours_low=72,
            adaptation_hours_high=720,
            # days to weeks before useful action
        ),
        social_trust=SocialTrustLayer(
            zone="suburban_sprawl",
            gratitude_network_active=False,
            obligation_type="transaction",
            money_penetration=0.90,
            mirror_neuron_triggers=[],
            # triggers present but not practiced
            # church attendance exists but limited to similar demographics
        ),
        decision_authority=DecisionAuthorityNode(
            zone="suburban_sprawl",
            owner_resident_same=False,
            decision_maker_present_in_crisis=False,
            absentee_ownership_percent=0.55,
            corporate_ownership_percent=0.50,
            community_council_exists=False,
            crisis_decision_protocol="none",
            estimated_decision_lag_hours=36.0,
            community_override_likely=False,
            post_crisis_legal_risk="high",
        ),
    )

    rural_fringe = ResilienceFoundation(
        zone="rural_fringe",
        zone_type=ZoneType.RURAL_FRINGE,
        population=25_000,
        social_trust_index=0.85,
        mutual_aid_networks_active=True,
        mutual_aid_network_names=[
            "farm_networks","volunteer_fire","church_networks","equipment_sharing"
        ],
        knowledge_holders_present=True,
        knowledge_holders_mobile=True,
        knowledge_domains=[
            "water_systems","food_preservation","equipment_repair",
            "medical_triage","animal_husbandry","fuel_management",
            "ice_navigation","oral_weather_prediction",
        ],
        cognition=CognitiveReadinessLayer(
            zone="rural_fringe",
            constraint_gradient=0.85,
            failure_mode_scanning=0.85,
            abundance_assumption=0.10,
            institutional_mediation_default=0.15,
            adaptation_hours_low=2,
            adaptation_hours_high=6,
        ),
        social_trust=SocialTrustLayer(
            zone="rural_fringe",
            gratitude_network_active=True,
            obligation_type="gratitude",
            money_penetration=0.20,
            mirror_neuron_triggers=[
                "witnessed_need","shared_hardship","kinship",
                "place_attachment","professional_identity",
            ],
        ),
        decision_authority=DecisionAuthorityNode(
            zone="rural_fringe",
            owner_resident_same=True,
            decision_maker_present_in_crisis=True,
            absentee_ownership_percent=0.10,
            corporate_ownership_percent=0.05,
            community_council_exists=True,
            crisis_decision_protocol="community",
            estimated_decision_lag_hours=1.0,
            community_override_likely=True,
            post_crisis_legal_risk="low",
        ),
    )

    city.zones = [inner_city, suburban, rural_fringe]

    # ── INSTITUTIONAL ASSETS ─────────────────────────────────────────────────

    city.assets = InstitutionalAssets(
        colleges=[
            CollegeNode(
                name="UW_Madison",
                enrollment=47_000,
                departments=[
                    "engineering","nursing","agriculture","chemistry",
                    "medicine","veterinary","environmental_science"
                ],
                labs=[
                    LabAsset("chemistry",   potential_functions=["sanitizer","water_treatment","fuel_refining"]),
                    LabAsset("mechanical",  potential_functions=["equipment_repair","fabrication","parts_manufacture"]),
                    LabAsset("biology",     potential_functions=["food_safety_testing","medical_supply"]),
                    LabAsset("agriculture", potential_functions=["food_production","soil_analysis","seed_storage"]),
                ],
                dormitory_capacity=10_000,
                cafeteria_capacity=15_000,
                backup_power=True,
                water_independent=False,
                seasonal_population={
                    "fall":1.0,"spring":0.9,"summer":0.2,"winter":0.85
                },
                community_access_agreement=False,  # GAP — needs negotiation
                supply_stockpile_days=7,
            )
        ],
        hospitals=[
            HospitalNode(
                name="UW_Health",
                bed_capacity=592,
                trauma_capable=True,
                backup_power_hours=72,
                water_independent=False,
                supply_stockpile_days=14,
                surge_capacity_multiplier=1.4,
            )
        ],
        coops=[
            CoopNode(
                name="Willy_Street_Coop",
                type="food",
                member_count=35_000,
                distribution_capacity_day=2_000,
                storage_capacity_days=14,
                production_capable=False,
                cold_storage=True,      # confirmed on-route observation
                backup_power=True,      # confirmed on-route observation
            )
        ],
        industrial=[
            # [POPULATE] Walmart distribution center
            # [POPULATE] Cold storage warehouses on beltline
            # [POPULATE] Industrial nodes east side
        ],
    )

    # ── INFRASTRUCTURE ───────────────────────────────────────────────────────

    city.infrastructure.water = WaterSystem(
        name="madison_municipal_water",
        source="sandstone_aquifer_22_wells",
        backup_source="lakes_mendota_monona_emergency",
        storage_days=2.0,
        redundancy=RedundancyLevel.SINGLE,  # generators confirmed at pump stations
        purification_methods=[
            "groundwater_treatment",
            "emergency_surface_treatment_capable",
        ],
        institutional_backups=["UW_Madison","Willy_Street_Coop"],
        days_to_critical=3,
        days_to_critical_backed=14,
        failure_modes=[
            FailureMode(
                trigger="grid_failure",
                time_to_failure_hours=6,
                cascade_targets=["medical","sewage","fire_suppression"],
                recovery_path=[
                    "activate_pump_station_generators",
                    "fuel_resupply_within_72h",
                    "emergency_lake_intake",
                ],
                knowledge_required=[
                    "generator_maintenance",
                    "emergency_water_treatment",
                    "aquifer_contamination_monitoring",
                ],
            ),
            FailureMode(
                trigger="generator_fuel_depletion",
                time_to_failure_hours=72,
                cascade_targets=["sewage_treatment","hospital","fire"],
                recovery_path=[
                    "fuel_convoy_priority_routing",
                    "manual_distribution_points",
                    "lake_emergency_intake_activation",
                ],
                knowledge_required=[
                    "water_distribution_manual_ops",
                    "emergency_purification",
                ],
            ),
            FailureMode(
                # TAIL RISK — not modeled by standard frameworks
                trigger="sewage_pump_failure",
                time_to_failure_hours=24,
                cascade_targets=["aquifer_recharge_zones"],
                recovery_path=[
                    "emergency_sewage_bypass",
                    "portable_treatment_units",
                ],
                knowledge_required=[
                    "sewage_system_manual_ops",
                    "aquifer_contamination_containment",
                ],
            ),
        ],
        treatment_capacity_gpd=0,  # [POPULATE from MMSD data]
    )

    city.infrastructure.food = FoodSystem(
        name="madison_food",
        local_production_percent=8.0,
        supply_chain_days=3.0,
        cold_storage_capacity_tons=0,  # [POPULATE]
        distribution_nodes=["Willy_Street_Coop","UW_cafeteria_system"],
        growing_season_days=150,
        redundancy=RedundancyLevel.SINGLE,
        institutional_backups=["Willy_Street_Coop","UW_Madison_ag"],
        days_to_critical=3,
        days_to_critical_backed=17,
    )

    city.infrastructure.energy = EnergySystem(
        name="madison_energy",
        grid_dependent_percent=95.0,
        local_generation_mw=0,     # [POPULATE]
        backup_fuel_days=3.0,
        renewable_sources=[],      # [POPULATE]
        redundancy=RedundancyLevel.NONE,
        institutional_backups=["UW_Madison_backup_power"],
        days_to_critical=1,
        days_to_critical_backed=4,
    )

    city.infrastructure.medical = MedicalSystem(
        name="madison_medical",
        beds_per_1000=2.2,
        trauma_centers=1,
        supply_stockpile_days=14,
        community_health_workers=0,  # [POPULATE]
        triage_capable_population_pct=0.02,
        redundancy=RedundancyLevel.SINGLE,
        institutional_backups=["UW_Health","UW_nursing_program"],
        days_to_critical=7,
        days_to_critical_backed=21,
    )

    city.infrastructure.repair = RepairSystem(
        name="madison_repair",
        skilled_trades_per_1000=0,  # [POPULATE]
        tool_library_nodes=2,
        parts_supply_days=7,
        knowledge_transmission_active=False,
        redundancy=RedundancyLevel.NONE,
        institutional_backups=["UW_engineering_shops"],
        days_to_critical=30,
        days_to_critical_backed=90,
    )

    city.infrastructure.comms = CommsSystem(
        name="madison_comms",
        grid_dependent=True,
        ham_operators=0,           # [POPULATE from ARRL data]
        cb_network_active=False,
        lora_mesh_nodes=0,
        backup_comms_range_miles=0,
        redundancy=RedundancyLevel.NONE,
        institutional_backups=[],
        days_to_critical=1,
        days_to_critical_backed=30,
    )

    city.infrastructure.manufacturing = ManufacturingSystem(
        name="madison_manufacturing",
        local_essential_production=["medical_devices"],
        fabrication_capacity="light",
        raw_material_days=14,
        redundancy=RedundancyLevel.NONE,
        institutional_backups=["UW_engineering","UW_chemistry"],
        days_to_critical=60,
        days_to_critical_backed=180,
    )

    return city
