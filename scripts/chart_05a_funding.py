#!/usr/bin/env python3
"""
chart_05a_funding.py — Section 5, HYPE vs BTC: price + perp funding.

Two stacked panels sharing an x-axis (May 1 - Jun 5 2026):
  top    - price indexed to 100 at May 1 (relative move; lets HYPE ~$70 and
           BTC ~$70k be compared directly as percent change)
  bottom - daily-mean annualized perp funding rate

Reports what happened without forcing a causal read: HYPE ran well ahead of BTC
over the window and gave some back on Jun 5; BTC declined throughout; HYPE
funding stayed persistently hotter than BTC's the whole time.

Sources: CoinGecko (price_compare.csv), Hyperliquid API (funding).
Run:  pipenv run python scripts/chart_05a_funding.py
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import price_compare_indexed, funding_daily

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")

START = "2026-05-01"
START_TS = pd.Timestamp(START, tz="UTC")
LAUNCHES = [
    ("THYP", pd.Timestamp("2026-05-12", tz="UTC"), cs.ACCENT3),
    ("BHYP", pd.Timestamp("2026-05-14", tz="UTC"), cs.ACCENT),
]


def _style(ax):
    ax.set_facecolor(cs.CARD)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(cs.GRID)
    ax.grid(axis="y", color=cs.GRID, lw=0.8, zorder=0)
    ax.tick_params(length=0, colors=cs.SUBINK)


def main():
    px = price_compare_indexed(start=START)
    fd = funding_daily(cutoff=False)
    fd = fd[fd.date >= START_TS]

    fig, (axp, axf) = plt.subplots(
        2, 1, figsize=(11.6, 8.6), sharex=True,
        gridspec_kw={"height_ratios": [1.05, 1.0], "hspace": 0.14})
    fig.patch.set_facecolor(cs.CANVAS)
    fig.subplots_adjust(left=0.105, right=0.935, top=0.80, bottom=0.10)

    # ---- top panel: price indexed to 100 -----------------------------------
    def _fmt_px(v):
        return f"\\${v/1000:.1f}k" if v >= 1000 else f"\\${v:.0f}"
    for coin, color in [("HYPE", cs.ACCENT), ("BTC", cs.ACCENT3)]:
        s = px[px.coin == coin]
        axp.plot(s.date, s.indexed, color=color, lw=2.4, label=coin, zorder=4)
        last = s.iloc[-1]
        axp.text(last.date, last.indexed,
                 f"  {last.indexed:.0f} \u00b7 {_fmt_px(last.price_usd)}",
                 va="center", ha="left", family=cs.MONO, fontsize=10.5,
                 color=color, weight="bold")
    axp.axhline(100, color=cs.FAINT, lw=1.0, zorder=2)
    # Actual dollar prices on key days (index hides the dollar reality).
    # NOTE: escape $ as \\$ so matplotlib does not enter mathtext mode.
    # Static labels (open space, no collision): baseline + peak.
    for dstr, yval, txt, ha, dx, dy in [
        ("2026-05-01", 100.0, "HYPE \\$39.67\nBTC \\$76.3k", "left",  10, 18),
        ("2026-06-04", 187.5, "peak \\$74.39",                  "right", -6, 10),
    ]:
        axp.annotate(txt, xy=(pd.Timestamp(dstr, tz="UTC"), yval),
                     xytext=(dx, dy), textcoords="offset points",
                     fontsize=8.4, color=cs.SUBINK, family=cs.BODY,
                     ha=ha, va="bottom")

    axp.margins(x=0.04)
    for _, d, color in LAUNCHES:
        axp.axvline(d, color=color, lw=1.0, ls=(0, (3, 3)), alpha=0.5, zorder=2)
    _style(axp)
    axp.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    for lbl in axp.get_yticklabels():
        lbl.set_family(cs.MONO); lbl.set_fontsize(10)
    axp.legend(loc="upper left", frameon=False, fontsize=11,
               prop={"family": cs.BODY})
    axp.set_ylabel("Price, indexed to 100 (May 1)", fontsize=9.5,
                   color=cs.SUBINK, family=cs.BODY)

    # ---- bottom panel: funding ---------------------------------------------
    for coin, color in [("HYPE", cs.ACCENT), ("BTC", cs.ACCENT3)]:
        s = fd[fd.coin == coin].sort_values("date")
        axf.plot(s.date, s.funding_annualized_pct, color=color, lw=2.2,
                 label=coin, zorder=4)
        last = s.iloc[-1]
        axf.text(last.date, last.funding_annualized_pct, f"  {last.funding_annualized_pct:.0f}%",
                 va="center", ha="left", family=cs.MONO, fontsize=11,
                 color=color, weight="bold")
    axf.axhline(0, color=cs.FAINT, lw=1.0, zorder=2)
    for _, d, color in LAUNCHES:
        axf.axvline(d, color=color, lw=1.0, ls=(0, (3, 3)), alpha=0.5, zorder=2)
    _style(axf)
    axf.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    for lbl in axf.get_yticklabels():
        lbl.set_family(cs.MONO); lbl.set_fontsize(10)
    axf.set_ylabel("Perp funding, annualized", fontsize=9.5,
                   color=cs.SUBINK, family=cs.BODY)
    axf.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    axf.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    for lbl in axf.get_xticklabels():
        lbl.set_fontsize(11); lbl.set_color(cs.INK)

    # ---- shared header (manual, since this is a 2-panel figure) ------------
    fig.text(0.105, 0.945, "H Y P E   V S   B T C   \u00b7   P R I C E   &   F U N D I N G",
             family=cs.MONO, fontsize=12, color=cs.ACCENT, weight="bold")
    fig.text(0.105, 0.885, "HYPE ran ahead of BTC \u2014 and longs kept paying",
             family=cs.DISPLAY, fontsize=23, color=cs.INK, weight="bold")
    fig.text(0.105, 0.840, "HYPE funding ran ~8% vs BTC ~3% through May, then spiked to 33% as price fell",
             family=cs.BODY, fontsize=12.5, color=cs.SUBINK)
    fig.text(0.105, 0.035, "HYPE  ETF  RESEARCH", family=cs.MONO, fontsize=9,
             color=cs.FAINT)
    fig.text(0.935, 0.035, "Sources: CoinGecko (price) \u00b7 Hyperliquid API (funding)",
             family=cs.BODY, fontsize=9, color=cs.FAINT, ha="right")

    out = os.path.join(CHARTS, "05a_funding.png")
    fig.savefig(out, dpi=200, facecolor=cs.CANVAS)
    fig.savefig(out.replace(".png", ".svg"), facecolor=cs.CANVAS)
    plt.close(fig)
    print("wrote 05a_funding.png and 05a_funding.svg")


if __name__ == "__main__":
    main()
