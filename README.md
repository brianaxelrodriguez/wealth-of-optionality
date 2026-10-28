# The Wealth of Optionality

**Primary language: English.** The English manuscript is the canonical edition for international readers and collaborators. A Spanish-language edition is maintained in parallel for Spanish-speaking readers; the theory, evidence labels, code, and replication protocol should remain substantively aligned across editions.

## Research question and contribution

How does accessible liquidity change the set of actions available to heterogeneous firms, and under what conditions can payment delays transmit financial stress through production networks? The paper develops conditional analytical results for liquidity distress under a Lomax shock distribution, the local propagation of shocks over a fixed network, exact aggregation by moments, and error bounds for distributional approximations. It separates those results from claims that require a solved dynamic equilibrium, validated microdata, or a credible causal design.

The paper does **not** claim a universal liquidity-dominates-productivity result, a globally certified bifurcation or hysteresis result, a structural estimate from national accounts, or a causal effect of public payment delays.

## Start here

1. [`manuscript/The_Wealth_of_Optionality_EN.pdf`](manuscript/The_Wealth_of_Optionality_EN.pdf) — primary manuscript.
2. [`manuscript/The_Wealth_of_Optionality_EN.tex`](manuscript/The_Wealth_of_Optionality_EN.tex) — editable LaTeX source.
3. [`docs/evidence_status.md`](docs/evidence_status.md) — evidence status and explicit limits.
4. [`docs/source_material_audit.md`](docs/source_material_audit.md) — source-material audit.
5. [`README_ES.md`](README_ES.md) — Spanish-language repository guide.

## Repository map

- `manuscript/`: English primary edition and Spanish companion edition, including PDF and LaTeX sources.
- `src/optionality_model.py`: deterministic analytical functions and conditional error bounds.
- `src/firm_simulator.py`: transparent agent-based mechanism laboratory. Realized sales are now constrained by the share of planned intermediate inputs that can be financed before production; this is a stylized mechanism, not an estimated production technology.
- `src/calibrate_initial_state.py`: initial-state moment fit and out-of-fit dynamic diagnostic.
- `src/bin_diagnostics.py`: numerical projection diagnostic for runway integrands.
- `src/audit_data.py`: integrity and descriptive checks for bundled data.
- `src/paper_figures.py`: reproducible figures with shared typography and axis sizing.
- `data/raw/`: archived source data.
- `data/processed/`: matched panels and derived descriptive tables.
- `figures/`: figures used in the Spanish and English manuscripts.
- `tests/`: unit tests, including the ABM production-constraint invariant.
- `SHA256SUMS.csv`: SHA-256 integrity manifest.

## Reproduce

Run from the repository root:

```bash
python -m pip install -r requirements.txt
python src/audit_data.py
python src/calibrate_initial_state.py
python src/bin_diagnostics.py
python src/paper_figures.py
python -m pytest -q
cd manuscript
pdflatex -interaction=nonstopmode La_riqueza_de_la_opcionalidad_ES.tex
pdflatex -interaction=nonstopmode La_riqueza_de_la_opcionalidad_ES.tex
pdflatex -interaction=nonstopmode The_Wealth_of_Optionality_EN.tex
pdflatex -interaction=nonstopmode The_Wealth_of_Optionality_EN.tex
```

The tests check mathematical functions and selected implementation invariants. They do not certify the global dynamic system, establish exact micro–macro closure for the economic model, or identify causal effects.

## Evidence status

- **Analytical results:** valid under the distributional, feasibility, stability, and regularity assumptions stated in the manuscript.
- **Macroeconomic series:** descriptive growth statistics for the Penn World Table national-price TFP index; not a newly estimated Solow residual and not a causal test.
- **Listed-firm accounting pilot:** descriptive ratios for selected Argentine listed firms; not representative of all firms and not linked to invoices, actual payment dates, counterparties, or exits.
- **ABM:** the production constraint now links realized sales to financed inputs. Other behavioral rules remain stylized; the dynamic runway fit remains a diagnostic and is not presented as successful calibration.
- **Causality:** no causal estimate is reported. A credible design requires linked transaction/payment data and defensible exogenous variation.

## Citation

Rodriguez, Brian Axel. *The Wealth of Optionality: Liquidity, Financial Selection, and Shock Propagation in Production Networks*. Working paper, 2026. See [`CITATION.cff`](CITATION.cff).

## V3 methodological scope
The manuscript excludes aggregate PWT/WDI TFP-growth analysis because it does not test the short-run firm-level liquidity mechanism. The empirical section is limited to a descriptive pilot of 52 listed Argentine firms. A file labelled multi-country was audited as a structural duplicate of the Argentina file and is excluded from international inference. The ABM runway increase is treated as a boundary-search diagnostic for missing surplus-allocation mechanisms, not as a validated theoretical result. The proposed invoice-data design uses a pre-treatment network matrix and staggered difference-in-differences; it is not an executed estimate.
