#!/usr/bin/env python3
"""
Ship Digital Twin: Pre-calculates fire response paths from vessel blueprints
Parses container ship JSON → optimal wolf pack trajectories
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Container:
    id: str
    coords: Tuple[float, float, float]  # x,y,z in meters from bow
    cargo_type: str
    battery_risk: float  # 0-1 lithium probability

class ShipDigitalTwin:
    def __init__(self, blueprint_file: str):
        with open(blueprint_file, 'r') as f:
            self.blueprint = json.load(f)
        
        self.containers: Dict[str, Container] = {}
        self.fire_paths = {}
        self.deck_layout = self.blueprint['deck_layout']
        self._parse_containers()
        self._precalculate_response_paths()
        
    def _parse_containers(self):
        """Extract battery-risk containers from blueprint."""
        for container in self.blueprint['cargo_manifest']:
            if container['cargo_type'] == 'lithium_battery':
                cont = Container(
                    id=container['id'],
                    coords=tuple(container['position']),  # [x,y,z]
                    cargo_type=container['cargo_type'],
                    battery_risk=container.get('fire_risk', 0.8)
                )
                self.containers[cont.id] = cont
    
    def _precalculate_response_paths(self):
        """Wolf pack optimal attack angles for each container."""
        launch_point = self.blueprint['drone_launcher']  # Bridge coords
        
        for cont_id, cont in self.containers.items():
            # Tetrahedron formation: 4 drones, 109.5° angles around fire
            paths = {
                'alpha': self._scout_path(launch_point, cont.coords),
                'beta1': self._attack_path(launch_point, cont.coords, 120),
                'beta2': self._attack_path(launch_point, cont.coords, 240),
                'gamma': self._deep_cool_path(launch_point, cont.coords)
            }
            self.fire_paths[cont_id] = paths
    
    def _scout_path(self, launch: Tuple, target: Tuple) -> List[Tuple]:
        """Alpha drone: thermal recon spiral approach."""
        path = [launch]
        for i in range(8):
            r = i * 0.5
            theta = i * 0.8  # Golden angle
            x = target[0] + r * math.cos(theta)
            y = target[1] + r * math.sin(theta)
            path.append((x, y, target[2] + 2))  # +2m hover
        return path
    
    def _attack_path(self, launch: Tuple, target: Tuple, angle_deg: float) -> List[Tuple]:
        """Beta CO2: Direct 120°/240° attack vector."""
        angle = math.radians(angle_deg)
        dx = 5 * math.cos(angle)  # 5m standoff
        dy = 5 * math.sin(angle)
        return [launch, (target[0] + dx, target[1] + dy, target[2] + 3)]
    
    def _deep_cool_path(self, launch: Tuple, target: Tuple) -> List[Tuple]:
        """Gamma LN2: Overhead kill shot."""
        return [launch, (target[0], target[1], target[2] + 8)]  # 8m altitude
    
    def get_wolfpack_paths(self, container_id: str) -> Dict:
        """Return pre-calculated 4-drone fire attack plan."""
        return self.fire_paths.get(container_id, {})
    
    def nearest_fire_risk(self, drone_pos: Tuple) -> Optional[str]:
        """Find highest-risk container near drone position."""
        if not self.containers:
            return None
        return max(self.containers, key=lambda c:
                  self.containers[c].battery_risk / (math.dist(drone_pos, self.containers[c].coords) + 1))
