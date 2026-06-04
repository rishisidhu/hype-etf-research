#!/usr/bin/env python3
"""
chart_style.py — shared light "soft-glass" visual system for all charts.

Imported by every chart_NN_*.py so the look stays consistent and is tweakable
in one place. Aesthetic: elegant, clear, Medium-friendly. Soft off-white canvas,
elevated card panel with subtle shadow + rounded corners, low-alpha gradient
fills, hairline gridlines, refined type hierarchy. Designed to survive as a flat
PNG/SVG (no fake blur that muddies on a white page).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ---- palette (light) ------------------------------------------------------
CANVAS   = "#F5F6F8"   # page-matching soft off-white (outermost)
CARD     = "#FFFFFF"   # elevated panel
INK      = "#1A1D21"   # primary text
SUBINK   = "#5B6470"   # secondary text
FAINT    = "#98A1AD"   # captions / footer
GRID     = "#E9ECF1"   # hairline gridlines
ACCENT   = "#11A37F"   # primary signal (HYPE / highlight) — refined teal-green
ACCENT2  = "#E8845B"   # secondary series (e.g. 21Shares)
ACCENT3  = "#3B7DD8"   # tertiary (BTC comparisons)
MUTE     = "#C6CCD4"   # muted comparator bars
GOLD     = "#D9A441"   # occasional emphasis / annotation

BRAND = "HYPE ETF RESEARCH"

# ---- fonts: prefer refined installed faces, fall back cleanly -------------
def _pick(cands, default):
    have = {f.name for f in fm.fontManager.ttflist}
    for c in cands:
        if c in have:
            return c
    return default

# Avoid overused defaults; prefer humanist/grotesque if present.
DISPLAY = _pick(["Inter", "IBM Plex Sans", "Helvetica Neue", "Arial", "DejaVu Sans"], "DejaVu Sans")
BODY    = _pick(["Inter", "IBM Plex Sans", "Helvetica Neue", "Arial", "DejaVu Sans"], "DejaVu Sans")
MONO    = _pick(["IBM Plex Mono", "SF Mono", "Menlo", "DejaVu Sans Mono"], "DejaVu Sans Mono")


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
    """Canvas + an elevated rounded 'card' + the plotting axes on top."""
    apply_rc()
    fig = plt.figure(figsize=figsize, dpi=200)

    # Card layer: a rounded rectangle with a soft shadow, drawn in figure coords.
    # Shadow (slightly offset, very light).
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

    # Plotting axes sit inside the card with generous padding.
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
