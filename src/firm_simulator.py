"""Minimal, transparent firm-level ABM for the Wealth of Optionality project.

This is a mechanism laboratory, not an empirically calibrated economy. It uses only
NumPy/Pandas plus the Python standard library, so it runs in Google Colab without Mesa.
A Mesa adapter can be added later without changing the transition rules.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math
import numpy as np
import pandas as pd

@dataclass
class Firm:
    fid: int
    cash: float
    credit_limit: float
    debt: float
    productivity: float
    innovative: bool
    alive: bool = True
    suppliers: Dict[int, float] = field(default_factory=dict)  # buyer -> supplier weights
    receivables: List[Tuple[int, float]] = field(default_factory=list)  # (due_period, amount)
    unpaid_inputs: float = 0.0
    age: int = 0

    @property
    def unused_credit(self) -> float:
        return max(0.0, self.credit_limit - self.debt)


def _weights(ids):
    if not ids:
        return {}
    w = 1.0 / len(ids)
    return {int(i): w for i in ids}


def _make_firm(fid: int, rng: np.random.Generator, initial: bool = False,
               initial_cash_scale: float = 1.0, cash_dispersion: float = 1.0,
               credit_scale: float = 1.0) -> Firm:
    """Create a firm with explicit initial-liquidity calibration knobs.

    cash_dispersion=1 and unit scales define the default initial-state distribution. These
    knobs permit a limited cross-sectional moment fit; they are not estimates of
    invoice-level payment mechanisms.
    """
    raw_cash = float(rng.uniform(0.35, 1.25) if initial else rng.uniform(0.25, 0.8))
    raw_credit = float(rng.uniform(0.25, 0.9) if initial else rng.uniform(0.1, 0.5))
    return Firm(
        fid=fid,
        cash=float(initial_cash_scale * math.exp(cash_dispersion * math.log(raw_cash))),
        credit_limit=float(credit_scale * raw_credit),
        debt=0.0,
        productivity=float(rng.lognormal(mean=0.0 if initial else -0.08, sigma=0.18)),
        innovative=bool(rng.random() < (0.30 if initial else 0.18)),
    )

def _initialise_network(firms: Dict[int, Firm], rng: np.random.Generator, degree: int = 3):
    ids = list(firms)
    for f in firms.values():
        candidates = [i for i in ids if i != f.fid]
        k = min(degree, len(candidates))
        chosen = list(rng.choice(candidates, size=k, replace=False)) if k else []
        f.suppliers = _weights(chosen)


def _rewire(firms: Dict[int, Firm], rng: np.random.Generator, substitutability: float):
    active_ids = [i for i, f in firms.items() if f.alive]
    for f in firms.values():
        if not f.alive:
            continue
        new_suppliers = {}
        for sid, weight in f.suppliers.items():
            if sid in firms and firms[sid].alive and sid != f.fid:
                new_suppliers[sid] = weight
            elif active_ids and rng.random() < substitutability:
                candidates = [i for i in active_ids if i != f.fid and i not in new_suppliers]
                if candidates:
                    # A substitute is selected from the surviving supplier pool. No claim
                    # is made that this random rule is an estimated matching function.
                    new_suppliers[int(rng.choice(candidates))] = weight
        if new_suppliers:
            total = sum(new_suppliers.values())
            f.suppliers = {i: w / total for i, w in new_suppliers.items()}
        else:
            f.suppliers = {}


def simulate_abm(seed: int = 1, n_initial: int = 80, steps: int = 50,
                 payment_delay: int = 2, substitutability: float = 0.5,
                 government_channel: bool = True, innovation_support: float = 0.0,
                 shock_scale: float = 0.08, max_population: int | None = None,
                 return_micro: bool = False, initial_cash_scale: float = 1.0,
                 cash_dispersion: float = 1.0, credit_scale: float = 1.0,
                 operating_cost_scale: float = 1.0, wage_share: float = 0.63, period_days: float = 91.25):
    """Run one firm-level ABM trajectory and return period-level observables.

    Parameters are normalized mechanism knobs, not empirical estimates. Government
    invoices are generated as a share of sales and collected after `payment_delay`.
    The effective runway discounts outstanding public receivables by a delay-dependent
    monetizability factor. Firm cash, credit, supplier payments, innovation, entry and
    exit evolve at agent level; aggregate series are emergent summaries.
    """
    if n_initial < 5 or steps < 1 or payment_delay < 0:
        raise ValueError("n_initial >= 5, steps >= 1, and payment_delay >= 0 are required")
    if not 0 <= substitutability <= 1 or not 0 <= innovation_support <= 1:
        raise ValueError("substitutability and innovation_support must be in [0,1]")
    if initial_cash_scale <= 0 or cash_dispersion <= 0 or credit_scale <= 0 or operating_cost_scale <= 0 or period_days <= 0 or not 0 <= wage_share <= 1:
        raise ValueError("cash/credit scales, dispersion, and period_days must be positive")
    rng = np.random.default_rng(seed)
    firms: Dict[int, Firm] = {i: _make_firm(i, rng, True, initial_cash_scale, cash_dispersion, credit_scale) for i in range(n_initial)}
    next_id = n_initial
    _initialise_network(firms, rng)
    max_population = max_population or int(1.5 * n_initial)
    records = []
    micro_records = []

    for t in range(steps):
        active = [f for f in firms.values() if f.alive]
        if not active:
            # Empty populations are allowed as outcomes, but the model cannot restart
            # unless an explicit entry rule creates an entrant.
            break
        inflow: Dict[int, float] = {}
        planned_inputs: Dict[int, float] = {}
        pre_network_cash: Dict[int, float] = {}
        sales_map: Dict[int, float] = {}
        arrears_map: Dict[int, float] = {}
        unpaid_map: Dict[int, float] = {}
        supplier_receipts = {f.fid: 0.0 for f in active}
        payment_flows = []

        # Stage 1: collect matured invoices and reserve liquidity before production.
        # Current-period sales are NOT available to finance current-period inputs.
        collection_map: Dict[int, float] = {}
        fixed_burn_map: Dict[int, float] = {}
        potential_sales_map: Dict[int, float] = {}
        planned_inputs: Dict[int, float] = {}
        pre_input_resources: Dict[int, float] = {}
        arrears_map: Dict[int, float] = {}
        unpaid_map: Dict[int, float] = {}
        draw_map: Dict[int, float] = {}
        realized_sales_map: Dict[int, float] = {}
        supplier_receipts = {f.fid: 0.0 for f in active}
        payment_flows = []

        for f in active:
            f.age += 1
            potential_sales = max(0.05, f.productivity * rng.lognormal(mean=-0.03, sigma=shock_scale))
            potential_sales_map[f.fid] = potential_sales
            collection = 0.0
            still_outstanding = []
            for due, amount in f.receivables:
                if due <= t:
                    collection += amount
                else:
                    still_outstanding.append((due, amount))
            f.receivables = still_outstanding
            collection_map[f.fid] = collection
            arrears_map[f.fid] = sum(a for _, a in f.receivables)
            fixed_burn = 0.17 * operating_cost_scale
            fixed_burn_map[f.fid] = fixed_burn
            # Only opening cash, matured invoices and undrawn credit can finance inputs.
            resources_before_inputs = f.cash + collection - fixed_burn
            pre_input_resources[f.fid] = resources_before_inputs
            planned_inputs[f.fid] = 0.42 * potential_sales * operating_cost_scale

        # Stage 2: simultaneous input purchases and deliveries. Input rationing determines
        # the production scale, so realized sales cannot exceed output feasible with paid inputs.
        for buyer in active:
            bid = buyer.fid
            planned = planned_inputs[bid]
            own_resources = max(0.0, pre_input_resources[bid])
            available = max(0.0, own_resources + buyer.unused_credit - 0.08)
            paid_total = min(planned, available)
            draw = (min(buyer.unused_credit, max(0.0, paid_total - own_resources)) if paid_total > 0 else 0.0)
            draw_map[bid] = draw
            buyer.debt += draw
            unpaid_map[bid] = planned - paid_total
            buyer.unpaid_inputs = unpaid_map[bid]
            factor = min(1.0, paid_total / planned) if planned > 0 else 1.0
            realized_sales = potential_sales_map[bid] * factor
            realized_sales_map[bid] = realized_sales
            sales_map[bid] = realized_sales
            gov_share = 0.25 if government_channel else 0.0
            invoice = realized_sales * gov_share
            private_receipts = realized_sales - invoice
            if invoice > 0 and payment_delay > 0:
                buyer.receivables.append((t + payment_delay, invoice))
            # Cash receipts from current production arrive only after the input decision.
            buyer._period_private_receipts = private_receipts
            buyer._period_immediate_government_receipt = invoice if payment_delay == 0 else 0.0
            buyer._period_wages = wage_share * realized_sales * operating_cost_scale
            for sid, weight in buyer.suppliers.items():
                if sid in supplier_receipts and sid != bid:
                    payment = paid_total * weight
                    supplier_receipts[sid] += payment
                    payment_flows.append((bid, sid, payment))

        # Stage 3: close cash, innovation, runway/hazard, and exit.
        exits = []
        active_for_stats = []
        for f in active:
            fid = f.fid
            f.cash = max(0.0, f.cash + collection_map[fid] - fixed_burn_map[fid]
                         - (planned_inputs[fid] - unpaid_map[fid]) + draw_map[fid]
                         + supplier_receipts[fid] + f._period_private_receipts
                         + f._period_immediate_government_receipt - f._period_wages)
            # Remove transient period fields so the state remains explicit.
            del f._period_private_receipts
            del f._period_immediate_government_receipt
            del f._period_wages
            if f.cash > 0 and f.debt > 0:
                repayment = min(f.cash, f.debt)
                f.cash -= repayment
                f.debt -= repayment
            outstanding = sum(a for _, a in f.receivables)
            delay_discount = math.exp(-0.35 * payment_delay) if government_channel else 0.0
            sales = max(sales_map[fid], 0.05)
            burn = (0.17 + (wage_share + 0.42) * sales) * operating_cost_scale
            effective_runway = (f.cash + f.unused_credit + delay_discount * outstanding) / burn
            slack = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, effective_runway - 1.0))))
            p_innovate = min(0.35, 0.015 + 0.10 * slack + 0.10 * innovation_support)
            if not f.innovative and f.cash >= 0.12 and rng.random() < p_innovate:
                f.cash -= 0.12
                f.productivity *= 1.08
                f.innovative = True
            elif f.innovative and rng.random() < 0.03:
                f.innovative = False
                f.productivity *= 0.99
            low_runway = 1.0 / (1.0 + max(effective_runway, 0.0))
            credit_stress = f.debt / max(f.credit_limit, 1e-6)
            input_stress = unpaid_map[fid] / max(planned_inputs[fid], 1e-6)
            p_exit = min(0.65, 0.015 + 0.12 * low_runway + 0.10 * min(credit_stress, 2.0) + 0.16 * input_stress)
            if f.cash < 0.02 and f.unused_credit < 0.02:
                p_exit = max(p_exit, 0.55)
            if rng.random() < p_exit:
                f.alive = False
                exits.append(fid)
            else:
                active_for_stats.append(f)

        # Stage 4: supplier graph adapts after exits; entry is endogenous to vacancies,
        # with a bounded replacement rule rather than a fixed entry cost/hysteresis.
        _rewire(firms, rng, substitutability)
        active_count = sum(f.alive for f in firms.values())
        vacancies = max(0, n_initial - active_count)
        entrants = min(vacancies, max(0, max_population - active_count), int(rng.poisson(1.0)))
        for _ in range(entrants):
            entrant = _make_firm(next_id, rng, False, initial_cash_scale, cash_dispersion, credit_scale)
            candidates = [i for i, f in firms.items() if f.alive]
            chosen = list(rng.choice(candidates, size=min(3, len(candidates)), replace=False)) if candidates else []
            entrant.suppliers = _weights(chosen)
            firms[next_id] = entrant
            next_id += 1
        _rewire(firms, rng, substitutability)

        survivors = [f for f in firms.values() if f.alive]
        n_alive = len(survivors)
        total_sales = sum(sales_map.get(f.fid, 0.0) for f in active if f.fid not in exits)
        total_arrears = sum(sum(a for _, a in f.receivables) for f in survivors)
        total_unpaid = sum(unpaid_map.get(f.fid, 0.0) for f in active if f.fid not in exits)
        innov_share = (sum(f.innovative for f in survivors) / n_alive) if n_alive else np.nan
        avg_productivity = float(np.mean([f.productivity for f in survivors])) if n_alive else np.nan
        avg_runway = float(np.mean([(f.cash + f.unused_credit) / 0.15 for f in survivors])) if n_alive else np.nan
        # Concentration: HHI of supplier appearances; higher values indicate a more
        # concentrated set of dependencies, not necessarily causal vulnerability.
        supplier_counts = {}
        for f in survivors:
            for sid in f.suppliers:
                if sid in firms and firms[sid].alive:
                    supplier_counts[sid] = supplier_counts.get(sid, 0) + 1
        vals = np.array(list(supplier_counts.values()), dtype=float)
        hhi = float(np.sum((vals / vals.sum()) ** 2)) if vals.size and vals.sum() else 0.0
        edge_count = sum(len([sid for sid in f.suppliers if sid in firms and firms[sid].alive]) for f in survivors)
        records.append({
            "period": t, "seed": seed, "payment_delay": payment_delay,
            "substitutability": substitutability, "government_channel": government_channel,
            "innovation_support": innovation_support, "active_firms": n_alive,
            "active_share_initial": n_alive / n_initial,
            "exit_count": len(exits), "entry_count": entrants,
            "innovative_share": innov_share, "mean_productivity": avg_productivity,
            "mean_liquidity_buffer": avg_runway, "public_arrears": total_arrears,
            "unpaid_supplier_inputs": total_unpaid, "supplier_hhi": hhi,
            "potential_sales": sum(potential_sales_map.get(f.fid, 0.0) for f in active if f.fid not in exits),
            "realized_sales": total_sales,
            "input_rationing_share": (sum(unpaid_map.get(f.fid, 0.0) for f in active if f.fid not in exits) / max(sum(planned_inputs.get(f.fid, 0.0) for f in active if f.fid not in exits), 1e-9)),
            "active_edges": edge_count, "sales_survivors": total_sales,
            "mean_network_degree": edge_count / n_alive if n_alive else np.nan,
        })
        if return_micro:
            for f in survivors:
                outstanding = sum(a for _, a in f.receivables)
                omega = math.exp(-0.35 * payment_delay) if government_channel else 0.0
                burn_proxy = (0.17 + (wage_share + 0.42) * max(sales_map.get(f.fid, f.productivity), 0.05)) * operating_cost_scale
                runway = (f.cash + f.unused_credit + omega * outstanding) / burn_proxy
                micro_records.append({
                    "period": t, "firm_id": f.fid, "alive": f.alive,
                    "cash": f.cash, "debt": f.debt, "unused_credit": f.unused_credit,
                    "public_receivables": outstanding, "effective_runway": runway,
                    "cash_runway_days": (f.cash / burn_proxy) * period_days,
                    "effective_runway_days": runway * period_days,
                    "innovative": int(f.innovative), "productivity": f.productivity,
                    "supplier_degree": sum(1 for sid in f.suppliers if sid in firms and firms[sid].alive),
                    "unpaid_inputs": f.unpaid_inputs, "age": f.age,
                    "realized_sales": sales_map.get(f.fid, 0.0),
                    "potential_sales": potential_sales_map.get(f.fid, 0.0),
                    "production_scale": (sales_map.get(f.fid, 0.0) / max(potential_sales_map.get(f.fid, 0.0), 1e-9)),
                    "payment_delay": payment_delay, "substitutability": substitutability,
                    "initial_cash_scale": initial_cash_scale, "cash_dispersion": cash_dispersion,
                    "credit_scale": credit_scale, "operating_cost_scale": operating_cost_scale,
                    "wage_share": wage_share,
                    "government_channel": government_channel, "seed": seed,
                })
    aggregate = pd.DataFrame(records)
    if return_micro:
        return aggregate, pd.DataFrame(micro_records)
    return aggregate


def run_factorial(seeds=(11, 23, 37), steps=50, n_initial=80) -> pd.DataFrame:
    """Small pre-registered design: delay x substitutability x government-channel x seed."""
    out = []
    for seed in seeds:
        for delay in (0, 2, 4):
            for sub in (0.15, 0.85):
                for gov in (True, False):
                    out.append(simulate_abm(seed=seed, n_initial=n_initial, steps=steps,
                                            payment_delay=delay, substitutability=sub,
                                            government_channel=gov))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def summarize_factorial(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    final = df.sort_values("period").groupby(
        ["seed", "payment_delay", "substitutability", "government_channel"], as_index=False
    ).tail(1)
    return final.groupby(["payment_delay", "substitutability", "government_channel"], as_index=False).agg(
        runs=("seed", "nunique"), mean_active_share=("active_share_initial", "mean"),
        sd_active_share=("active_share_initial", "std"), mean_innovative_share=("innovative_share", "mean"),
        mean_productivity=("mean_productivity", "mean"), mean_arrears=("public_arrears", "mean"),
        mean_unpaid_inputs=("unpaid_supplier_inputs", "mean"), mean_supplier_hhi=("supplier_hhi", "mean")
    )


def project_to_runway_bins(micro: pd.DataFrame, bins=(0.0, 0.5, 1.0, 2.0, 4.0, float("inf"))) -> pd.DataFrame:
    """Project agent microstates onto runway x routine states and estimate transitions.

    Entrants and exits are not silently treated as routine switches: the output separately
    reports observed within-firm transitions among firms present in consecutive snapshots.
    This empirical projection is diagnostic and need not be Markovian.
    """
    if micro.empty:
        return pd.DataFrame(columns=["from_state", "to_state", "count", "probability"])
    d=micro.copy()
    labels=[f"R{i}" for i in range(len(bins)-1)]
    d["runway_bin"]=pd.cut(d["effective_runway"], bins=bins, labels=labels, include_lowest=True, right=False)
    d["state"]=d["runway_bin"].astype(str)+"_I"+d["innovative"].astype(str)
    d=d.sort_values(["firm_id","period"])
    d["next_period"]=d.groupby("firm_id")["period"].shift(-1)
    d["next_state"]=d.groupby("firm_id")["state"].shift(-1)
    pairs=d[d["next_period"]==d["period"]+1].dropna(subset=["next_state"])
    counts=pairs.groupby(["state","next_state"], observed=False).size().rename("count").reset_index()
    counts=counts.rename(columns={"state":"from_state","next_state":"to_state"})
    if counts.empty: return counts.assign(probability=pd.Series(dtype=float))
    counts["probability"]=counts["count"]/counts.groupby("from_state")["count"].transform("sum")
    return counts
