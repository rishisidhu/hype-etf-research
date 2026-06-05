#!/usr/bin/env python3
"""
chart_03c_price_timeline.py — Section 3, HYPE price timeline.

HYPE price (CoinGecko daily) from early March through the analysis cutoff
(Jun 2), with the ETF launch dates marked. The point: HYPE was already climbing
well before the ETFs listed, and kept climbing through launch — the wrapper met
pre-existing demand rather than manufacturing it. The Jun 3-4 selloff is handled
separately in the closing coda.

Source: CoinGecko (free, keyless). Trimmed at ANALYSIS_CUTOFF.
Run:  pipenv run python scripts/chart_03c_price_timeline.py
"""
import os
import sys
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import load_mcap_history

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")

LAUNCHES = [
    ("THYP launch", "May 12", pd.Timestamp("2026-05-12", tz="UTC"), cs.ACCENT3),
    ("BHYP launch", "May 14", pd.Timestamp("2026-05-14", tz="UTC"), cs.ACCENT),
]


def main():
    df = load_mcap_history()  # already deduped + trimmed at cutoff (Jun 2)

    fig, ax = cs.new_figure()

    ymax = df.price_usd.max() * 1.15

    # Launch markers: two dashed verticals (THYP May 12, BHYP May 14), but a
    # single shared label, since the dates are only two days apart and per-line
    # labels would overlap. In a March-Jun view they read as one event.
    for label, datestr, d, color in LAUNCHES:
        if df.date.min() <= d <= df.date.max():
            ax.axvline(d, color=color, lw=1.0, ls=(0, (3, 3)), alpha=0.6, zorder=2)
    bhyp_d = LAUNCHES[1][2]
    ax.text(bhyp_d, ymax * 0.34, "  ETFs launch\n  THYP May 12\n  BHYP May 14",
            fontsize=8.6, color=cs.SUBINK, family=cs.BODY, va="bottom", ha="left")

    ax.plot(df.date, df.price_usd, color=cs.ACCENT, lw=2.4, zorder=4)

    # End-value label.
    last = df.iloc[-1]
    ax.text(last.date, last.price_usd, f"  ${last.price_usd:.0f}",
            va="center", ha="left", family=cs.MONO, fontsize=12,
            color=cs.ACCENT, weight="bold")

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}"))
    ax.set_ylim(0, ymax)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO); lbl.set_fontsize(11)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(11); lbl.set_color(cs.INK)

    cs.header(fig,
              "HYPE price · CoinGecko",
              "HYPE was climbing before the ETFs arrived",
              "Daily price, early March \u2013 Jun 2 (launch dates marked)")
    cs.footer(fig, "Source: CoinGecko \u00b7 trimmed at Jun 2; see coda on the Jun 3\u20134 selloff")

    cs.save(fig, "03c_price_timeline", CHARTS)


if __name__ == "__main__":
    main()
