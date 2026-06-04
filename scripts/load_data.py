#!/usr/bin/env python3
"""
load_data.py — single source of truth for reading every dataset.

Every chart imports from here so there's one place that knows where data lives,
how it's typed, and where the analysis window ends.

Key conventions:
  * ANALYSIS_CUTOFF (2026-06-02): trend series are trimmed to this date so the
    June 3-4 market-wide selloff doesn't distort the launch-window story. Full
    data stays on disk and is reachable via cutoff=False for the closing coda.
  * Funding timestamps are mixed ISO8601 (some with microseconds); parsed with
    format='ISO8601', utc=True everywhere.

Usage:
    from load_data import load_all
    d = load_all()
Run directly to print a summary of every dataset:
    pipenv run python scripts/load_data.py
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Trend charts end here; the Jun 3-4 selloff is handled separately in the coda.
ANALYSIS_CUTOFF = pd.Timestamp("2026-06-02", tz="UTC")

# ETF launch dates, for annotating the market-cap timeline
LAUNCHES = {
    "THYP": pd.Timestamp("2026-05-12", tz="UTC"),
    "BHYP": pd.Timestamp("2026-05-15", tz="UTC"),
    "HYPG": pd.Timestamp("2026-06-03", tz="UTC"),
}


def _path(name):
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing data file: {p}. Run fetch_data.py first.")
    return p


# ---------------------------------------------------------------------------
# Curated ETF datasets
# ---------------------------------------------------------------------------
def load_products():
    return pd.read_csv(_path("products.csv"))


def load_weekly():
    df = pd.read_csv(_path("category_flows_weekly.csv"))
    df["net_inflow_usd_m"] = pd.to_numeric(df["net_inflow_usd_m"])
    df["cumulative_usd_m"] = pd.to_numeric(df["cumulative_usd_m"])
    return df


def load_issuer():
    df = pd.read_csv(_path("issuer_cumulative.csv"))
    for c in ("cumulative_inflow_usd_m", "aum_usd_m", "avg_daily_vol_usd_m"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def latest_issuer_inflows():
    df = load_issuer().sort_values("as_of_date")
    return df.groupby("ticker")["cumulative_inflow_usd_m"].last()


def load_absorption():
    df = pd.read_csv(_path("debut_absorption.csv"))
    df["absorption_pct_10d"] = pd.to_numeric(df["absorption_pct_10d"])
    return df


# ---------------------------------------------------------------------------
# Fetched live datasets
# ---------------------------------------------------------------------------
def load_prices_current():
    return pd.read_csv(_path("prices_current.csv"))


def load_mcap_history(cutoff=True):
    df = pd.read_csv(_path("hype_mcap_history.csv"))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df["market_cap_usd"] = pd.to_numeric(df["market_cap_usd"])
    df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
    df = df.drop_duplicates(subset="date", keep="last").sort_values("date")
    if cutoff:
        df = df[df["date"] <= ANALYSIS_CUTOFF]
    return df.reset_index(drop=True)


def load_tvl(cutoff=True):
    df = pd.read_csv(_path("hyperliquid_tvl.csv"))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df["tvl_usd"] = pd.to_numeric(df["tvl_usd"])
    df = df.sort_values("date")
    if cutoff:
        df = df[df["date"] <= ANALYSIS_CUTOFF]
    return df.reset_index(drop=True)


def load_funding(cutoff=True):
    """Hourly funding for HYPE + BTC. Adds annualized % column for readability."""
    df = pd.read_csv(_path("funding_history.csv"))
    df["time"] = pd.to_datetime(df["time"], format="ISO8601", utc=True)
    df["funding_rate"] = pd.to_numeric(df["funding_rate"])
    df["premium"] = pd.to_numeric(df["premium"], errors="coerce")
    # Hyperliquid funds hourly -> annualize for intuition
    df["funding_annualized_pct"] = df["funding_rate"] * 24 * 365 * 100
    df = df.sort_values(["coin", "time"])
    if cutoff:
        df = df[df["time"] <= ANALYSIS_CUTOFF]
    return df.reset_index(drop=True)


def funding_daily(cutoff=True):
    """Daily-averaged funding per coin (cleaner for the §5 comparison chart)."""
    df = load_funding(cutoff=cutoff).copy()
    df["date"] = df["time"].dt.floor("D")
    out = (df.groupby(["coin", "date"])
             .agg(funding_rate=("funding_rate", "mean"),
                  funding_annualized_pct=("funding_annualized_pct", "mean"))
             .reset_index())
    return out


def funding_summary(coin, cutoff=True):
    """Quick stats for prose: mean annualized, % positive."""
    s = load_funding(cutoff=cutoff)
    s = s[s["coin"] == coin]["funding_rate"]
    return {
        "n": len(s),
        "mean_annualized_pct": s.mean() * 24 * 365 * 100,
        "pct_positive": 100 * (s > 0).mean(),
    }


def load_all(cutoff=True):
    return {
        "products": load_products(),
        "weekly": load_weekly(),
        "issuer": load_issuer(),
        "absorption": load_absorption(),
        "prices_current": load_prices_current(),
        "mcap_history": load_mcap_history(cutoff=cutoff),
        "tvl": load_tvl(cutoff=cutoff),
        "funding": load_funding(cutoff=cutoff),
    }


if __name__ == "__main__":
    print(f"ANALYSIS_CUTOFF = {ANALYSIS_CUTOFF.date()} (trend series trimmed here)\n")
    d = load_all()
    for k, v in d.items():
        print(f"=== {k}: {len(v)} rows ===")
        if k in ("mcap_history", "tvl"):
            print(f"    {v['date'].min().date()} -> {v['date'].max().date()}")
        elif k == "funding":
            print(f"    {v['time'].min()} -> {v['time'].max()}")
        elif k in ("products", "weekly", "issuer", "absorption", "prices_current"):
            print(v.to_string(index=False)[:600])
        print()
    print("Funding summaries (through cutoff):")
    for coin in ("HYPE", "BTC"):
        s = funding_summary(coin)
        print(f"  {coin}: ann~{s['mean_annualized_pct']:.1f}%  "
              f"%pos={s['pct_positive']:.0f}%  n={s['n']}")
