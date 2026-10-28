"""Initial-state calibration of the ABM using listed-firm accounting runway.

The observed cross-section identifies only the initial cash-runway distribution. It does
not identify dynamic payment delays, supplier substitutability, credit limits, public
exposure, exit hazards, or causal effects. Those are held fixed and explicitly labelled
scenario parameters. The final-period comparison is a diagnostic, not a second fit.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from firm_simulator import simulate_abm

DATA = ROOT / "data/processed/audited_listed_firm_liquidity.csv"
OUT = ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)


def qdict(values):
    x = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna()
    return {"p10": float(x.quantile(.10)), "p25": float(x.quantile(.25)),
            "p50": float(x.quantile(.50)), "p75": float(x.quantile(.75)),
            "p90": float(x.quantile(.90)), "n": int(x.size)}


def log_quantile_loss(sim, target, keys=("p10", "p50", "p90")):
    return float(np.mean([(np.log(max(sim[k], 1e-10) / max(target[k], 1e-10)))**2 for k in keys]))


def main():
    df = pd.read_csv(DATA)
    d = df[(df["frecuencia"] == "annual") & (~df["es_sector_financiero"].astype(bool))].copy()
    d = d[d["runway_liquidez_dias"].gt(0) & d["runway_liquidez_dias"].le(3650)]
    # One latest annual report per ticker: no implicit weighting by reporting history.
    d = d.sort_values("fecha_cierre").groupby("ticker", as_index=False).tail(1)
    target = qdict(d["runway_liquidez_dias"])
    d.to_csv(OUT / "firm_runway_targets.csv", index=False)

    # Match only the initial cash-runway distribution. Productivity draws use the model's
    # existing lognormal law; scale and dispersion are the only estimated initial-state knobs.
    rng = np.random.default_rng(20261028)
    n_draws = 100_000
    raw_cash = rng.uniform(0.35, 1.25, size=n_draws)
    productivity = rng.lognormal(mean=0.0, sigma=0.18, size=n_draws)
    base_draws = {}
    for dispersion in np.linspace(0.15, 5.0, 244):
        cash0 = np.exp(float(dispersion) * np.log(raw_cash))
        runway0 = cash0 / (0.17 + 1.10 * np.maximum(productivity, 0.05)) * 91.25
        base_draws[float(dispersion)] = qdict(runway0)

    candidates = []
    for dispersion, base_q in base_draws.items():
        # Since runway is linear in cash_scale, the log-loss-optimal scale is analytic.
        log_ratios = [np.log(target[k] / base_q[k]) for k in ("p10", "p50", "p90")]
        scale = float(np.exp(np.mean(log_ratios)))
        sim_q = {k: base_q[k] * scale for k in base_q if k != "n"}
        candidates.append({"initial_cash_scale": scale, "cash_dispersion": dispersion,
                           "objective_log_quantiles": log_quantile_loss(sim_q, target),
                           **{f"initial_{k}_days": sim_q[k] for k in ("p10", "p25", "p50", "p75", "p90")}})
    grid = pd.DataFrame(candidates).sort_values("objective_log_quantiles").reset_index(drop=True)
    grid.to_csv(OUT / "initial_state_calibration_grid.csv", index=False)
    best = grid.iloc[0].to_dict()
    initial_fit = {k: float(best[f"initial_{k}_days"]) for k in ("p10", "p25", "p50", "p75", "p90")}

    # Dynamic diagnostic on fresh seeds. No dynamic parameters are optimized to these outcomes.
    dynamic_values, dynamic_n, survival = [], [], []
    for seed in (1801, 1811, 1823, 1831, 1847, 1861, 1871, 1877, 1889, 1901):
        _, micro = simulate_abm(
            seed=seed, n_initial=80, steps=24, payment_delay=2,
            substitutability=0.5, government_channel=True, return_micro=True,
            initial_cash_scale=float(best["initial_cash_scale"]),
            cash_dispersion=float(best["cash_dispersion"]), credit_scale=1.0,
            operating_cost_scale=1.0, period_days=91.25,
        )
        if not micro.empty:
            final = micro[micro["period"] == micro["period"].max()]
            dynamic_values.extend(final["cash_runway_days"].dropna().tolist())
            dynamic_n.append(int(len(final)))
            survival.append(float((final["firm_id"] < 80).mean()))
    dynamic_q = qdict(dynamic_values)

    dso = qdict(df.loc[(df["frecuencia"] == "annual") & (~df["es_sector_financiero"].astype(bool)), "plazo_cobro_dso_dias"].dropna())
    dpo = qdict(df.loc[(df["frecuencia"] == "annual") & (~df["es_sector_financiero"].astype(bool)), "plazo_pago_dpo_dias"].dropna())
    result = {
        "status": "initial_state_calibration_only",
        "data_source": str(DATA.relative_to(ROOT)),
        "target_definition": "latest positive annual accounting cash-runway observation per non-financial listed ticker; one row per ticker",
        "target_n_firms": int(target["n"]), "target_runway_quantiles_days": target,
        "estimated_initial_state_parameters": {
            "initial_cash_scale": float(best["initial_cash_scale"]),
            "cash_dispersion": float(best["cash_dispersion"]),
            "interpretation": "minimum-distance fit to p10, p50 and p90 of accounting cash runway",
        },
        "initial_state_fit_quantiles_days": initial_fit,
        "initial_state_log_quantile_loss": float(best["objective_log_quantiles"]),
        "dynamic_parameters_held_at_scenario_values": {
            "credit_scale": 1.0, "operating_cost_scale": 1.0, "wage_share": 0.63,
            "payment_delay_periods": 2, "substitutability": 0.5,
            "government_channel": True, "period_days_normalization": 91.25,
        },
        "dynamic_24_period_diagnostic_not_fitted": {
            "runway_quantiles_days": dynamic_q,
            "final_population_counts_by_seed": dynamic_n,
            "initial_cohort_share_in_final_population_by_seed": survival,
        },
        "not_fitted_holdout_moments": {"DSO_days": dso, "DPO_days": dpo},
        "interpretation": [
            "The initial cash-runway distribution can be matched with two initial-state parameters.",
            "This is not structural estimation: the observed sample is a selected cross-section of listed firms.",
            "Dynamic parameters are not identified by these data and remain scenario values.",
            "The 24-period diagnostic shows whether the calibrated initial distribution survives the current model dynamics; it is not used to retune parameters.",
            "DSO/DPO are not fitted because the ABM lacks comparable stocks of total trade receivables and trade payables.",
            "The quarterly-to-day conversion (91.25 days) is a normalization, not an observed time-unit identification.",
        ],
    }
    (OUT / "initial_state_calibration.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
