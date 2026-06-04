# HYPE ETF Research

Data, code, and charts behind a research piece on the US spot Hyperliquid (HYPE)
ETF launch — BHYP (Bitwise) and THYP (21Shares), with HYPG (Grayscale) and the
leveraged TXXH noted for context.

> **Disclosure.** This is my own independent research. It was not commissioned by,
> reviewed by, or undertaken on behalf of Bitwise, and it does not represent
> Bitwise's views. I do work at/with Bitwise, which issues one of the funds
> discussed (BHYP) — readers should weigh that affiliation for themselves.
>
> **All data used here is publicly sourced.** Nothing in this repository is
> private, internal, or proprietary to Bitwise. Every figure comes from public
> APIs (CoinGecko, DeFiLlama, the Hyperliquid API) or public reporting, and each
> data point carries its source so anyone can reproduce it.
>
> Not investment advice.

## Setup
```bash
pipenv install
pipenv shell
python scripts/fetch_data.py     # pull live price/TVL/funding (free, keyless)
python scripts/load_data.py      # verify datasets load
```

## Data provenance
- Price / market cap / history: CoinGecko (free, keyless, public)
- Hyperliquid TVL: DeFiLlama (free, keyless, public)
- HYPE & BTC funding history: Hyperliquid native API (free, keyless, public)
- ETF net flows: compiled from public SoSoValue reporting (no free API exists);
  each row carries a source. Figures marked "reported" need primary verification.

Trend charts are trimmed to an analysis cutoff (see `scripts/load_data.py`); the
recent market-wide selloff is handled separately in the article.
