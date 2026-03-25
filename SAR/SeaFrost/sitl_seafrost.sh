#!/bin/bash
# 4-drone SeaFrost wolf pack SITL
# Launch from ArduPilot root directory

echo "🚁 Launching SeaFrost 4-drone maritime fire swarm..."

# Kill existing SITL
pkill -f sim_vehicle.py

# Drone 1: Alpha Scout (SYSID=1)
sim_vehicle.py -v ArduCopter --console --map --aircraft=Alpha --add-param=SYSID_THISMAV=1 -I1 &
sleep 5

# Drone 2: Beta-1 CO2 (SYSID=2)  
sim_vehicle.py -v ArduCopter --console --map --aircraft=Beta1 --add-param=SYSID_THISMAV=2 -I2 &
sleep 5

# Drone 3: Beta-2 CO2 (SYSID=3)
sim_vehicle.py -v ArduCopter --console --map --aircraft=Beta2 --add-param=SYSID_THISMAV=3 -I3 &
sleep 5

# Drone 4: Gamma LN2 (SYSID=4)
sim_vehicle.py -v ArduCopter --console --map --aircraft=Gamma --add-param=SYSID_THISMAV=4 -I4 &

echo "✅ SITL ports: 5760(Alpha), 5761(Beta1), 5762(Beta2), 5763(Gamma)"
echo "Run: python maersk_fire_test.py"
echo "Connect MAVLink: tcp:127.0.0.1:5760-5763"
