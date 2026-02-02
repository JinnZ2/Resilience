import numpy as np

# -----------------------------
# Node definitions (communities)
# -----------------------------
nodes = ["Minneapolis", "Juneau", "Bismarck", "Helena"]
num_nodes = len(nodes)

# Baseline environmental time stress (hours/day required to survive climate extremes)
H_climate = np.array([4.0, 3.0, 3.5, 3.8])      # heating, cooling, snow clearing, weather events
H_infra = np.array([1.5, 2.0, 1.2, 1.0])        # extra time navigating infrastructure stress
H_community = np.array([2.5, 3.0, 2.0, 2.0])   # time gained via mutual aid / hidden labor
H_human = np.array([3.0, 2.5, 2.5, 2.5])       # survival behavior activation threshold
H_centralization = np.array([1.0, 0.8, 1.2, 1.0]) # imposed time cost of centralized policies
H_resource = np.array([3.5, 3.0, 3.2, 3.0])    # time needed to secure survival resources
H_support = np.array([0.7, 0.8, 0.6, 0.65])    # community control (reduces centralization time cost)
R = np.array([0.6, 0.7, 0.65, 0.62])           # fraction of stress mitigated by built-in slack

# -----------------------------
# Edge definitions (coupled nodes)
# -----------------------------
# w_ij = fraction of node j's time stress affecting node i
w = np.array([
    [0.0, 0.3, 0.2, 0.2],
    [0.3, 0.0, 0.15, 0.15],
    [0.2, 0.15, 0.0, 0.25],
    [0.2, 0.15, 0.25, 0.0]
])

# -----------------------------
# Survival behavior activation
# -----------------------------
def survival_activation_time(stress, threshold=2.0, factor=1.5):
    return factor * (stress - threshold) if stress > threshold else 0

# -----------------------------
# Node update function (time-centric)
# -----------------------------
def update_time_stress(S_current):
    S_new = np.zeros_like(S_current)
    for i in range(num_nodes):
        # Propagate coupled node stress
        edge_sum = 0
        for j in range(num_nodes):
            if i != j:
                edge_sum += w[i,j] * S_current[j] * (1 - H_community[j]) * (1 + H_centralization[j]*(1-H_support[j]))
        # Node stress update (hours/day)
        S_new[i] = S_current[i] + edge_sum \
                   + H_climate[i]*(1-R[i]) \
                   + H_infra[i] \
                   + H_centralization[i]*(1-H_support[i]) \
                   + H_resource[i] \
                   - H_community[i] \
                   - H_human[i]*survival_activation_time(S_current[i])
        # clip to non-negative (cannot have negative time deficit)
        S_new[i] = max(0.0, S_new[i])
    return S_new

# -----------------------------
# Simulation
# -----------------------------
timesteps = 10
S = np.zeros((timesteps, num_nodes))
# initial time stress baseline (hours/day)
S[0] = np.array([2.0, 2.0, 2.0, 2.0])

for t in range(1, timesteps):
    S[t] = update_time_stress(S[t-1])

# -----------------------------
# Output results
# -----------------------------
for i, node in enumerate(nodes):
    print(f"\nNode: {node}")
    for t in range(timesteps):
        print(f" Timestep {t}: Time Deficit = {S[t,i]:.2f} hours/day")
