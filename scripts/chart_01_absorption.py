#!/usr/bin/env python3
"""
chart_01_absorption.py — Section 1 hook (Chart 1 of 2).

Reproduces a PUBLISHED figure from Kairos Research (X post, ~May 25 2026):
spot HYPE ETFs absorbed 1.04% of HYPE's market cap in their first 10 trading
days, vs BTC 0.59% / ETH 0.41% / SOL 0.31%, using a new-issuer cohort
(excluding GBTC/ETHE legacy-trust outflows), normalized by each asset's market
cap at launch.

IMPORTANT: This chart REPRODUCES Kairos's published numbers. It is NOT an
independent computation by this repo — we do not have the historical first-10-day
flow data for the 2024 BTC/ETH launches to recompute it. Attribution and a link
to the primary source belong in the article caption.

Run:  pipenv run python scripts/chart_01_absorption.py
"""
import os
import sys
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import load_absorption

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")


def main():
    df = load_absorption()
    df = df.sort_values("absorption_pct_10d", ascending=False).reset_index(drop=True)

    fig, ax = cs.new_figure()
    xs = range(len(df))
    colors = [cs.ACCENT if a == "HYPE" else cs.MUTE for a in df.asset]
    bars = ax.bar(xs, df.absorption_pct_10d, color=colors, width=0.62, zorder=3)

    for b, a, v in zip(bars, df.asset, df.absorption_pct_10d):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.025, f"{v:.2f}%",
                ha="center", va="bottom", family=cs.MONO,
                fontsize=14 if a == "HYPE" else 12,
                color=cs.INK if a == "HYPE" else cs.SUBINK, weight="bold")

    ax.set_xticks(list(xs))
    ax.set_xticklabels(df.asset)
    for lbl, a in zip(ax.get_xticklabels(), df.asset):
        lbl.set_fontsize(12.5)
        if a == "HYPE":
            lbl.set_color(cs.ACCENT)
            lbl.set_weight("bold")
        else:
            lbl.set_color(cs.INK)

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.2f}%"))
    ax.set_ylim(0, max(df.absorption_pct_10d) * 1.18)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO)
        lbl.set_fontsize(11)

    cs.header(fig,
              "ETF debut · first 10 trading days · per Kairos Research",
              "HYPE set a crypto-ETF debut record",
              "Net inflows as a share of token market cap at launch (new-issuer cohort)")
    cs.footer(fig, "Source: Kairos Research (@Kairos_Res), May 27 2026 · reproduced")

    cs.save(fig, "01_absorption", CHARTS)


if __name__ == "__main__":
    main()
