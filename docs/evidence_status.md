# Evidence and claim audit

## Analytical claims retained

1. Distress probability is the survival function of the cash-loss distribution; monotonicity follows when the loss distribution has positive density.
2. Under a Lomax tail, distress probability, marginal risk reduction, elasticity, and convexity have the closed forms shown in the manuscript.
3. Under common burn and the stated Lomax specification, Jensen's inequality implies that expected distress is at least distress evaluated at mean runway; this is a mathematical aggregation result, not a causal claim.
4. If payment delay weakly reduces the fraction of receivables monetizable before obligations fall due, effective runway weakly decreases; the sign for exit hazard follows only under the stated monotone hazard specification.
5. A nonnegative linear network multiplier exists under the spectral-radius condition `rho(beta W) < 1`. It is a frozen-network, short-run local multiplier before exit thresholds, switching, or renegotiation change the system.
6. Exact moment closure is equivalent to constancy of `S o T` on each fiber of the aggregation map.
7. The bin integration bound and the Gronwall trajectory bound require distinct assumptions; neither establishes a bifurcation.
8. The Bellman formulation is a template, not a solved dynamic program: transition laws, pricing, default/liquidation, and entry must be specified before equilibrium claims.
9. The ABM now makes realized sales depend on the share of planned intermediate inputs financed before current-period production. The input constraint is a stylized proportional technology; it is not a calibrated production function or evidence of real-world propagation.

## Claims explicitly not made

- No universal claim that liquidity dominates productivity.
- No claim of a certified fold or general hysteresis in the microfounded distributional system.
- No structural parameter estimate from WDI/PWT or listed-firm accounting ratios.
- No causal estimate of public payment delays, reverse causality, or supplier-network spillovers.
- No successful dynamic calibration of the agent-based model.
- No structural interpretation of ABM productivity/network outcomes beyond the stylized mechanism encoded in the code.

## Data constraints

The listed-firm pilot contains 537 reports for 52 Argentine tickers. Its purported consolidated multi-country CSV is byte-identical to the Argentina CSV. It has no invoice-level due dates, actual payment dates, public-contract exposure, counterparties, or observed firm exits. The PWT/WDI panel supports descriptive macroeconomic context but does not measure the firm-level mechanism.

## Endogeneity audit

The paper distinguishes: (a) delay-to-liquidity causality; (b) reverse causality from firm condition to certification/payment timing and supplier terms; (c) common causes such as fiscal stress and sectoral demand; (d) endogenous network adjustment; (e) mediation through runway; and (f) selection into listed/surviving samples. A future causal design must define the estimand, pre-shock exposure, event or instrument, interference mapping, and falsification tests before estimation.


## V3 scope decision
The PWT/WDI aggregate TFP-growth section and figures have been removed from the manuscript because they do not test the firm-level liquidity mechanism. Historical files remain in the repository for provenance, not as evidence used in the paper. The purported multi-country accounting file was audited as a duplicate of the Argentina file and is excluded from cross-country claims.


## V3 scope decision
The PWT/WDI aggregate TFP-growth section and figures have been removed from the manuscript because they do not test the firm-level liquidity mechanism. Historical files remain in the repository for provenance, not as evidence used in the paper. The purported multi-country accounting file was audited as a duplicate of the Argentina file and is excluded from cross-country claims.
