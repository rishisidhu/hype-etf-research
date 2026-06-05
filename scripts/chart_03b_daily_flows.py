#!/usr/bin/env python3
"""
chart_03b_daily_flows.py — Section 3, daily granularity.

Daily combined net inflows across every disclosed trading day, May 12 - Jun 4
2026. Shows the texture the weekly bars smooth over. The analysis cutoff (Jun 2)
is marked; days after it belong to the separate post-cutoff / selloff analysis.

Source: SoSoValue dashboard (recorded Jun 4 2026), daily combined series.
Run:  pipenv run python scripts/chart_03b_daily_flows.py
"""
import os
import sys
import pandas as pd
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import load_daily_flows, ANALYSIS_CUTOFF

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")


def main():
    df = load_daily_flows()

    fig, ax = cs.new_figure()
    colors = [cs.ACCENT if d <= ANALYSIS_CUTOFF else cs.MUTE for d in df.date]
    ax.bar(df.date, df.daily_net_inflow_usd_m, color=colors, width=0.7, zorder=3)

    cutoff_x = ANALYSIS_CUTOFF + pd.Timedelta(hours=12)
    ax.axvline(cutoff_x, color=cs.FAINT, lw=1.0, ls=(0, (4, 3)), zorder=2)
    ax.text(cutoff_x, df.daily_net_inflow_usd_m.max() * 1.04, " analysis cutoff",
            fontsize=9.5, color=cs.FAINT, family=cs.BODY, va="top", ha="left")

    for _, r in df.iterrows():
        if r.daily_net_inflow_usd_m >= 15:
            ax.text(r.date, r.daily_net_inflow_usd_m + 0.8,
                    f"${r.daily_net_inflow_usd_m:.0f}M", ha="center", va="bottom",
                    family=cs.MONO, fontsize=10.5, color=cs.INK, weight="bold")

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax.set_ylim(0, df.daily_net_inflow_usd_m.max() * 1.18)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO)
        lbl.set_fontsize(11)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(11)
        lbl.set_color(cs.INK)

    cs.header(fig,
              "Combined daily net inflows · May 12 – Jun 4",
              "The daily texture behind the trend",
              "Net inflows surged on May 20 and May 29, then cooled into June")
    cs.footer(fig, "Source: SoSoValue dashboard (recorded Jun 4 2026) · daily combined")

    cs.save(fig, "03b_daily_flows", CHARTS)


if __name__ == "__main__":
    main()
