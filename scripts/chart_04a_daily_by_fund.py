#!/usr/bin/env python3
"""
chart_04a_daily_by_fund.py — Section 4, per-fund daily flows.

Daily net inflows per fund (BHYP, THYP, HYPG), derived from Farside's per-fund
cumulative series. Grouped bars, full window May 12 - Jun 4 2026. Shows how each
fund performed day by day, including HYPG's late arrival (Jun 3).

Source: Farside Investors (farside.co.uk/hyp). Separate from the SoSoValue
combined series used in Section 3; the two trackers differ by a few percent.

Run:  pipenv run python scripts/chart_04a_daily_by_fund.py
"""
import os
import sys
import numpy as np
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import fund_daily_from_cumulative

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")


def main():
    df = fund_daily_from_cumulative()
    n = len(df)
    x = np.arange(n)
    w = 0.27

    fig, ax = cs.new_figure()
    ax.bar(x - w, df.bhyp_usd_m, width=w, color=cs.ACCENT,  label="BHYP (Bitwise)",  zorder=3)
    ax.bar(x,     df.thyp_usd_m, width=w, color=cs.ACCENT3, label="THYP (21Shares)", zorder=3)
    ax.bar(x + w, df.hypg_usd_m, width=w, color=cs.GOLD,    label="HYPG (Grayscale)", zorder=3)

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}M"))
    ax.set_ylim(0, max(df.bhyp_usd_m.max(), df.thyp_usd_m.max()) * 1.18)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO); lbl.set_fontsize(11)

    # x labels: show every date as MM-DD, rotated lightly
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%b %-d") for d in df.date],
                       fontsize=9, color=cs.INK, rotation=45, ha="right")

    ax.legend(loc="upper left", frameon=False, fontsize=11,
              prop={"family": cs.BODY})

    cs.header(fig,
              "Per-fund daily net inflows · Farside",
              "Day by day, BHYP and THYP traded the lead",
              "Daily flows by fund, May 12 \u2013 Jun 4 (HYPG listed Jun 3)")
    cs.footer(fig, "Source: Farside Investors (farside.co.uk/hyp), recorded Jun 5 2026")

    cs.save(fig, "04a_daily_by_fund", CHARTS)


if __name__ == "__main__":
    main()
