#!/usr/bin/env python3
"""
chart_03a_weekly_flows.py — Section 3, weekly summary.

Combined BHYP + THYP net inflows bucketed by week (derived from the daily
SoSoValue series, so it ties exactly to the daily chart). Full weeks are accent
green; partial weeks are muted grey.

Run:  pipenv run python scripts/chart_03a_weekly_flows.py
"""
import os
import sys
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import load_weekly

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")


def main():
    df = load_weekly()

    fig, ax = cs.new_figure()
    xs = range(len(df))
    # Color by completeness: full weeks accent, partial weeks muted.
    colors = [cs.MUTE if str(p).lower() == "yes" else cs.ACCENT
              for p in df.is_partial]
    bars = ax.bar(xs, df.net_inflow_usd_m, color=colors, width=0.62, zorder=3)

    for b, v in zip(bars, df.net_inflow_usd_m):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.4, f"${v:.1f}M",
                ha="center", va="bottom", family=cs.MONO, fontsize=13,
                color=cs.INK, weight="bold")

    ax.set_xticks(list(xs))
    labels = []
    for _, r in df.iterrows():
        rng = f"{r.period_start[5:]}\u2013{r.period_end[5:]}"
        tag = " (partial)" if str(r.is_partial).lower() == "yes" else ""
        labels.append(f"{r.week_label}{tag}\n{rng}")
    ax.set_xticklabels(labels)
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(11)
        lbl.set_color(cs.INK)

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax.set_ylim(0, df.net_inflow_usd_m.max() * 1.22)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO)
        lbl.set_fontsize(11)

    cs.header(fig,
              "Combined BHYP + THYP · weekly net flows",
              "Inflows built to a late-May crescendo",
              "A strong launch surge that peaked in late May, then normalized")
    cs.footer(fig, "Source: SoSoValue dashboard (recorded Jun 4 2026) · weekly = sum of daily")

    cs.save(fig, "03a_weekly_flows", CHARTS)


if __name__ == "__main__":
    main()
