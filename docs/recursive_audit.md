# Recursive audit — 2026

## Recursion focus
This pass revisited the oldest available project archive (`The_Wealth_of_Optionality_2026-10-28_R2.zip`, 320 entries), rather than treating the compact manuscript as the sole source. The older archive contains a much broader figure inventory. Four legacy graphics were restored to the working tree: the WBES public-payment frequency figure and the PWT TFP-growth distribution in both language editions.

## Figure selection rule
The restored figures are descriptive or explicitly illustrative. More ambitious legacy figures on hysteresis, Krawczyk certificates, ROC/exit prediction, fiscal frontiers, and synthetic Kaldor effects were not reinserted automatically: their presence in an older archive is not evidence that their assumptions, code, or empirical claims have survived the current audit. They should only return after their generating scripts and evidentiary status are revalidated.

## Scientific limitations retained
- Lomax formulas are conditional on the specified tail distribution. Distribution-free monotonicity is stated separately; lognormal is a robustness alternative, not proof of universal functional-form invariance.
- The ABM dynamic calibration remains rejected as a fit: simulated runway expands markedly relative to accounting targets. No initial-condition retuning is used to conceal the discrepancy.
- No structural parameter estimate or causal estimate is reported. WDI/PWT and listed-firm accounting ratios are descriptive; WBES numbers come from public frequency tables, not a weighted microdata regression.
- The purported multi-country accounting file is byte-identical to the Argentina file and is not treated as multi-country evidence. The listed-firm sample has survival/selection and temporal-overlap limitations.
- No global bifurcation, hysteresis, or complete finite-dimensional micro–macro closure is claimed.

## PDF dating and audience
The title pages show only `2026`, without month or day. English remains the canonical GitHub edition; Spanish is retained as a parallel edition.

## Next release gate
Before restoring additional legacy figures, independently rerun their generating code, reconcile each plotted quantity with a source dataset, document whether the plot is theoretical, synthetic, or empirical, and remove any figure whose data provenance or mathematical interpretation cannot be verified.


## V3 decisions
- Removed the aggregate PWT/WDI TFP-growth section and figures from the manuscript; the data do not identify the short-run firm-level liquidity channel. Historical source files may remain for provenance only.
- Renamed the empirical section to emphasize the limits of public data; the accounting analysis is explicitly limited to 52 listed Argentine firms. The file labelled multi-country was audited as a structural duplicate and excluded from international inference.
- Reframed the ABM runway increase as a boundary-search diagnostic for missing surplus-allocation sinks, not as proof that standard frictions are generally insufficient.
- Added a linked-invoice protocol using a pre-treatment network matrix and staggered DiD; it remains a proposed design, not an executed estimate.


## V3 decisions
- Removed the aggregate PWT/WDI TFP-growth section and figures from the manuscript; the data do not identify the short-run firm-level liquidity channel. Historical source files may remain for provenance only.
- Renamed the empirical section to emphasize the limits of public data; the accounting analysis is explicitly limited to 52 listed Argentine firms. The file labelled multi-country was audited as a structural duplicate and excluded from international inference.
- Reframed the ABM runway increase as a boundary-search diagnostic for missing surplus-allocation sinks, not as proof that standard frictions are generally insufficient.
- Added a linked-invoice protocol using a pre-treatment network matrix and staggered DiD; it remains a proposed design, not an executed estimate.

## V3 release checks (2026)
- Reframed the ABM runway increase as a boundary-search diagnostic for missing surplus-allocation mechanisms; explicitly labels the proposed sinks as hypotheses, not established causes, and avoids claiming a general failure of standard literature frictions.
- Renamed the empirical section to emphasize public-data limits and restricts the accounting pilot to 52 Argentine listed firms; the purported multi-country file is explicitly noted as structurally duplicated and excluded from international inference.
- Removed the aggregate PWT/WDI TFP-growth section, figures, and evidence-inventory rows from the main manuscript.
- Added a pre-treatment network-matrix and staggered DiD protocol based on Callaway and Sant'Anna (2021); the design is clearly labelled proposed, not executed.
- Added the local fixed-active-set condition to the Grönwall trajectory bound and restricted the exit hazard to $h_0,\kappa\geq0$, $h_0+\kappa\leq1$.
- English PDF: 24 pages. Spanish PDF: 25 pages. Both compiled successfully; 11 tests passed.
