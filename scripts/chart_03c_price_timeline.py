#!/usr/bin/env python3
"""
chart_03c_price_timeline.py - Section 3, HYPE vs BTC price around launch.

Both coins indexed to 100 at the series start (late April), showing that HYPE
was range-bound until the ETFs listed in mid-May, then broke out and decoupled
from a flat-to-lower Bitcoin. Launch dates marked. The chart shows timing; the
text argues the ETFs widened access to an already-productive asset rather than
causing the move.

Source: CoinGecko (price_compare.csv), both coins.
Run:  pipenv run python scripts/chart_03c_price_timeline.py
"""
import os
import sys
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_style as cs
from load_data import price_compare_indexed

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts")

LAUNCHES = [
    ("THYP", pd.Timestamp("2026-05-12", tz="UTC"), cs.ACCENT3),
    ("BHYP", pd.Timestamp("2026-05-14", tz="UTC"), cs.ACCENT),
]


def main():
    px = price_compare_indexed()  # indexed to 100 at series start, both coins

    fig, ax = cs.new_figure()
    ymax = px.indexed.max() * 1.10

    for _, d, color in LAUNCHES:
        ax.axvline(d, color=color, lw=1.0, ls=(0, (3, 3)), alpha=0.55, zorder=2)
    ax.text(LAUNCHES[1][1], ymax * 0.40, "  ETFs launch\n  May 12 / 14",
            fontsize=8.6, color=cs.SUBINK, family=cs.BODY, va="bottom", ha="left")

    ax.axhline(100, color=cs.FAINT, lw=1.0, zorder=2)

    def _px_on(coin, dstr):
        r = px[(px.coin == coin) & (px.date == pd.Timestamp(dstr, tz="UTC"))]
        return r.price_usd.iloc[0] if len(r) else None

    def _fmt(v):
        return f"${v/1000:.0f}k" if v >= 1000 else f"${v:.0f}"

    for coin, color in [("HYPE", cs.ACCENT), ("BTC", cs.ACCENT3)]:
        s = px[px.coin == coin].sort_values("date")
        ax.plot(s.date, s.indexed, color=color, lw=2.4, label=coin, zorder=4)
        last = s.iloc[-1]
        # end label: index + dollar folded together
        ax.text(last.date, last.indexed, f"  {last.indexed:.0f} ({_fmt(last.price_usd)})",
                va="center", ha="left", family=cs.MONO, fontsize=10,
                color=color, weight="bold")

    # Dollar notes at start, launch, and HYPE peak (kept off the crowded right edge).
    start_date = px.date.min()
    notes = [
        ("HYPE", start_date, _fmt(_px_on("HYPE", str(start_date.date()))), 6, 8, "left"),
        ("BTC",  start_date, _fmt(_px_on("BTC",  str(start_date.date()))), 6, -14, "left"),
        ("HYPE", pd.Timestamp("2026-06-04", tz="UTC"), f'peak {_fmt(_px_on("HYPE","2026-06-04"))}', 0, 10, "right"),
    ]
    for coin, d, txt, dx, dy, ha in notes:
        yv = px[(px.coin==coin) & (px.date==d)].indexed.iloc[0]
        ax.annotate(txt, xy=(d, yv), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.2, color=(cs.ACCENT if coin=="HYPE" else cs.ACCENT3),
                    family=cs.BODY, ha=ha, va="bottom")

    cs.style_axes(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.set_ylim(min(80, px.indexed.min() * 0.96), ymax)
    for lbl in ax.get_yticklabels():
        lbl.set_family(cs.MONO); lbl.set_fontsize(11)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(11); lbl.set_color(cs.INK)

    ax.legend(loc="upper left", frameon=False, fontsize=11,
              prop={"family": cs.BODY})

    cs.header(fig,
              "HYPE vs BTC, indexed to 100 \u00b7 CoinGecko",
              "HYPE broke out as the ETFs arrived",
              "Price indexed to 100 at series start; BTC flat while HYPE doubled")
    cs.footer(fig, "Source: CoinGecko \u00b7 both coins indexed to 100 at the start of the window")

    cs.save(fig, "03c_price_timeline", CHARTS)


if __name__ == "__main__":
    main()
