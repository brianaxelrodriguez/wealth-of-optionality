"""Reproduce key integrity and descriptive checks for bundled research data."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    raw_arg = DATA / "raw" / "liquidez_corporativa_ARG_Argentina.csv"
    raw_all = DATA / "raw" / "liquidez_corporativa_TODOS_LOS_PAISES.csv"
    audited = DATA / "processed" / "audited_listed_firm_liquidity.csv"
    panel = DATA / "processed" / "country_panel_wdi_pwt.csv"
    summary = json.loads((DATA / "processed" / "liquidity_audit.json").read_text(encoding="utf-8"))
    df = pd.read_csv(audited)
    p = pd.read_csv(panel)
    out = {
        "source_files_identical": sha256(raw_arg) == sha256(raw_all),
        "source_sha256_argentina": sha256(raw_arg),
        "audited_rows": int(len(df)),
        "audited_tickers": int(df["ticker"].nunique()),
        "panel_rows": int(len(p)),
        "panel_economies": int(p["iso3"].nunique()),
        "panel_year_min": int(p["year"].min()),
        "panel_year_max": int(p["year"].max()),
        "audit_summary_consistent_with_source": summary["source_sha256"] == sha256(raw_arg),
        "interpretation": "Integrity and descriptive checks only; no causal or structural identification."
    }
    target = DATA / "processed" / "reproducibility_audit.json"
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
