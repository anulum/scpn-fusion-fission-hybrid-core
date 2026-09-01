# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Fusion Fission Hybrid Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the fusion source driving a subcritical blanket,
the strictly subcritical multiplication-factor interval with its
documented margin, and the declared neutron economy across the owned
fertile classes. The text panel of every image carries the
repository's nuclear non-claim: nothing here is a nuclear-safety,
criticality-safety, or licensing statement.

Outputs (written next to this script):

- ``repo_header.png`` — the fusion source inside its subcritical
  blanket (used by ``README.md``).
- ``repo_header_keff_interval.png`` — the strictly open k_eff interval
  with the documented criticality margin.
- ``repo_header_neutron_economy.png`` — source, blanket and fertile
  class as a declared chain.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

CRITICALITY_MARGIN_KEFF = 0.98
FERTILE_CLASSES = ("depleted_uranium", "natural_uranium", "thorium")

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "fusion_fission_hybrid"),
    ("Hard Invariant", "k_eff strictly inside (0, 1)"),
    ("Criticality Margin", "k_eff above 0.98 flagged"),
    ("Fertile Classes", "depleted · natural uranium · thorium"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the right-hand text panel with the nuclear non-claim."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.85,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.775,
        "FUSION FISSION",
        color="white",
        fontsize=22,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.735,
        "HYBRID CORE",
        color="white",
        fontsize=22,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.678,
        subtitle,
        color=CYAN,
        fontsize=10.5,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.638, 0.638], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.578
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.070
    ax.plot([0.08, 0.85], [0.145, 0.145], color=STEEL, lw=0.8, alpha=0.5)
    ax.text(
        0.08,
        0.105,
        "No nuclear-safety, criticality-safety or",
        color=RED,
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.9,
    )
    ax.text(
        0.08,
        0.078,
        "licensing claim of any kind is made.",
        color=RED,
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.9,
    )
    ax.text(
        0.08,
        0.042,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.015,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _source_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
) -> None:
    """Draw the glowing fusion neutron source."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 150)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 150)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=28,
        cmap=_glow_cmap(),
        alpha=0.92,
    )


def generate_source_and_blanket() -> None:
    """Generate ``repo_header.png``: the driven subcritical blanket."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    theta = np.linspace(0.0, 2.0 * np.pi, 300)

    _source_glow(ax, 0.0, 0.0, 0.30, 0.95)
    ax.plot(
        0.28 * np.cos(theta),
        0.28 * np.sin(theta),
        color=CYAN,
        lw=1.7,
        alpha=0.95,
    )
    ax.text(
        0.0,
        -0.52,
        "fusion neutron source",
        color=CYAN,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    for radius in (0.86, 1.14):
        ax.plot(
            radius * np.cos(theta),
            radius * np.sin(theta),
            color=STEEL,
            lw=2.2,
            alpha=0.95,
        )
    ax.text(
        1.45,
        0.92,
        "subcritical blanket",
        color="#8899aa",
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    for index in range(20):
        angle = 2.0 * np.pi * index / 20
        ax.annotate(
            "",
            xy=(0.84 * np.cos(angle), 0.84 * np.sin(angle)),
            xytext=(0.36 * np.cos(angle), 0.36 * np.sin(angle)),
            arrowprops={"arrowstyle": "->", "color": PROBE, "lw": 1.0, "alpha": 0.75},
        )
    for index in range(28):
        angle = 2.0 * np.pi * index / 28 + 0.11
        ax.plot(
            [
                np.cos(angle) - 0.05 * np.sin(angle),
                np.cos(angle) + 0.05 * np.sin(angle),
            ],
            [
                np.sin(angle) + 0.05 * np.cos(angle),
                np.sin(angle) - 0.05 * np.cos(angle),
            ],
            color=MAGENTA,
            lw=1.2,
            alpha=0.8,
        )

    ax.text(
        -2.62,
        1.24,
        r"driven multiplication  $M = 1/(1 - k_{eff})$",
        color=MAGENTA,
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        -2.62,
        0.98,
        "the blanket never sustains itself",
        color="#667799",
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    ax.text(
        0.0,
        -1.32,
        "declared subcritical by construction · k_eff strictly inside (0, 1)",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "A Source, A Blanket, No Chain")
    _save(fig, plt, "repo_header.png")


def generate_keff_interval() -> None:
    """Generate ``repo_header_keff_interval.png``: the open interval."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    axis_y = 5.0
    ax.plot([1.0, 8.6], [axis_y, axis_y], color=STEEL, lw=1.8, alpha=0.85)
    ticks = ((0.0, "0"), (0.25, "0.25"), (0.5, "0.50"), (0.75, "0.75"), (1.0, "1"))
    for fraction, label in ticks:
        tick_x = 1.0 + 7.6 * fraction
        ax.plot(
            [tick_x, tick_x],
            [axis_y - 0.18, axis_y + 0.18],
            color=STEEL,
            lw=1.1,
            alpha=0.8,
        )
        ax.text(
            tick_x,
            axis_y - 0.62,
            label,
            color="#8899bb",
            fontsize=8.5,
            fontfamily="monospace",
            ha="center",
        )
    ax.text(
        5.0,
        3.55,
        "multiplication factor  k_eff",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="center",
    )

    for fraction in (0.0, 1.0):
        ax.plot(
            1.0 + 7.6 * fraction,
            axis_y,
            "o",
            color=RED,
            ms=11,
            mfc=BG,
            mew=2.2,
            alpha=0.95,
        )
    ax.text(
        1.0,
        axis_y + 0.75,
        "0 excluded",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        8.6,
        axis_y + 0.75,
        "1 excluded · never critical",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="right",
        alpha=0.95,
    )

    margin_x = 1.0 + 7.6 * CRITICALITY_MARGIN_KEFF
    ax.fill_between(
        [1.0, margin_x],
        axis_y - 0.30,
        axis_y + 0.30,
        color=GREEN,
        alpha=0.10,
    )
    ax.fill_between(
        [margin_x, 8.6],
        axis_y - 0.30,
        axis_y + 0.30,
        color=RED,
        alpha=0.16,
    )
    ax.text(
        4.4,
        axis_y + 1.55,
        "accepted subcritical interval",
        color=GREEN,
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.annotate(
        f"k_eff > {CRITICALITY_MARGIN_KEFF:.2f} · FLAGGED",
        xy=(margin_x + 0.08, axis_y - 0.42),
        xytext=(6.95, 2.55),
        color=RED,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
        arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.0, "alpha": 0.7},
    )

    for fraction, inside in ((0.42, True), (0.90, True), (0.995, False)):
        mark_x = 1.0 + 7.6 * fraction
        if inside:
            ax.plot(mark_x, axis_y, "o", color=CYAN, ms=6, alpha=0.95)
        else:
            ax.plot(
                mark_x,
                axis_y,
                "x",
                color=RED,
                ms=9,
                mew=2.2,
                alpha=0.95,
            )

    ax.text(
        5.0,
        1.5,
        "a driven hybrid blanket never reaches criticality · enforced "
        "in the configuration model",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Strictly Subcritical, Enforced")
    _save(fig, plt, "repo_header_keff_interval.png")


def generate_neutron_economy() -> None:
    """Generate ``repo_header_neutron_economy.png``: the chain."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    _source_glow(ax, 1.75, 0.55, 0.28, 0.8)
    ax.plot(
        1.75 + 0.26 * np.cos(theta),
        0.55 + 0.26 * np.sin(theta),
        color=CYAN,
        lw=1.6,
        alpha=0.95,
    )
    ax.text(
        1.75,
        -0.55,
        "fusion source",
        color=CYAN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        1.75,
        -0.92,
        "declared neutron yield",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.annotate(
        "",
        xy=(4.05, 0.55),
        xytext=(2.35, 0.55),
        arrowprops={
            "arrowstyle": "-|>",
            "color": PROBE,
            "lw": 1.8,
            "alpha": 0.9,
            "mutation_scale": 12,
        },
    )
    ax.text(
        3.2,
        0.92,
        "source neutrons",
        color=PROBE,
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.add_patch(
        plt.Rectangle(
            (4.1, -0.75),
            1.9,
            2.6,
            fill=False,
            ec=STEEL,
            lw=2.0,
            alpha=0.9,
        )
    )
    for index in range(5):
        line_y = -0.42 + index * 0.53
        ax.plot(
            [4.35, 5.75],
            [line_y, line_y],
            color=MAGENTA,
            lw=1.0,
            alpha=0.55,
        )
    ax.text(
        5.05,
        2.05,
        "subcritical blanket",
        color="#99bbdd",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        5.05,
        -1.12,
        r"$M = 1/(1 - k_{eff})$",
        color=MAGENTA,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.annotate(
        "",
        xy=(7.6, 0.55),
        xytext=(6.1, 0.55),
        arrowprops={
            "arrowstyle": "-|>",
            "color": PROBE,
            "lw": 1.8,
            "alpha": 0.9,
            "mutation_scale": 12,
        },
    )
    ax.text(
        6.85,
        0.92,
        "multiplied output",
        color=PROBE,
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        8.4,
        1.62,
        "fertile class",
        color="#99bbdd",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    for index, name in enumerate(FERTILE_CLASSES):
        ax.text(
            8.4,
            1.15 - index * 0.42,
            name,
            color="#7799bb",
            fontsize=7.5,
            fontfamily="monospace",
            ha="center",
            alpha=0.9,
        )
    ax.text(
        8.4,
        -0.6,
        "one of three, validated",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.text(
        5.0,
        -2.35,
        "every quantity here is declared and validated · none is "
        "measured, none is licensed",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    ax.text(
        5.0,
        -2.78,
        "no nuclear-safety, criticality-safety or licensing claim of any kind",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    _text_panel(fig, "A Declared Neutron Economy")
    _save(fig, plt, "repo_header_neutron_economy.png")


if __name__ == "__main__":
    generate_source_and_blanket()
    generate_keff_interval()
    generate_neutron_economy()
