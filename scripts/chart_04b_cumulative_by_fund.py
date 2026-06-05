#!/usr/bin/env python3
"""
chart_04b_cumulative_by_fund.py — Section 4, per-fund cumulative race.

Cumulative net inflows per fund (BHYP, THYP, HYPG), May 12 - Jun 4 2026.
THYP led from launch; BHYP crossed over in late May and pulled away; HYPG
entered late. Dashed verticals mark each fund's first recorded inflow
(Farside basis) and the approximate BHYP/THYP crossover.

Source: Farside Investors (farside.co.uk/hyp). Separate tracker from the
SoSoValue combined series in Section 3.

Run:  pipenv run python scripts/chart_04b_cumulative_by_fund.py
"""
import os
import sys
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import load_fund_cumulative

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")

# Launch markers on a Farside basis (first non-zero inflow), staggered labels.
LAUNCHES = [
    ("THYP launch", "May 12", pd.Timestamp("2026-05-12", tz="UTC"), cs.ACCENT3, 0.20),
    ("BHYP launch", "May 14", pd.Timestamp("2026-05-14", tz="UTC"), cs.ACCENT,  0.30),
    ("HYPG launch", "Jun 3",  pd.Timestamp("2026-06-03", tz="UTC"), cs.GOLD,    0.20),
]
CROSSOVER = pd.Timestamp("2026-05-23", tz="UTC")  # indicative (lines cross May 22-26)


def main():
    df = load_fund_cumulative()
    ymax = df.bhyp_cum_usd_m.max() * 1.12

    fig, ax = cs.new_figure()

    # Launch markers: subtle fund-colored dashed verticals + small date labels.
    for label, datestr, d, color, yfrac in LAUNCHES:
        ax.axvline(d, color=color, lw=1.0, ls=(0, (3, 3)), alpha=0.55, zorder=2)
        ax.text(d, ymax * yfrac, f" {label}\n {datestr}", fontsize=8.2,
                color=color, family=cs.BODY, va="bottom", ha="left")

    # Crossover: full-height grey dashed line, the narrative beat.
    ax.axvline(CROSSOVER, color=cs.FAINT, lw=1.2, ls=(0, (4, 3)), zorder=2)
    ax.text(CROSSOVER, ymax * 0.97, " BHYP overtakes\n ~May 23", fontsize=9,
            color=cs.SUBINK, family=cs.BODY, va="top", ha="left")

    ax.plot(df.date, df.bhyp_cum_usd_m, color=cs.ACCENT,  lw=2.4,
            label="BHYP (Bitwise)", zorder=4)
    ax.plot(df.date, df.thyp_cum_usd_m, color=cs.ACCENT3, lw=2.4,
            label="THYP (21Shares)", zorder=4)
    ax.plot(df.date, df.hypg_cum_usd_m, color=cs.GOLD,    lw=2.0,
            label="HYPG (Grayscale)", zorder=3)

    last = df.iloc[-1]
    for val, color in [(last.bhyp_cum_usd_m, cs.ACCENT),
                       (last.thyp_cum_usd_m, cs.ACCENT3),
                       (last.hypg_cum_usd_m, cs.GOLD)]:
        ax.text(last.date, val, f"  ${val:.1f}M", va="center", ha="left",
                family=cs.MONO, fontsize=11, color=color, weight="bold")

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}M"))
    ax.set_ylim(0, ymax)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO); lbl.set_fontsize(11)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(11); lbl.set_color(cs.INK)

    ax.legend(loc="upper left", frameon=False, fontsize=11,
              prop={"family": cs.BODY}, bbox_to_anchor=(0.0, 0.88))

    cs.header(fig,
              "Per-fund cumulative net inflows · Farside",
              "BHYP started behind, then pulled ahead",
              "Cumulative flows by fund, May 12 \u2013 Jun 4")
    cs.footer(fig, "Source: Farside Investors (farside.co.uk/hyp), recorded Jun 5 2026")

    cs.save(fig, "04b_cumulative_by_fund", CHARTS)


if __name__ == "__main__":
    main()
