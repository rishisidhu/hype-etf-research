#!/usr/bin/env python3
"""
chart_style.py — shared light "soft-glass" visual system for all charts.

Light, elegant, Medium-friendly. Soft off-white canvas, elevated white card with
subtle shadow + rounded corners, hairline gridlines, refined type hierarchy.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

# ---- palette (light) ------------------------------------------------------
CANVAS   = "#F5F6F8"
CARD     = "#FFFFFF"
INK      = "#1A1D21"
SUBINK   = "#5B6470"
FAINT    = "#98A1AD"
GRID     = "#E9ECF1"
ACCENT   = "#11A37F"
ACCENT2  = "#E8845B"
ACCENT3  = "#3B7DD8"
MUTE     = "#C6CCD4"
GOLD     = "#D9A441"

BRAND = "HYPE ETF RESEARCH"

# ---- fonts ----------------------------------------------------------------
# Prefer faces matplotlib reads cleanly. Variable-font "Inter" is intentionally
# NOT used: matplotlib can't extract its glyphs and renders blanks. On macOS,
# Helvetica Neue / Menlo are always present and complete.
def _pick(cands, default):
    have = {f.name for f in fm.fontManager.ttflist}
    for c in cands:
        if c in have:
            return c
    return default

DISPLAY = _pick(["Helvetica Neue", "Arial", "DejaVu Sans"], "DejaVu Sans")
BODY    = _pick(["Helvetica Neue", "Arial", "DejaVu Sans"], "DejaVu Sans")
MONO    = _pick(["Menlo", "SF Mono", "DejaVu Sans Mono"], "DejaVu Sans Mono")


def apply_rc():
    plt.rcParams.update({
        "figure.facecolor": CANVAS, "savefig.facecolor": CANVAS,
        "axes.facecolor": CARD, "font.family": BODY,
        "text.color": INK, "axes.labelcolor": SUBINK,
        "xtick.color": SUBINK, "ytick.color": SUBINK,
        "axes.edgecolor": GRID, "axes.linewidth": 0,
        "xtick.major.size": 0, "ytick.major.size": 0,
        "font.size": 13,
    })


def new_figure(figsize=(9.6, 6.6)):
    apply_rc()
    fig = plt.figure(figsize=figsize, dpi=200)
    shadow = FancyBboxPatch((0.035, 0.045), 0.945, 0.93,
                            boxstyle="round,pad=0,rounding_size=0.022",
                            transform=fig.transFigure, facecolor="#000000",
                            edgecolor="none", alpha=0.05, zorder=0)
    shadow.set_mutation_aspect(figsize[0] / figsize[1])
    fig.add_artist(shadow)
    card = FancyBboxPatch((0.03, 0.055), 0.945, 0.93,
                          boxstyle="round,pad=0,rounding_size=0.022",
                          transform=fig.transFigure, facecolor=CARD,
                          edgecolor=GRID, linewidth=1.0, zorder=1)
    card.set_mutation_aspect(figsize[0] / figsize[1])
    fig.add_artist(card)
    ax = fig.add_axes([0.105, 0.165, 0.83, 0.56])
    ax.set_facecolor(CARD)
    ax.set_zorder(2)
    ax.patch.set_alpha(0)
    return fig, ax


def header(fig, kicker, headline, subhead):
    spaced = "\u2009".join(kicker.upper())
    fig.text(0.105, 0.895, spaced, fontsize=10.5, color=ACCENT,
             family=MONO, weight="bold")
    fig.text(0.105, 0.825, headline, fontsize=22, color=INK,
             family=DISPLAY, weight="bold")
    fig.text(0.105, 0.772, subhead, fontsize=12.5, color=SUBINK, family=BODY)


def footer(fig, source):
    fig.add_artist(plt.Line2D([0.105, 0.935], [0.105, 0.105],
                   color=GRID, lw=1.0, transform=fig.transFigure))
    fig.text(0.105, 0.072, BRAND, fontsize=9, color=FAINT,
             family=MONO, weight="bold")
    fig.text(0.935, 0.072, source, fontsize=8.4, color=FAINT,
             family=BODY, ha="right")


def style_axes(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.grid(axis="y", color=GRID, lw=1.0, zorder=0)
    ax.set_axisbelow(True)


def save(fig, stem, charts_dir):
    import os
    fig.savefig(os.path.join(charts_dir, f"{stem}.png"))
    fig.savefig(os.path.join(charts_dir, f"{stem}.svg"))
    plt.close(fig)
    print(f"wrote {stem}.png and {stem}.svg")
