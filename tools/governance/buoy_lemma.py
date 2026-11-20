"""Admissible finite-time envelope for a perturbed zero spectral cluster."""
import math


def admissible_window(gap, interpolation_error, substrate_error, radius, flow_budget):
    """Return inclusive time bounds for the allocated flow error.

    radius bounds both ||C - 18I|| and ||C_hat - 18I|| in spectral norm.
    The caller supplies a separate budget for the change in projector.
    """
    inputs = (gap, interpolation_error, substrate_error, radius, flow_budget)
    if not all(math.isfinite(x) and x >= 0 for x in inputs) or gap == 0 or not 0 < flow_budget < 1:
        raise ValueError("Invalid gap, error budget or operator radius")
    epsilon = interpolation_error + 2 * radius * substrate_error
    if not epsilon < gap / 2:
        raise ValueError("Noise ceiling exceeded")
    # Divide twice to avoid squaring a very small positive epsilon.
    t_min = -math.log(flow_budget) / (gap - epsilon) / (gap - epsilon)
    t_max = (-math.log1p(-flow_budget) / epsilon / epsilon) if epsilon else math.inf
    if not math.isfinite(t_min) or t_min > t_max:
        raise ValueError("No admissible finite-time operating window")
    return epsilon, t_min, t_max
