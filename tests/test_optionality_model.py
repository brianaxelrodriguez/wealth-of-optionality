import numpy as np
import pytest
from src.optionality_model import (
    lomax_distress, lomax_marginal_risk_reduction, lomax_elasticity,
    network_multiplier, bin_integration_error_bound, trajectory_error_bound,
)


def test_lomax_distress_decreases_with_runway():
    vals = lomax_distress(np.array([0., 1., 5.]), burn=2, scale=3, shape=1.5)
    assert vals[0] == pytest.approx(1.0)
    assert vals[0] > vals[1] > vals[2] > 0


def test_lomax_derivative_matches_finite_difference():
    r, h = 1.7, 1e-6
    numerical = -(lomax_distress(r+h, 1.2, 2.4, 1.7)-lomax_distress(r-h, 1.2, 2.4, 1.7))/(2*h)
    assert lomax_marginal_risk_reduction(r, 1.2, 2.4, 1.7) == pytest.approx(numerical, rel=1e-5)


def test_lomax_elasticity_limits():
    assert lomax_elasticity(0, 1, 2, 3) == 0
    assert lomax_elasticity(1e9, 1, 2, 3) == pytest.approx(3, rel=1e-8)


def test_network_multiplier_matches_closed_form():
    u = np.array([1., 0.])
    W = np.array([[0., 1.], [0.5, 0.]])
    x = network_multiplier(u, W, 0.4)
    assert np.all(x >= u - 1e-12)
    assert np.allclose(x, u + 0.4*W@x)


def test_network_multiplier_rejects_unstable_case():
    with pytest.raises(ValueError):
        network_multiplier(np.ones(2), np.ones((2,2)), 1.0)


def test_bin_bound():
    assert bin_integration_error_bound(4, 0.25) == pytest.approx(0.5)


def test_gronwall_bound_zero_lipschitz():
    assert trajectory_error_bound(0.1, 0.2, 0, 3) == pytest.approx(0.7)


def test_invalid_runway_rejected():
    with pytest.raises(ValueError):
        lomax_distress(-1)


def test_agent_based_simulation_returns_finite_summary():
    from src.firm_simulator import simulate_abm
    out = simulate_abm(seed=19, n_initial=8, steps=3, payment_delay=1,
                       substitutability=0.5, government_channel=True)
    assert len(out) == 3
    assert np.isfinite(out.select_dtypes(include=[np.number]).to_numpy()).all()


def test_abm_input_rationing_reduces_realized_sales():
    from src.firm_simulator import simulate_abm
    _, micro = simulate_abm(seed=2, n_initial=10, steps=3, payment_delay=2,
                            initial_cash_scale=0.01, credit_scale=0.01,
                            return_micro=True)
    assert not micro.empty
    assert (micro["realized_sales"] <= micro["potential_sales"] + 1e-12).all()
    assert (micro["production_scale"] >= 0).all()
    assert (micro["production_scale"] <= 1 + 1e-12).all()
    assert (micro["production_scale"] < 1).any()


def test_abm_zero_delay_and_no_government_channel_have_no_public_arrears():
    from src.firm_simulator import simulate_abm
    zero_delay = simulate_abm(seed=31, n_initial=10, steps=4, payment_delay=0,
                              government_channel=True)
    no_government = simulate_abm(seed=31, n_initial=10, steps=4, payment_delay=3,
                                 government_channel=False)
    assert np.allclose(zero_delay["public_arrears"], 0.0)
    assert np.allclose(no_government["public_arrears"], 0.0)
    assert (zero_delay["realized_sales"] <= zero_delay["potential_sales"] + 1e-12).all()
    assert (no_government["realized_sales"] <= no_government["potential_sales"] + 1e-12).all()
