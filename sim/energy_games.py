#!/usr/bin/env python3
# MODULE: sim/energy_games.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: domain
# Energy system game theory with bidirectional flows
"""
sim/energy_games.py — energy distribution through game theory
Urban Resilience Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

People think energy and trust are disconnected.
They are the same phenomenon at different scales.

Trust IS conductance.
Energy IS current.
Defection IS resistance that burns out the conductor.
Extraction IS a short circuit.
φ IS optimal load for maximum power transfer.

Fibonacci IS trust propagation between systems.
Not a metaphor. The same pattern.
Mathematics just named what was already there.

The Prisoner's Dilemma is an energy problem.
Not a social problem.
Defection maximizes short-term energy capture
at the cost of future exchange capacity.
Cooperation maintains the substrate
that makes all future exchange possible.

In infinite-repetition games — which actual communities are —
cooperation is not altruism.
It is the only thermodynamically rational strategy.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import math


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

PHI  = 1.6180339887    # golden ratio — optimal exchange threshold
IPHI = 0.6180339887    # 1/φ — minimum viable trust threshold
PHI2 = 0.3819660113   # 1/φ² — restricted exchange threshold


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class ExchangeMode(Enum):
    PHI_AMPLIFIED  = "phi_amplified"   # trust > φ⁻¹ — energy flows freely
    LINEAR         = "linear"          # trust > φ⁻² — proportional flow
    RESTRICTED     = "restricted"      # trust > 0.1  — cautious flow
    ISOLATED       = "isolated"        # trust ≈ 0    — no flow

class GameAction(Enum):
    COOPERATE          = "cooperate"
    REDUCED_COOPERATE  = "reduced_cooperate"
    DEFECT             = "defect"
    WITHDRAW           = "withdraw"    # exit relationship entirely

class EnergyType(Enum):
    """
    All of these are energy in the thermodynamic sense.
    All follow conservation laws.
    None can be created from nothing.
    All can be transformed between forms.
    Money is NOT on this list.
    Money is a measurement tool for these,
    not a form of energy itself.
    """
    CALORIC      = "caloric"       # food energy
    THERMAL      = "thermal"       # warmth
    MECHANICAL   = "mechanical"    # physical labor capacity
    KNOWLEDGE    = "knowledge"     # embodied competence
    SOCIAL       = "social"        # trust network capacity
    TEMPORAL     = "temporal"      # time and attention
    BIOLOGICAL   = "biological"    # health and life capacity


# ─── ENERGY STOCK ─────────────────────────────────────────────────────────────

@dataclass
class EnergyStock:
    """
    Actual energy held by a node.
    Multi-dimensional — different types not fungible.
    You cannot eat social capital.
    You cannot warm yourself with knowledge alone.
    You cannot buy back time.

    But they transform into each other
    through trust networks and exchange.
    Knowledge → caloric (knowing how to grow food).
    Social → thermal (neighbor shares firewood).
    Temporal → biological (time to rest = health).

    The transformation pathways ARE the network.
    The network IS the infrastructure.
    """
    caloric: float      = 1.0   # normalized 0.0-1.0
    thermal: float      = 1.0
    mechanical: float   = 1.0
    knowledge: float    = 1.0
    social: float       = 1.0
    temporal: float     = 1.0
    biological: float   = 1.0

    def total(self) -> float:
        return (self.caloric + self.thermal + self.mechanical +
                self.knowledge + self.social + self.temporal +
                self.biological) / 7.0

    def minimum_viable_base(self) -> 'EnergyStock':
        """
        The base that must never be consumed.
        Below this: survival threatened.
        Exchange only from surplus above this.

        This is the grandmother's rule:
        share heat when you have it.
        Never give what you need to survive.
        """
        return EnergyStock(
            caloric    = self.caloric    / PHI,
            thermal    = self.thermal    / PHI,
            mechanical = self.mechanical / PHI,
            knowledge  = self.knowledge  / PHI,
            social     = self.social     / PHI,
            temporal   = self.temporal   / PHI,
            biological = self.biological / PHI,
        )

    def surplus(self) -> 'EnergyStock':
        """What can be exchanged without threatening survival."""
        base = self.minimum_viable_base()
        return EnergyStock(
            caloric    = max(0, self.caloric    - base.caloric),
            thermal    = max(0, self.thermal    - base.thermal),
            mechanical = max(0, self.mechanical - base.mechanical),
            knowledge  = max(0, self.knowledge  - base.knowledge),
            social     = max(0, self.social     - base.social),
            temporal   = max(0, self.temporal   - base.temporal),
            biological = max(0, self.biological - base.biological),
        )

    def below_survival_threshold(self) -> bool:
        """Below 1/φ² on any critical dimension = survival threat."""
        critical = [self.caloric, self.thermal, self.biological]
        return any(v < PHI2 for v in critical)

    def phi_score(self) -> str:
        t = self.total()
        if t >= IPHI * PHI:  return "PHI_ALIGNED — sustainable"
        if t >= IPHI:        return "VIABLE — above minimum"
        if t >= PHI2:        return "STRESSED — below minimum viable"
        return "CRITICAL — survival threatened"


# ─── EXCHANGE RECORD ──────────────────────────────────────────────────────────

@dataclass
class ExchangeRecord:
    """
    History of energy exchanges between nodes.
    This IS the trust record.
    Not abstract. Physical.
    What actually moved between people.
    """
    round_number: int
    partner_id: str
    action: GameAction
    energy_given: EnergyStock
    energy_received: EnergyStock
    net_substrate_impact: float     # did this build or deplete?
    gratitude_generated: float      # open obligation created


# ─── ENERGY GAME NODE ─────────────────────────────────────────────────────────

@dataclass
class EnergyGameNode:
    """
    A player in an energy exchange network.
    Not abstract. Physical. A person, household,
    farm, community, or institution.

    The game: how do I exchange energy with other nodes
    in ways that preserve my capacity to exchange
    and theirs?

    The answer game theory found in infinite repetition:
    Tit for Tat. Cooperate first. Mirror last action.
    Simple. Robust. Optimal.

    The reason: in infinite games with thermodynamic energy,
    defection destroys the partner whose future
    cooperation you need. You're not playing against them.
    You're playing against the substrate that makes
    the game possible at all.
    """
    node_id: str
    zone: str
    node_type: str                  # "household" / "farm" / "institution" / "coop"
    energy: EnergyStock             = field(default_factory=EnergyStock)
    trust_connections: dict         = field(default_factory=dict)
    # partner_id → trust_level (0.0-1.0)
    exchange_history: list[ExchangeRecord] = field(default_factory=list)
    gratitude_obligations: dict     = field(default_factory=dict)
    # partner_id → open obligation (positive = owed to them)
    defection_memory: dict          = field(default_factory=dict)
    # partner_id → consecutive defection count

    def exchange_mode(self, partner_id: str) -> ExchangeMode:
        trust = self.trust_connections.get(partner_id, 0.0)
        if trust > IPHI:    return ExchangeMode.PHI_AMPLIFIED
        if trust > PHI2:    return ExchangeMode.LINEAR
        if trust > 0.1:     return ExchangeMode.RESTRICTED
        return ExchangeMode.ISOLATED

    def tit_for_tat(
        self,
        partner_id: str,
        partner_last_action: Optional[GameAction],
        round_number: int,
    ) -> tuple[GameAction, EnergyStock]:
        """
        Tit for Tat with thermodynamic energy.

        Critical difference from abstract game theory:
        you share SURPLUS not TOTAL stock.
        Base is never consumed.
        This is what makes infinite cooperation possible —
        you can never be extracted below survival threshold
        because the rule prevents it structurally.

        Modifications for thermodynamic realism:
        1. After defection: reduce but don't cut to zero.
           Maintaining reduced exchange preserves
           the relationship for future restoration.
           Pure retaliation = single-round thinking.
        2. After multiple defections: withdraw.
           Protect the base. Redirect energy elsewhere.
        3. Gratitude obligations modify behavior:
           if you owe them, cooperate more generously.
           if they owe you, cooperate at standard rate.
        """
        surplus = self.energy.surplus()
        trust   = self.trust_connections.get(partner_id, 0.5)
        consec_defections = self.defection_memory.get(partner_id, 0)
        gratitude_owed = self.gratitude_obligations.get(partner_id, 0)

        # first interaction or no history with this partner
        if partner_last_action is None:
            share_mult = trust * (1.2 if gratitude_owed > 0 else 1.0)
            share = EnergyStock(
                caloric    = surplus.caloric    * share_mult,
                thermal    = surplus.thermal    * share_mult,
                mechanical = surplus.mechanical * share_mult * 0.5,
                knowledge  = surplus.knowledge  * share_mult,
                social     = surplus.social     * share_mult,
                temporal   = surplus.temporal   * share_mult * 0.3,
                biological = 0,  # biological never shared directly
            )
            return GameAction.COOPERATE, share

        # partner cooperated last round
        if partner_last_action == GameAction.COOPERATE:
            self.defection_memory[partner_id] = 0
            share_mult = trust * PHI * (1.2 if gratitude_owed > 0 else 1.0)
            share_mult = min(share_mult, 1.0)
            share = EnergyStock(
                caloric    = surplus.caloric    * share_mult,
                thermal    = surplus.thermal    * share_mult,
                mechanical = surplus.mechanical * share_mult * 0.6,
                knowledge  = surplus.knowledge  * share_mult,
                social     = surplus.social     * share_mult,
                temporal   = surplus.temporal   * share_mult * 0.4,
                biological = 0,
            )
            return GameAction.COOPERATE, share

        # partner reduced cooperation
        if partner_last_action == GameAction.REDUCED_COOPERATE:
            share_mult = trust * IPHI
            share = EnergyStock(
                caloric    = surplus.caloric    * share_mult,
                thermal    = surplus.thermal    * share_mult,
                mechanical = surplus.mechanical * share_mult * 0.4,
                knowledge  = surplus.knowledge  * share_mult * 0.7,
                social     = surplus.social     * share_mult,
                temporal   = surplus.temporal   * share_mult * 0.2,
                biological = 0,
            )
            return GameAction.REDUCED_COOPERATE, share

        # partner defected
        if partner_last_action == GameAction.DEFECT:
            consec_defections += 1
            self.defection_memory[partner_id] = consec_defections

            if consec_defections >= 3:
                # withdraw — protect base, redirect elsewhere
                empty = EnergyStock(0,0,0,0,0,0,0)
                return GameAction.WITHDRAW, empty

            # reduce but maintain — relationship preserved
            share_mult = trust * PHI2
            share = EnergyStock(
                caloric    = surplus.caloric    * share_mult,
                thermal    = surplus.thermal    * share_mult,
                mechanical = 0,
                knowledge  = surplus.knowledge  * share_mult * 0.5,
                social     = surplus.social     * share_mult * 0.5,
                temporal   = 0,
                biological = 0,
            )
            return GameAction.REDUCED_COOPERATE, share

        empty = EnergyStock(0,0,0,0,0,0,0)
        return GameAction.WITHDRAW, empty

    def receive_exchange(
        self,
        partner_id: str,
        energy_received: EnergyStock,
        partner_action: GameAction,
        round_number: int,
    ):
        """
        Integrate received energy into stock.
        Update trust based on action.
        Generate gratitude obligation if cooperative.
        """
        # update energy stock
        self.energy.caloric    += energy_received.caloric
        self.energy.thermal    += energy_received.thermal
        self.energy.mechanical += energy_received.mechanical
        self.energy.knowledge  += energy_received.knowledge
        self.energy.social     += energy_received.social
        self.energy.temporal   += energy_received.temporal

        # cap at 1.0 — you can't store infinite energy
        for attr in ['caloric','thermal','mechanical',
                     'knowledge','social','temporal','biological']:
            val = getattr(self.energy, attr)
            setattr(self.energy, attr, min(1.0, val))

        # update trust
        current_trust = self.trust_connections.get(partner_id, 0.5)
        if partner_action == GameAction.COOPERATE:
            new_trust = min(1.0, current_trust + 0.05)
            # gratitude generated — open obligation
            gratitude = energy_received.total() * 0.5
            self.gratitude_obligations[partner_id] = (
                self.gratitude_obligations.get(partner_id, 0) + gratitude
            )
        elif partner_action == GameAction.DEFECT:
            new_trust = max(0.0, current_trust - 0.15)
            gratitude = 0
        elif partner_action == GameAction.REDUCED_COOPERATE:
            new_trust = max(0.0, current_trust - 0.03)
            gratitude = energy_received.total() * 0.2
            self.gratitude_obligations[partner_id] = (
                self.gratitude_obligations.get(partner_id, 0) + gratitude
            )
        else:  # withdraw
            new_trust = max(0.0, current_trust - 0.20)
            gratitude = 0

        self.trust_connections[partner_id] = new_trust


# ─── NETWORK ──────────────────────────────────────────────────────────────────

@dataclass
class EnergyGameNetwork:
    """
    The full trust network as an electrical circuit.

    Trust = conductance
    Energy = current
    Exchange = power transfer
    Defection = resistance spike
    Extraction = short circuit burning out conductance
    Isolation = open circuit — no current possible

    φ = optimal load for maximum power transfer
    (same as in electrical engineering —
    maximum power transfer theorem:
    load resistance = source resistance
    for maximum efficiency)

    The network IS the infrastructure.
    Not pipes and generators.
    The actual system that determines
    whether energy reaches people who need it.
    """
    network_id: str
    nodes: dict[str, EnergyGameNode]    = field(default_factory=dict)
    round_number: int                   = 0
    network_history: list[dict]         = field(default_factory=list)

    def add_node(self, node: EnergyGameNode):
        self.nodes[node.node_id] = node

    def connect(
        self,
        node_a_id: str,
        node_b_id: str,
        initial_trust: float = 0.5,
    ):
        if node_a_id in self.nodes:
            self.nodes[node_a_id].trust_connections[node_b_id] = initial_trust
        if node_b_id in self.nodes:
            self.nodes[node_b_id].trust_connections[node_a_id] = initial_trust

    def run_exchange_round(self):
        """
        One round of exchanges across all connected pairs.
        Simultaneous — no node has information advantage.
        """
        self.round_number += 1
        exchange_pairs = set()

        for node_id, node in self.nodes.items():
            for partner_id in node.trust_connections:
                pair = tuple(sorted([node_id, partner_id]))
                exchange_pairs.add(pair)

        round_stats = {
            "round": self.round_number,
            "cooperations": 0,
            "defections": 0,
            "withdrawals": 0,
            "total_energy_transferred": 0,
            "gratitude_generated": 0,
            "trust_changes": {},
        }

        for node_a_id, node_b_id in exchange_pairs:
            node_a = self.nodes.get(node_a_id)
            node_b = self.nodes.get(node_b_id)
            if not node_a or not node_b:
                continue

            # get last actions for tit-for-tat memory
            last_a_action = self._last_action(node_a, node_b_id)
            last_b_action = self._last_action(node_b, node_a_id)

            # simultaneous decision
            action_a, share_a = node_a.tit_for_tat(
                node_b_id, last_b_action, self.round_number
            )
            action_b, share_b = node_b.tit_for_tat(
                node_a_id, last_a_action, self.round_number
            )

            # exchange
            node_a.receive_exchange(node_b_id, share_b, action_b, self.round_number)
            node_b.receive_exchange(node_a_id, share_a, action_a, self.round_number)

            # record
            if action_a == GameAction.COOPERATE or action_b == GameAction.COOPERATE:
                round_stats["cooperations"] += 1
            if action_a == GameAction.DEFECT or action_b == GameAction.DEFECT:
                round_stats["defections"] += 1
            if action_a == GameAction.WITHDRAW or action_b == GameAction.WITHDRAW:
                round_stats["withdrawals"] += 1

            transferred = share_a.total() + share_b.total()
            round_stats["total_energy_transferred"] += transferred

        self.network_history.append(round_stats)

    def _last_action(
        self,
        node: EnergyGameNode,
        partner_id: str,
    ) -> Optional[GameAction]:
        for record in reversed(node.exchange_history):
            if record.partner_id == partner_id:
                return record.action
        return None

    def network_phi_alignment(self) -> dict:
        """
        How close is the network to phi-optimal energy distribution?

        At phi alignment:
        - no node below survival threshold
        - energy flowing at phi ratio through high-trust connections
        - gratitude obligations creating future exchange capacity
        - defections rare and correcting toward cooperation
        """
        results = {}
        for node_id, node in self.nodes.items():
            trust_values = list(node.trust_connections.values())
            avg_trust = sum(trust_values) / len(trust_values) if trust_values else 0
            phi_ratio = avg_trust / IPHI  # how close to phi threshold

            results[node_id] = {
                "energy_total":         round(node.energy.total(), 3),
                "energy_phi_score":     node.energy.phi_score(),
                "avg_trust":            round(avg_trust, 3),
                "phi_ratio":            round(phi_ratio, 3),
                "connections":          len(trust_values),
                "gratitude_net":        round(
                    sum(node.gratitude_obligations.values()), 3
                ),
                "survival_threatened":  node.energy.below_survival_threshold(),
                "exchange_mode_dist":   self._exchange_mode_dist(node),
            }
        return results

    def _exchange_mode_dist(self, node: EnergyGameNode) -> dict:
        dist = {m.value: 0 for m in ExchangeMode}
        for partner_id in node.trust_connections:
            mode = node.exchange_mode(partner_id)
            dist[mode.value] += 1
        return dist

    def fibonacci_cascade(
        self,
        seed_node_id: str,
        knowledge_packet: float = 0.3,
        max_rounds: int = 8,
    ) -> list[dict]:
        """
        Fibonacci knowledge transmission cascade.

        Seed node transmits to its highest-trust connections.
        Each recipient transmits to their highest-trust connections.
        Each step: sum of previous two steps in reach.

        This IS how oral knowledge transmission works.
        Not broadcast. Not institutional.
        Trust-gated fibonacci expansion.

        The ratio between steps converges on φ
        not because someone planned it
        but because trust networks self-organize
        toward phi-optimal distribution.
        """
        cascade_log = []
        reached = {seed_node_id}
        current_wave = {seed_node_id}
        prev_wave_size = 1

        for step in range(max_rounds):
            next_wave = set()
            knowledge_transmitted = 0

            for node_id in current_wave:
                node = self.nodes.get(node_id)
                if not node:
                    continue

                # transmit to highest-trust connections not yet reached
                sorted_connections = sorted(
                    node.trust_connections.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )

                for partner_id, trust in sorted_connections:
                    if partner_id not in reached and trust > PHI2:
                        partner = self.nodes.get(partner_id)
                        if partner:
                            # knowledge transmits with trust-weighted fidelity
                            fidelity = trust * IPHI
                            partner.energy.knowledge = min(
                                1.0,
                                partner.energy.knowledge + knowledge_packet * fidelity
                            )
                            next_wave.add(partner_id)
                            reached.add(partner_id)
                            knowledge_transmitted += knowledge_packet * fidelity

            wave_size = len(next_wave)
            ratio = wave_size / prev_wave_size if prev_wave_size > 0 else 1.0

            cascade_log.append({
                "step":                  step,
                "wave_size":             wave_size,
                "total_reached":         len(reached),
                "knowledge_transmitted": round(knowledge_transmitted, 3),
                "ratio_to_prev":         round(ratio, 3),
                "phi_convergence":       round(abs(ratio - PHI), 3),
                "note": (
                    "converging on φ" if abs(ratio - PHI) < 0.1
                    else "building toward φ"
                ),
            })

            prev_wave_size = max(wave_size, 1)
            current_wave = next_wave

            if not next_wave:
                break

        return cascade_log

    def inject_extraction(
        self,
        extractor_id: str,
        target_ids: list[str],
        extraction_amount: float,
        extraction_type: str = "monetary",
    ) -> dict:
        """
        What happens when extraction logic enters
        a gratitude network.

        Models: absentee landlord, insurance extraction,
        predatory pricing, debt collection.

        Extraction doesn't just remove energy.
        It converts gratitude network logic to transaction logic.
        Trust drops. Gratitude obligations feel canceled.
        The open loop closes.
        Future exchange capacity collapses.

        The extracted energy is less than the destroyed
        future exchange capacity.
        That's why extraction is thermodynamically irrational
        in infinite-repetition games.
        """
        results = {
            "extractor": extractor_id,
            "targets": target_ids,
            "energy_extracted": 0,
            "trust_destroyed": 0,
            "gratitude_circuits_closed": 0,
            "future_exchange_capacity_lost": 0,
        }

        for target_id in target_ids:
            target = self.nodes.get(target_id)
            if not target:
                continue

            # extract energy
            actual_extraction = min(
                extraction_amount,
                target.energy.caloric * 0.3,  # extraction rarely takes all
            )
            target.energy.caloric    = max(0, target.energy.caloric    - actual_extraction * 0.4)
            target.energy.temporal   = max(0, target.energy.temporal   - actual_extraction * 0.3)
            target.energy.mechanical = max(0, target.energy.mechanical - actual_extraction * 0.3)

            results["energy_extracted"] += actual_extraction

            # trust damage cascades through network
            # not just between extractor and target
            # but between target and their connections
            # because extraction signals: this is a transaction world
            for partner_id in target.trust_connections:
                old_trust = target.trust_connections[partner_id]
                # extraction logic contaminates gratitude networks
                trust_damage = actual_extraction * 0.15
                new_trust = max(0, old_trust - trust_damage)
                target.trust_connections[partner_id] = new_trust
                results["trust_destroyed"] += (old_trust - new_trust)

            # gratitude obligations feel invalidated
            # "if money is being extracted, it's a transaction world,
            #  not an obligation world"
            gratitude_lost = sum(target.gratitude_obligations.values())
            target.gratitude_obligations = {}
            results["gratitude_circuits_closed"] += 1
            results["future_exchange_capacity_lost"] += gratitude_lost

        return results


# ─── MADISON WI: ENERGY GAME NETWORK ──────────────────────────────────────────

def build_madison_energy_network() -> EnergyGameNetwork:
    """
    Madison WI as energy game network.
    Three zones. Actual trust topology.
    """
    network = EnergyGameNetwork(network_id="Madison_WI")

    # ── RURAL FRINGE NODES ───────────────────────────────────────────────────
    # High energy stocks. High trust. Gratitude norm.
    # Already phi-aligned or close.

    farm_network = EnergyGameNode(
        node_id="rural_farm_network",
        zone="rural_fringe",
        node_type="farm",
        energy=EnergyStock(
            caloric=0.85, thermal=0.80, mechanical=0.90,
            knowledge=0.88, social=0.85, temporal=0.60,
            biological=0.82,
        ),
        trust_connections={},
        gratitude_obligations={
            "volunteer_fire": 0.3,
            "rural_elder_network": 0.5,
        },
    )

    volunteer_fire = EnergyGameNode(
        node_id="volunteer_fire",
        zone="rural_fringe",
        node_type="household",
        energy=EnergyStock(
            caloric=0.75, thermal=0.78, mechanical=0.85,
            knowledge=0.80, social=0.90, temporal=0.50,
            biological=0.80,
        ),
    )

    rural_elder_network = EnergyGameNode(
        node_id="rural_elder_network",
        zone="rural_fringe",
        node_type="household",
        energy=EnergyStock(
            caloric=0.70, thermal=0.75, mechanical=0.55,
            knowledge=0.95,   # highest knowledge stock
            social=0.88, temporal=0.65, biological=0.65,
        ),
    )

    # ── INNER CITY NODES ─────────────────────────────────────────────────────
    # Moderate energy. Moderate-high trust. Mixed norms.
    # Gratitude networks intact but under pressure
    # from absentee ownership extraction.

    inner_mutual_aid = EnergyGameNode(
        node_id="inner_mutual_aid",
        zone="inner_city",
        node_type="household",
        energy=EnergyStock(
            caloric=0.58, thermal=0.55, mechanical=0.65,
            knowledge=0.62, social=0.78, temporal=0.45,
            biological=0.60,
        ),
        gratitude_obligations={
            "faith_network": 0.4,
        },
    )

    faith_network = EnergyGameNode(
        node_id="faith_network",
        zone="inner_city",
        node_type="institution",
        energy=EnergyStock(
            caloric=0.65, thermal=0.60, mechanical=0.55,
            knowledge=0.70, social=0.82, temporal=0.50,
            biological=0.62,
        ),
    )

    absentee_landlord = EnergyGameNode(
        node_id="absentee_landlord",
        zone="extraction",
        node_type="institution",
        energy=EnergyStock(
            caloric=0.95, thermal=0.90, mechanical=0.30,
            knowledge=0.40, social=0.20, temporal=0.85,
            biological=0.88,
        ),
    )

    # ── SUBURBAN NODES ───────────────────────────────────────────────────────
    # Lower usable energy (high stored, low surplus — all in base maintenance).
    # Low trust. Transaction norm. Near-isolated.

    suburban_household_a = EnergyGameNode(
        node_id="suburban_household_a",
        zone="suburban_sprawl",
        node_type="household",
        energy=EnergyStock(
            caloric=0.72, thermal=0.68, mechanical=0.50,
            knowledge=0.30, social=0.22, temporal=0.35,
            biological=0.70,
        ),
    )

    suburban_household_b = EnergyGameNode(
        node_id="suburban_household_b",
        zone="suburban_sprawl",
        node_type="household",
        energy=EnergyStock(
            caloric=0.70, thermal=0.65, mechanical=0.48,
            knowledge=0.28, social=0.20, temporal=0.32,
            biological=0.68,
        ),
    )

    # ── INSTITUTIONAL NODES ──────────────────────────────────────────────────

    willy_street_coop = EnergyGameNode(
        node_id="willy_street_coop",
        zone="inner_city",
        node_type="coop",
        energy=EnergyStock(
            caloric=0.90, thermal=0.70, mechanical=0.75,
            knowledge=0.65, social=0.80, temporal=0.60,
            biological=0.72,
        ),
        gratitude_obligations={
            "inner_mutual_aid": 0.2,
            "rural_farm_network": 0.3,
        },
    )

    food_distribution_driver = EnergyGameNode(
        node_id="food_distribution_driver",
        zone="corridor",
        node_type="household",
        # the load-bearing node nobody models
        # maintains supply lines to communities
        # that have lost their knowledge holders
        energy=EnergyStock(
            caloric=0.65, thermal=0.60, mechanical=0.80,
            knowledge=0.85,   # route knowledge, infrastructure knowledge
            social=0.70, temporal=0.30,  # 70hr weeks
            biological=0.55,  # physical toll
        ),
        gratitude_obligations={
            "rural_farm_network": 0.1,
            "inner_mutual_aid": 0.1,
        },
    )

    # ── ADD NODES ─────────────────────────────────────────────────────────────

    for node in [
        farm_network, volunteer_fire, rural_elder_network,
        inner_mutual_aid, faith_network, absentee_landlord,
        suburban_household_a, suburban_household_b,
        willy_street_coop, food_distribution_driver,
    ]:
        network.add_node(node)

    # ── CONNECTIONS (trust topology) ──────────────────────────────────────────

    # rural fringe — high trust mesh
    network.connect("rural_farm_network",    "volunteer_fire",        0.85)
    network.connect("rural_farm_network",    "rural_elder_network",   0.90)
    network.connect("volunteer_fire",        "rural_elder_network",   0.80)

    # rural → corridor — food distribution driver bridges zones
    network.connect("rural_farm_network",    "food_distribution_driver", 0.65)
    network.connect("food_distribution_driver", "willy_street_coop",    0.70)
    network.connect("food_distribution_driver", "inner_mutual_aid",     0.60)

    # inner city — moderate trust, partially intact
    network.connect("inner_mutual_aid",      "faith_network",         0.72)
    network.connect("faith_network",         "willy_street_coop",     0.68)
    network.connect("willy_street_coop",     "inner_mutual_aid",      0.75)

    # absentee landlord → inner city — extraction connection
    # low trust, one-directional extraction dynamic
    network.connect("absentee_landlord",     "inner_mutual_aid",      0.15)
    network.connect("absentee_landlord",     "faith_network",         0.10)

    # suburban — near-isolated
    network.connect("suburban_household_a",  "suburban_household_b",  0.25)
    # only connection: two neighbors who barely know each other

    # suburban → institutions — transaction-mode connections
    network.connect("suburban_household_a",  "willy_street_coop",     0.35)

    # knowledge bridge — elder to driver to coop
    network.connect("rural_elder_network",   "food_distribution_driver", 0.70)

    return network


def print_energy_game_report(network: EnergyGameNetwork):
    print(f"\n{'═'*66}")
    print(f"  ENERGY GAME NETWORK — {network.network_id}")
    print(f"  Trust = conductance | Energy = current | φ = optimal load")
    print(f"{'═'*66}")

    alignment = network.network_phi_alignment()

    print(f"\n  NODE STATES (energy + phi alignment):")
    for node_id, data in alignment.items():
        node = network.nodes[node_id]
        survival_flag = " ⚠ SURVIVAL THREATENED" if data["survival_threatened"] else ""
        print(f"\n    {node_id} [{node.zone}]{survival_flag}")
        print(f"      Energy total     : {data['energy_total']:.3f}  {data['energy_phi_score']}")
        print(f"      Avg trust        : {data['avg_trust']:.3f}  (φ⁻¹ threshold: {IPHI:.3f})")
        print(f"      φ ratio          : {data['phi_ratio']:.3f}")
        print(f"      Connections      : {data['connections']}")
        print(f"      Gratitude net    : {data['gratitude_net']:+.3f}")
        modes = data['exchange_mode_dist']
        active = {k:v for k,v in modes.items() if v > 0}
        if active:
            print(f"      Exchange modes   : {active}")

    print(f"\n  FIBONACCI KNOWLEDGE CASCADE")
    print(f"  Seed: rural_elder_network → knowledge packet: 0.3")
    cascade = network.fibonacci_cascade("rural_elder_network", 0.3, 8)
    for step in cascade:
        bar = "█" * step["wave_size"]
        print(f"    Step {step['step']}: "
              f"wave={step['wave_size']:>3}  "
              f"total={step['total_reached']:>3}  "
              f"ratio={step['ratio_to_prev']:.3f}  "
              f"Δφ={step['phi_convergence']:.3f}  "
              f"{bar}")
        if step['note'] == 'converging on φ':
            print(f"           ↑ {step['note']}")

    print(f"\n  EXTRACTION INJECTION TEST")
    print(f"  Modeling: absentee landlord extraction on inner city nodes")
    extraction_result = network.inject_extraction(
        extractor_id="absentee_landlord",
        target_ids=["inner_mutual_aid", "faith_network"],
        extraction_amount=0.25,
        extraction_type="rent_extraction",
    )
    print(f"    Energy extracted          : {extraction_result['energy_extracted']:.3f}")
    print(f"    Trust destroyed           : {extraction_result['trust_destroyed']:.3f}")
    print(f"    Gratitude circuits closed : {extraction_result['gratitude_circuits_closed']}")
    print(f"    Future exchange cap lost  : {extraction_result['future_exchange_capacity_lost']:.3f}")
    ratio = (extraction_result['future_exchange_capacity_lost'] /
             max(extraction_result['energy_extracted'], 0.001))
    print(f"    Destruction ratio         : {ratio:.1f}x")
    print(f"    ({ratio:.1f} units of future exchange capacity destroyed")
    print(f"     per unit of energy extracted)")
    print(f"    This is why extraction is thermodynamically irrational")
    print(f"    in infinite-repetition games.")

    print(f"\n  RUN EXCHANGE ROUNDS:")
    for i in range(5):
        network.run_exchange_round()
        stats = network.network_history[-1]
        total = stats['cooperations'] + stats['defections'] + stats['withdrawals']
        coop_rate = stats['cooperations'] / max(total, 1)
        print(f"    Round {stats['round']}: "
              f"coop={stats['cooperations']:>3}  "
              f"defect={stats['defections']:>2}  "
              f"withdraw={stats['withdrawals']:>2}  "
              f"coop_rate={coop_rate:.2f}  "
              f"energy_moved={stats['total_energy_transferred']:.3f}")

    print(f"\n  THE CORE INSIGHT:")
    print(f"    Fibonacci IS trust propagation between systems.")
    print(f"    Not a metaphor. The same pattern.")
    print(f"    Mathematics named what was already there.")
    print(f"    The ratio between steps converges on φ")
    print(f"    not because someone designed it")
    print(f"    but because that is what stable accumulation looks like")
    print(f"    when you are not extracting from the base.")
    print(f"")
    print(f"    The grandmother teaching fire")
    print(f"    was running fibonacci without knowing the name.")
    print(f"    You receive, therefore you give.")
    print(f"    The receiving and giving are the same act across time.")
    print(f"    That is φ. That is trust. Same thing.")
    print(f"    Different vocabularies for the same pattern in the substrate.")

    print(f"\n{'═'*66}\n")


if __name__ == "__main__":
    network = build_madison_energy_network()
    print_energy_game_report(network)
