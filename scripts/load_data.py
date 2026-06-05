#!/usr/bin/env python3
"""
load_data.py — single source of truth for reading every dataset.

Conventions:
  * ANALYSIS_CUTOFF (2026-06-02): trend series (price/TVL/funding) trimmed here
    so the Jun 3-4 selloff doesn't distort the launch-window story. Full data
    stays on disk; pass cutoff=False for the closing coda / June-2-onward work.
  * Flow data: daily_flows.csv (transcribed from the SoSoValue dashboard, the
    primary source) is authoritative. Weekly totals are DERIVED from it so the
    weekly and daily charts can never disagree.
  * Funding timestamps are mixed ISO8601; parsed with format='ISO8601', utc.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

ANALYSIS_CUTOFF = pd.Timestamp("2026-06-02", tz="UTC")

LAUNCHES = {
    "THYP": pd.Timestamp("2026-05-12", tz="UTC"),
    "BHYP": pd.Timestamp("2026-05-15", tz="UTC"),
    "HYPG": pd.Timestamp("2026-06-03", tz="UTC"),
}

WEEK_BUCKETS = [
    ("Week 1",       "2026-05-12", "2026-05-15", True),
    ("Week 2",       "2026-05-18", "2026-05-22", False),
    ("Week 3",       "2026-05-26", "2026-05-29", False),
    ("Early June",   "2026-06-01", "2026-06-04", True),
]


def _path(name):
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing data file: {p}. Run fetch_data.py first.")
    return p


# ---- curated / transcribed -------------------------------------------------
def load_products():
    return pd.read_csv(_path("products.csv"))


def load_daily_flows():
    df = pd.read_csv(_path("daily_flows.csv"))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    for c in ("daily_net_inflow_usd_m", "cumulative_usd_m",
              "value_traded_usd_m", "net_assets_usd_m"):
        df[c] = pd.to_numeric(df[c])
    return df.sort_values("date").reset_index(drop=True)


def weekly_from_daily():
    daily = load_daily_flows()
    rows, cum = [], 0.0
    for label, start, end, partial in WEEK_BUCKETS:
        s = pd.Timestamp(start, tz="UTC")
        e = pd.Timestamp(end, tz="UTC")
        wk = daily[(daily.date >= s) & (daily.date <= e)]
        net = wk.daily_net_inflow_usd_m.sum()
        cum += net
        rows.append({
            "week_label": label, "period_start": start, "period_end": end,
            "net_inflow_usd_m": round(net, 2), "cumulative_usd_m": round(cum, 2),
            "is_partial": "yes" if partial else "no",
        })
    return pd.DataFrame(rows)


def load_weekly():
    return weekly_from_daily()


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


# ---- fetched live ----------------------------------------------------------
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
    df = pd.read_csv(_path("funding_history.csv"))
    df["time"] = pd.to_datetime(df["time"], format="ISO8601", utc=True)
    df["funding_rate"] = pd.to_numeric(df["funding_rate"])
    df["premium"] = pd.to_numeric(df["premium"], errors="coerce")
    df["funding_annualized_pct"] = df["funding_rate"] * 24 * 365 * 100
    df = df.sort_values(["coin", "time"])
    if cutoff:
        df = df[df["time"] <= ANALYSIS_CUTOFF]
    return df.reset_index(drop=True)


def funding_daily(cutoff=True):
    df = load_funding(cutoff=cutoff).copy()
    df["date"] = df["time"].dt.floor("D")
    return (df.groupby(["coin", "date"])
              .agg(funding_rate=("funding_rate", "mean"),
                   funding_annualized_pct=("funding_annualized_pct", "mean"))
              .reset_index())


def funding_summary(coin, cutoff=True):
    s = load_funding(cutoff=cutoff)
    s = s[s["coin"] == coin]["funding_rate"]
    return {"n": len(s),
            "mean_annualized_pct": s.mean() * 24 * 365 * 100,
            "pct_positive": 100 * (s > 0).mean()}


def load_all(cutoff=True):
    return {
        "products": load_products(),
        "daily_flows": load_daily_flows(),
        "weekly": weekly_from_daily(),
        "issuer": load_issuer(),
        "absorption": load_absorption(),
        "prices_current": load_prices_current(),
        "mcap_history": load_mcap_history(cutoff=cutoff),
        "tvl": load_tvl(cutoff=cutoff),
        "funding": load_funding(cutoff=cutoff),
    }


if __name__ == "__main__":
    print(f"ANALYSIS_CUTOFF = {ANALYSIS_CUTOFF.date()}\n")
    print("=== weekly (derived from daily) ===")
    print(weekly_from_daily().to_string(index=False))
    d = load_daily_flows()
    print(f"\ndaily_flows: {len(d)} rows, cumulative ends at "
          f"${d.cumulative_usd_m.iloc[-1]:.2f}M")


# ---- per-fund flows (Farside) ----------------------------------------------
def load_fund_cumulative():
    """Per-fund CUMULATIVE net inflows (Farside). Full window from May 12.

    Source is separate from the SoSoValue combined series; the two trackers
    differ by a few percent (methodology). Use Farside for per-fund views.
    """
    df = pd.read_csv(_path("cumulative_flows_by_fund.csv"))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    for c in ("bhyp_cum_usd_m", "thyp_cum_usd_m", "hypg_cum_usd_m"):
        df[c] = pd.to_numeric(df[c])
    return df.sort_values("date").reset_index(drop=True)


def fund_daily_from_cumulative():
    """Derive per-fund DAILY net inflows by differencing the cumulative series,
    so daily and cumulative can never disagree (single source of truth)."""
    cum = load_fund_cumulative().set_index("date")
    funds = ["bhyp_cum_usd_m", "thyp_cum_usd_m", "hypg_cum_usd_m"]
    daily = cum[funds].diff()
    daily.iloc[0] = cum[funds].iloc[0]  # first row: daily == initial cumulative
    daily.columns = ["bhyp_usd_m", "thyp_usd_m", "hypg_usd_m"]
    return daily.round(2).reset_index()
