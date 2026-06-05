#!/usr/bin/env python3
"""
fetch_data.py — pull every LIVE figure the article needs, from free/keyless APIs.

Sources (all free, no payment method required):
  1. CoinGecko (keyless)      -> HYPE/BTC/ETH/SOL spot price + market cap (current)
  2. CoinGecko (keyless)      -> HYPE market-cap history (for the timeline chart)
  3. DeFiLlama (keyless)      -> Hyperliquid protocol TVL history
  4. Hyperliquid native API   -> HYPE & BTC funding-rate history (paginated to now)

Fetch once, cache to CSV. Charts read the CSVs, not the API.

Usage:
    pipenv run python scripts/fetch_data.py

Optional free CoinGecko Demo key (more stable). Set before running:
    export COINGECKO_DEMO_KEY="CG-xxxx"
"""
import os
import sys
import time
import datetime as dt

try:
    import requests
    import pandas as pd
except ImportError:
    sys.exit("Install deps first:  pipenv install requests pandas")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

CG_BASE = "https://api.coingecko.com/api/v3"
LLAMA_BASE = "https://api.llama.fi"
HL_INFO = "https://api.hyperliquid.xyz/info"

COINS = {"hyperliquid": "HYPE", "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}

CG_PAUSE = 8

DEMO_KEY = os.environ.get("COINGECKO_DEMO_KEY")


def _cg_headers():
    return {"accept": "application/json",
            **({"x-cg-demo-api-key": DEMO_KEY} if DEMO_KEY else {})}


def _get(url, **kw):
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=30, **kw)
            if r.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"  rate-limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == 3:
                raise
            time.sleep(4 * (attempt + 1))
    return None


# 1. Current price + market cap (one call for all four)
def fetch_prices():
    print("[1/4] CoinGecko: current price + market cap ...")
    data = _get(f"{CG_BASE}/simple/price", headers=_cg_headers(), params={
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_change": "true",
    })
    rows = [{
        "ticker": COINS[cid],
        "coingecko_id": cid,
        "price_usd": data[cid].get("usd"),
        "market_cap_usd": data[cid].get("usd_market_cap"),
        "change_24h_pct": data[cid].get("usd_24h_change"),
        "fetched_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    } for cid in COINS]
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "prices_current.csv")
    df.to_csv(out, index=False)
    print(f"      -> {out}")
    return df


# 2. HYPE market-cap history for the timeline chart
def fetch_hype_mcap_history(days=90):
    print(f"[2/4] CoinGecko: HYPE market-cap history ({days}d) ...")
    time.sleep(CG_PAUSE)
    data = _get(f"{CG_BASE}/coins/hyperliquid/market_chart",
                headers=_cg_headers(),
                params={"vs_currency": "usd", "days": days, "interval": "daily"})
    caps = data.get("market_caps", [])
    prices = data.get("prices", [])
    df = pd.DataFrame({
        "date": [dt.datetime.fromtimestamp(c[0] / 1000, dt.UTC).date() for c in caps],
        "market_cap_usd": [c[1] for c in caps],
        "price_usd": [p[1] for p in prices] if len(prices) == len(caps) else None,
    })
    # CoinGecko appends the current (incomplete) day onto the daily series,
    # producing a duplicate date. Keep the LAST row for each date (most recent).
    df = df.drop_duplicates(subset="date", keep="last").reset_index(drop=True)
    out = os.path.join(DATA_DIR, "hype_mcap_history.csv")
    df.to_csv(out, index=False)
    print(f"      -> {out} ({len(df)} rows)")
    return df


# 3. Hyperliquid protocol TVL history (DeFiLlama)
def fetch_hyperliquid_tvl():
    print("[3/4] DeFiLlama: Hyperliquid TVL history ...")
    data = _get(f"{LLAMA_BASE}/protocol/hyperliquid")
    tvl = data.get("tvl", [])
    df = pd.DataFrame([
        {"date": dt.datetime.fromtimestamp(p["date"], dt.UTC).date(),
         "tvl_usd": p["totalLiquidityUSD"]}
        for p in tvl
    ])
    out = os.path.join(DATA_DIR, "hyperliquid_tvl.csv")
    df.to_csv(out, index=False)
    print(f"      -> {out} ({len(df)} rows)")
    return df


# 4. Funding-rate history from Hyperliquid's OWN API (HYPE + BTC), paginated
def fetch_funding(coin, days=35):
    """Paginate forward through Hyperliquid funding history to 'now'.

    The API returns at most ~500 records per call, oldest-first from startTime.
    We page forward (advancing startTime past the last row each loop) until we
    reach the present, so the series is complete AND current.
    """
    now_ms = int(dt.datetime.now(dt.UTC).timestamp() * 1000)
    cursor = now_ms - days * 24 * 60 * 60 * 1000
    rows = []
    seen = set()
    while cursor < now_ms:
        payload = {"type": "fundingHistory", "coin": coin, "startTime": cursor}
        batch = requests.post(HL_INFO, json=payload, timeout=30,
                              headers={"Content-Type": "application/json"}).json()
        if not batch:
            break
        new = [r for r in batch if r["time"] not in seen]
        if not new:
            break
        for r in new:
            seen.add(r["time"])
            rows.append({
                "coin": r["coin"],
                "time": dt.datetime.fromtimestamp(r["time"] / 1000, dt.UTC),
                "funding_rate": float(r["fundingRate"]),
                "premium": float(r["premium"]),
            })
        cursor = max(r["time"] for r in new) + 1
        time.sleep(0.3)  # be polite to the API
    return pd.DataFrame(rows)


def fetch_funding_both(days=35):
    print(f"[4/4] Hyperliquid API: funding history HYPE + BTC ({days}d, paginated) ...")
    frames = []
    for coin in ("HYPE", "BTC"):
        try:
            f = fetch_funding(coin, days)
            frames.append(f)
            rng = f"{f['time'].min()} -> {f['time'].max()}" if len(f) else "empty"
            print(f"      {coin}: {len(f)} rows  ({rng})")
        except Exception as e:
            print(f"      {coin}: FAILED ({e})")
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    out = os.path.join(DATA_DIR, "funding_history.csv")
    df.to_csv(out, index=False)
    print(f"      -> {out} ({len(df)} rows total)")
    return df


if __name__ == "__main__":
    print("Fetching live data (all free, keyless). Caching to ../data/*.csv\n")
    results = {}
    for name, fn in [("prices", fetch_prices),
                     ("mcap_history", fetch_hype_mcap_history),
                     ("tvl", fetch_hyperliquid_tvl),
                     ("funding", fetch_funding_both)]:
        try:
            results[name] = fn()
        except Exception as e:
            print(f"  !! {name} failed: {e}\n     (other sources will still run)")
    print("\nDone. Fetched:", ", ".join(k for k, v in results.items() if v is not None))
    if "prices" in results and results["prices"] is not None:
        print("\nCurrent snapshot:")
        print(results["prices"].to_string(index=False))


# 5. Price-comparison history (HYPE + BTC) for the Section 5 relative-fall panel.
#    Separate from fetch_hype_mcap_history so the existing price-timeline data
#    (hype_mcap_history.csv) is never disturbed. Long format, both coins.
def fetch_price_compare(days=45):
    print(f"[5] CoinGecko: HYPE + BTC price history ({days}d) for comparison panel ...")
    frames = []
    for cg_id, sym in [("hyperliquid", "HYPE"), ("bitcoin", "BTC")]:
        time.sleep(CG_PAUSE)
        data = _get(f"{CG_BASE}/coins/{cg_id}/market_chart",
                    headers=_cg_headers(),
                    params={"vs_currency": "usd", "days": days, "interval": "daily"})
        prices = data.get("prices", [])
        df = pd.DataFrame({
            "date": [dt.datetime.fromtimestamp(p[0] / 1000, dt.UTC).date() for p in prices],
            "coin": sym,
            "price_usd": [p[1] for p in prices],
        })
        df = df.drop_duplicates(subset="date", keep="last")
        frames.append(df)
        rng = f"{df['date'].min()} -> {df['date'].max()}" if len(df) else "empty"
        print(f"      {sym}: {len(df)} rows  ({rng})")
    out_df = pd.concat(frames, ignore_index=True)
    out = os.path.join(DATA_DIR, "price_compare.csv")
    out_df.to_csv(out, index=False)
    print(f"      -> {out} ({len(out_df)} rows total)")
    return out_df
