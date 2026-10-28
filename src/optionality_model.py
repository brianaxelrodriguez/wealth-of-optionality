"""Core analytical functions for the liquidity-optionality framework.

All functions are deterministic. This module implements conditional formulae;
it does not estimate structural parameters or identify causal effects.
"""
from __future__ import annotations
import math
import numpy as np


def lomax_distress(runway, burn=1.0, scale=1.0, shape=1.5):
    """P(X > burn*runway) for a Lomax shock with scale and shape > 0."""
    if burn <= 0 or scale <= 0 or shape <= 0:
        raise ValueError("burn, scale and shape must be strictly positive")
    r = np.asarray(runway, dtype=float)
    if np.any(r < 0):
        raise ValueError("runway must be nonnegative")
    ans = (1.0 + burn * r / scale) ** (-shape)
    return float(ans) if ans.ndim == 0 else ans


def lomax_marginal_risk_reduction(runway, burn=1.0, scale=1.0, shape=1.5):
    """Return -dq/dR for the Lomax distress probability."""
    if burn <= 0 or scale <= 0 or shape <= 0:
        raise ValueError("burn, scale and shape must be strictly positive")
    r = np.asarray(runway, dtype=float)
    if np.any(r < 0):
        raise ValueError("runway must be nonnegative")
    ans = shape * burn / scale * (1.0 + burn * r / scale) ** (-shape - 1.0)
    return float(ans) if ans.ndim == 0 else ans


def lomax_elasticity(runway, burn=1.0, scale=1.0, shape=1.5):
    """Absolute elasticity -R q'(R)/q(R)."""
    if burn <= 0 or scale <= 0 or shape <= 0:
        raise ValueError("burn, scale and shape must be strictly positive")
    r = np.asarray(runway, dtype=float)
    if np.any(r < 0):
        raise ValueError("runway must be nonnegative")
    ans = shape * burn * r / (scale + burn * r)
    return float(ans) if ans.ndim == 0 else ans


def network_multiplier(direct_shock, exposure, beta):
    """Solve x = u + beta W x when rho(beta W) < 1 and W,u are nonnegative."""
    u = np.asarray(direct_shock, dtype=float)
    W = np.asarray(exposure, dtype=float)
    if W.shape != (u.size, u.size):
        raise ValueError("exposure must be a square matrix matching the shock vector")
    if beta < 0 or np.any(u < 0) or np.any(W < 0):
        raise ValueError("beta, direct shocks and exposure weights must be nonnegative")
    spectral_radius = max(abs(np.linalg.eigvals(beta * W)), default=0.0)
    if spectral_radius >= 1.0:
        raise ValueError("stability condition rho(beta W) < 1 is not satisfied")
    return np.linalg.solve(np.eye(u.size) - beta * W, u)


def bin_integration_error_bound(lipschitz_constant, max_bin_width):
    """Worst-case midpoint integration error bound for a probability measure."""
    if lipschitz_constant < 0 or max_bin_width < 0:
        raise ValueError("Lipschitz constant and bin width must be nonnegative")
    return lipschitz_constant * max_bin_width / 2.0


def trajectory_error_bound(initial_error, field_error, lipschitz, time):
    """Gronwall bound, assuming common invariant domain and Lipschitz fields."""
    if min(initial_error, field_error, lipschitz, time) < 0:
        raise ValueError("all arguments must be nonnegative")
    if lipschitz == 0:
        return initial_error + field_error * time
    return math.exp(lipschitz * time) * initial_error + field_error * math.expm1(lipschitz * time) / lipschitz
