#!/usr/bin/env python3
"""
chart_05b_funding_summary.py — Section 5, funding structural summary.

Two robust, spike-resistant comparisons of HYPE vs BTC perp funding over the
structural window (May 1 - Jun 1, i.e. excluding the early-June spike):
  - median daily funding (the typical cost of staying long)
  - % of days funding was positive (persistence of long-side demand)

Both separate HYPE from BTC cleanly: HYPE's perp ran a higher carry AND was
positive far more consistently - a structurally more one-directional, long-
biased market. (We deliberately do NOT chart funding/return correlation or
skew: at n=31 those are not statistically robust.)

Source: Hyperliquid API. Window excludes Jun 2-5 spike.
Run:  pipenv run python scripts/chart_05b_funding_summary.py
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import funding_daily

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")
START = pd.Timestamp("2026-05-01", tz="UTC")
END = pd.Timestamp("2026-06-01", tz="UTC")


def main():
    fd = funding_daily(cutoff=False)
    fd = fd[(fd.date >= START) & (fd.date <= END)]

    stats = {}
    for c in ("HYPE", "BTC"):
        f = fd[fd.coin == c].funding_annualized_pct
        stats[c] = {"median": f.median(), "pct_pos": 100.0 * (f > 0).mean()}

    fig, ax = cs.new_figure()

    # Two metric groups on one axis is unit-mismatched, so use two sub-positions
    # with a shared y in "value" terms but labelled per metric. Simplest honest
    # layout: 4 bars, grouped in 2 pairs, each pair labelled beneath.
    groups = [("Median daily funding\n(annualized)", "median", "%"),
              ("Days funding was positive", "pct_pos", "%")]
    xpos = [0, 1]      # group centers
    w = 0.34
    for gi, (glabel, key, unit) in enumerate(groups):
        hv, bv = stats["HYPE"][key], stats["BTC"][key]
        ax.bar(gi - w/2, hv, width=w, color=cs.ACCENT, zorder=3,
               label="HYPE" if gi == 0 else None)
        ax.bar(gi + w/2, bv, width=w, color=cs.ACCENT3, zorder=3,
               label="BTC" if gi == 0 else None)
        for xx, vv in [(gi - w/2, hv), (gi + w/2, bv)]:
            ax.text(xx, vv + 1.5, f"{vv:.0f}{unit}", ha="center", va="bottom",
                    family=cs.MONO, fontsize=12, color=cs.INK, weight="bold")

    cs.style_axes(ax)
    ax.set_xticks(xpos)
    ax.set_xticklabels([g[0] for g in groups], fontsize=11, color=cs.INK)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100"], family=cs.MONO, fontsize=10)
    ax.set_ylabel("value (% funding / % of days)", fontsize=9.5,
                  color=cs.SUBINK, family=cs.BODY)
    ax.legend(loc="upper right", frameon=False, fontsize=11,
              prop={"family": cs.BODY})

    cs.header(fig,
              "Perp funding, structural summary \u00b7 Hyperliquid",
              "HYPE longs paid more, and paid it almost every day",
              "HYPE vs BTC, May 1 \u2013 Jun 1 (before the June spike)")
    cs.footer(fig, "Source: Hyperliquid API \u00b7 daily-mean funding; median and share of positive days")

    cs.save(fig, "05b_funding_summary", CHARTS)


if __name__ == "__main__":
    main()
