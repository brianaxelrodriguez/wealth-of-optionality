"""Regenerate the descriptive and theoretical figures used in both manuscripts."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Shared visual system for every figure in both language editions.
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "lines.linewidth": 1.6,
    "figure.dpi": 180,
    "savefig.dpi": 220,
})

ROOT = Path(__file__).resolve().parents[1]
FIG_ES = ROOT / "figures"
FIG_EN = ROOT / "figures" / "en"
DATA = ROOT / "data" / "processed"
FIG_ES.mkdir(parents=True, exist_ok=True)
FIG_EN.mkdir(parents=True, exist_ok=True)


def draw_runway(path: Path, english: bool):
    R = np.linspace(0, 10, 500)
    burn, scale, shape = 1.0, 1.5, 1.5  # illustrative, not estimated
    q = (1 + burn * R / scale) ** (-shape)
    urgency = shape * burn / scale * (1 + burn * R / scale) ** (-shape - 1)
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.plot(R, q, label="Distress probability q(R)" if english else "Probabilidad de distress q(R)")
    ax.plot(R, urgency, label="Marginal risk reduction −q′(R)" if english else "Reducción marginal del riesgo −q′(R)")
    ax.set_xlabel("Accessible runway R (time units)" if english else "Runway accesible R (unidades de tiempo)")
    ax.set_ylabel("Probability / marginal response" if english else "Probabilidad / respuesta marginal")
    ax.set_title("Runway, distress risk, and urgency" if english else "Runway, riesgo de distress y urgencia")
    ax.legend(frameon=False)
    ax.grid(True, alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def draw_tfp(path: Path, english: bool):
    df = pd.read_csv(DATA / "annual_tfp_statistics.csv")
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.plot(df["year"], df["median_tfp_growth_log_pct"], marker="o", linewidth=1.5)
    ax.axhline(0, linewidth=.8)
    ax.set_xlabel("Year" if english else "Año")
    ax.set_ylabel(r"Median $100\,\Delta\log(\mathrm{rtfpna})$" if english else r"Mediana de $100\,\Delta\log(\mathrm{rtfpna})$")
    ax.set_title("Median annual PWT TFP-index growth" if english else "Crecimiento mediano anual del índice de PTF de PWT")
    ax.grid(True, alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def draw_liquidity(path: Path, english: bool):
    df = pd.read_csv(DATA / "audited_listed_firm_liquidity.csv")
    df = df[(df["frecuencia"] == "annual") & (~df["es_sector_financiero"].astype(bool))]
    cols = ["runway_liquidez_dias", "plazo_cobro_dso_dias", "plazo_pago_dpo_dias"]
    vals = [df[c].dropna().to_numpy(dtype=float) for c in cols]
    vals = [v[(v >= 0) & (v <= np.quantile(v, .95))] for v in vals]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.boxplot(vals, showfliers=False)
    ax.set_xticks([1, 2, 3], ["Strict runway (days)", "DSO (days)", "DPO (days)"] if english else ["Runway estricto (días)", "DSO (días)", "DPO (días)"])
    ax.set_ylabel("Days (each series visually truncated at its 95th percentile)" if english else "Días (cada serie truncada visualmente en su percentil 95)")
    ax.set_title("Listed nonfinancial firms: accounting ratios" if english else "Emisoras no financieras: ratios contables")
    ax.grid(True, axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    draw_runway(FIG_ES / "runway_urgency.png", False)
    draw_tfp(FIG_ES / "observed_tfp_growth.png", False)
    draw_liquidity(FIG_ES / "listed_firm_liquidity.png", False)
    draw_runway(FIG_EN / "runway_urgency.png", True)
    draw_tfp(FIG_EN / "observed_tfp_growth.png", True)
    draw_liquidity(FIG_EN / "listed_firm_liquidity.png", True)
