#!/usr/bin/env python3
"""
chart_04c_race_frames.py — Section 4, per-fund cumulative RACE (GIF frames).

Emits PNG frames of the per-fund cumulative race (BHYP/THYP/HYPG), revealing one
more day per frame against fixed axes. Launch and crossover markers pop in as the
animation date reaches them. A large date readout (upper-right of the plot) ticks
through the actual trading days. Assemble frames into a GIF with any online tool.

Source: Farside Investors (farside.co.uk/hyp).
Run:  pipenv run python scripts/chart_04c_race_frames.py
Output: charts/race_frames/frame_000.png ...
"""
import os
import sys
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import load_fund_cumulative

FRAMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "charts", "race_frames")

LAUNCHES = [
    ("THYP launch", "May 12", pd.Timestamp("2026-05-12", tz="UTC"), cs.ACCENT3, 0.20),
    ("BHYP launch", "May 14", pd.Timestamp("2026-05-14", tz="UTC"), cs.ACCENT,  0.30),
    ("HYPG launch", "Jun 3",  pd.Timestamp("2026-06-03", tz="UTC"), cs.GOLD,    0.20),
]
CROSSOVER = pd.Timestamp("2026-05-23", tz="UTC")
HOLD_FRAMES = 6


def draw_frame(df_full, upto_idx, ymax, xmin, xmax, path):
    d = df_full.iloc[:upto_idx + 1]
    cur_date = d.date.iloc[-1]

    fig, ax = cs.new_figure()

    for label, datestr, dt, color, yfrac in LAUNCHES:
        if cur_date >= dt:
            ax.axvline(dt, color=color, lw=1.0, ls=(0, (3, 3)), alpha=0.55, zorder=2)
            ax.text(dt, ymax * yfrac, f" {label}\n {datestr}", fontsize=8.2,
                    color=color, family=cs.BODY, va="bottom", ha="left")

    if cur_date >= CROSSOVER:
        ax.axvline(CROSSOVER, color=cs.FAINT, lw=1.2, ls=(0, (4, 3)), zorder=2)
        ax.text(CROSSOVER, ymax * 0.97, " BHYP overtakes\n ~May 23", fontsize=9,
                color=cs.SUBINK, family=cs.BODY, va="top", ha="left")

    series = [("bhyp_cum_usd_m", cs.ACCENT, "BHYP (Bitwise)"),
              ("thyp_cum_usd_m", cs.ACCENT3, "THYP (21Shares)"),
              ("hypg_cum_usd_m", cs.GOLD, "HYPG (Grayscale)")]
    for col, color, label in series:
        ax.plot(d.date, d[col], color=color, lw=2.4, label=label, zorder=4)
        v = d[col].iloc[-1]
        if v > 0.05:
            ax.text(d.date.iloc[-1], v, f"  ${v:.1f}M", va="center", ha="left",
                    family=cs.MONO, fontsize=11, color=color, weight="bold")

    # Large changing date readout, left side below the legend (stays clear of
    # the rising lines and the right-side tip labels throughout the animation).
    ax.text(0.035, 0.55, cur_date.strftime("%b %-d"), transform=ax.transAxes,
            ha="left", va="top", family=cs.MONO, fontsize=26, weight="bold",
            color=cs.INK, alpha=0.85)

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax.set_ylim(0, ymax)
    ax.set_xlim(xmin, xmax)
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
              "The HYPE ETF race",
              "Cumulative flows by fund, May 12 \u2013 Jun 4")
    cs.footer(fig, "Source: Farside Investors (farside.co.uk/hyp), recorded Jun 5 2026")

    import matplotlib.pyplot as plt
    fig.savefig(path)
    plt.close(fig)


def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    df = load_fund_cumulative()
    ymax = df.bhyp_cum_usd_m.max() * 1.12
    xmin, xmax = df.date.iloc[0], df.date.iloc[-1]
    pad = (xmax - xmin) * 0.12
    xmax_padded = xmax + pad

    frame = 0
    for i in range(len(df)):
        draw_frame(df, i, ymax, xmin, xmax_padded,
                   os.path.join(FRAMES_DIR, f"frame_{frame:03d}.png"))
        frame += 1
    for _ in range(HOLD_FRAMES):
        draw_frame(df, len(df) - 1, ymax, xmin, xmax_padded,
                   os.path.join(FRAMES_DIR, f"frame_{frame:03d}.png"))
        frame += 1
    print(f"wrote {frame} frames to {FRAMES_DIR}")


if __name__ == "__main__":
    main()
