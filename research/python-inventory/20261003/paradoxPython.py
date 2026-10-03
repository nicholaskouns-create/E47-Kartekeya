import numpy as np

def generate_paradoxical_chaos(n_steps=1000, r=3.99):
    # Simulates the chaotic feedback loop of the predictive paradox
    x = np.zeros(n_steps)
    x[0] = 0.5  # Maximum uncertainty initial state
    for t in range(1, n_steps):
        # State updates based on the predictive out-matching loop
        x[t] = r * x[t-1] * (1 - x[t-1])
    return x

# Simulate 1000 structural iterations
chaos_trajectory = generate_paradoxical_chaos()

# Compute the Shannon Entropy of the noise (quantized into 20 bins)
counts, _ = np.histogram(chaos_trajectory, bins=20)
probs = counts / np.sum(counts)
probs = probs[probs > 0]
entropy = -np.sum(probs * np.log2(probs))

print(f"Calculated Shannon Entropy: {entropy:.4f} bits")
print(f"Theoretical Max Entropy: {np.log2(20):.4f} bits")
