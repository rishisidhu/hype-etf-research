# HYPE ETF Research

Data, code, and charts behind a research piece on the US spot Hyperliquid (HYPE)
ETF launch — BHYP (Bitwise) and THYP (21Shares), with HYPG (Grayscale) and the
leveraged TXXH noted for context.

> Disclosure: the author works at/with Bitwise, issuer of BHYP. Analysis aims to
> be even-handed; every figure is sourced. Not investment advice.

## Setup
```bash
pipenv install
pipenv shell
python scripts/fetch_data.py     # pull live price/TVL/funding (free, keyless)
python scripts/load_data.py      # verify datasets load
```

## Data provenance
- Price / market cap / history: CoinGecko (free, keyless)
- Hyperliquid TVL: DeFiLlama (free, keyless)
- HYPE & BTC funding history: Hyperliquid native API (free, keyless)
- ETF net flows: compiled from public SoSoValue reporting (no free API exists);
  each row carries a source. Figures marked "reported" need primary verification.

Trend charts are trimmed to an analysis cutoff (see `scripts/load_data.py`); the
recent market-wide selloff is handled separately.
