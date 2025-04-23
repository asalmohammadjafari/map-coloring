from __future__ import annotations

from typing import Dict, Optional, Tuple

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from shapely import wkt


DATASET_PATH = "./countries_dataset.csv"


def _is_non_interactive_backend() -> bool:
    """Return True only for backends that cannot open GUI windows."""
    backend = matplotlib.get_backend().lower()
    non_interactive = {name.lower() for name in matplotlib.rcsetup.non_interactive_bk}
    return backend in non_interactive


def draw_colored_map(
    solution: Optional[Dict[str, str]],
    gdf: gpd.GeoDataFrame,
    continent: str,
    assignments_number: int,
    show: bool = True,
) -> Tuple[plt.Figure, plt.Axes]:
    """Visualize solved map coloring for a continent."""
    selected_continent = gdf[gdf["continent"] == continent].copy()
    if selected_continent.empty:
        raise ValueError(f"No rows found for continent '{continent}'.")

    if solution is not None:
        selected_continent["color"] = selected_continent["iso_a3"].apply(lambda x: solution.get(x, "lightgrey"))
    else:
        selected_continent["color"] = "lightgrey"

    fig, ax = plt.subplots(1, figsize=(12, 12))
    selected_continent.plot(ax=ax, color=selected_continent["color"], edgecolor="black")

    minx, miny, maxx, maxy = selected_continent.total_bounds
    if continent == "Europe":
        ax.set_xlim(-40, 60)
        ax.set_ylim(35, 80)
        text_x, text_y = -40, 82
    else:
        ax.set_xlim(minx - 1, maxx + 1)
        ax.set_ylim(miny - 1, maxy + 1)
        text_x, text_y = minx, maxy + 2

    if solution:
        for _, row in selected_continent.iterrows():
            iso_code = row["iso_a3"]
            if iso_code in solution:
                ax.text(row.geometry.centroid.x, row.geometry.centroid.y, iso_code, fontsize=6, ha="center", va="center")

    ax.text(text_x, text_y, f"Assignment Number: {assignments_number}", fontsize=12, ha="left", va="center")
    ax.set_title(f"Map Coloring - {continent}")
    ax.set_axis_off()

    if show and not _is_non_interactive_backend():
        plt.show()

    return fig, ax


def draw(
    continent: str,
    solution: Optional[Dict[str, str]],
    assignments_number: int,
    show: bool = True,
) -> Tuple[plt.Figure, plt.Axes]:
    """Load data and draw map coloring results."""
    neighbors_df = pd.read_csv(DATASET_PATH)
    neighbors_df["geometry"] = neighbors_df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(neighbors_df, geometry="geometry")
    return draw_colored_map(solution, gdf, continent, assignments_number, show=show)
