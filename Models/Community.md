import numpy as np

# -----------------------------
# Node definitions
# -----------------------------
nodes = ["Minneapolis", "Juneau", "Bismarck", "Helena"]
num_nodes = len(nodes)

# Environmental stress (0-1, normalized)
H_climate = np.array([0.9, 0.7, 0.85, 0.88])      # extreme amplitude and dual-season stress
H_infra = np.array([0.7, 0.8, 0.65, 0.6])         # infrastructure vulnerability
H_community = np.array([0.8, 0.9, 0.75, 0.7])    # hidden labor / adaptive slack
H_human = np.array([0.95, 0.9, 0.9, 0.9])         # survival activation threshold
H_centralization = np.array([0.5, 0.4, 0.6, 0.55])# centralized control stress factor
H_resource = np.array([0.6, 0.7, 0.65, 0.6])      # supply/economic stress

# Community support coefficient (0-1)
H_support = np.array([0.7, 0.8, 0.6, 0.65])       # higher = more local autonomy

# Resilience coefficient (0-1)
R = np.array([0.6, 0.7, 0.65, 0.62])             # ability to absorb stress

# -----------------------------
# Edge definitions (weight matrix)
# -----------------------------
# symmetric weights representing coupling between nodes (0 = no influence)
# e.g., economic, social, or infrastructure interdependence
w = np.array([
    [0.0, 0.3, 0.2, 0.2],  # Minneapolis
    [0.3, 0.0, 0.15, 0.15],# Juneau
    [0.2, 0.15, 0.0, 0.25],# Bismarck
    [0.2, 0.15, 0.25, 0.0] # Helena
])

# Delay matrix (not used in first iteration; placeholder)
d = np.zeros((num_nodes, num_nodes))

# -----------------------------
# Stress threshold function
# -----------------------------
def survival_activation(stress, threshold=0.6, factor=1.5):
    return factor * (stress - threshold) if stress > threshold else 0

# -----------------------------
# Node update function
# -----------------------------
def update_stress(S_current):
    S_new = np.zeros_like(S_current)
    for i in range(num_nodes):
        edge_sum = 0
        for j in range(num_nodes):
            if i != j:
                # interaction dampened by community slack, amplified by centralization
                edge_sum += w[i,j] * S_current[j] * (1 - H_community[j]) * (1 + H_centralization[j]*(1-H_support[j]))
        # node stress propagation
        S_new[i] = S_current[i] + edge_sum + H_climate[i]*(1-R[i]) + H_infra[i] + H_resource[i] + H_human[i]*survival_activation(S_current[i])
    # clip to max 1
    S_new = np.clip(S_new, 0, 1)
    return S_new

# -----------------------------
# Simulation
# -----------------------------
timesteps = 10
S = np.zeros((timesteps, num_nodes))
# initialize stress (baseline)
S[0] = np.array([0.2, 0.2, 0.2, 0.2])

for t in range(1, timesteps):
    S[t] = update_stress(S[t-1])

# -----------------------------
# Output
# -----------------------------
for i, node in enumerate(nodes):
    print(f"\nNode: {node}")
    for t in range(timesteps):
        print(f" Timestep {t}: Stress = {S[t,i]:.3f}")
