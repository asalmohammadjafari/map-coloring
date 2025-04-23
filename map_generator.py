from __future__ import annotations

from typing import Dict, List

import pandas as pd


DATASET_PATH = "./countries_dataset.csv"


def generate_borders_by_continent(continent: str) -> Dict[str, List[str]]:
    """Return adjacency list by ISO A3 for a single continent."""
    neighbors_df = pd.read_csv(DATASET_PATH)
    continent_df = neighbors_df[neighbors_df["continent"] == continent]

    borders: Dict[str, List[str]] = {}
    for _, row in continent_df.iterrows():
        neighbors = row["neighbors"].split(", ") if isinstance(row["neighbors"], str) else []
        borders[row["iso_a3"]] = neighbors

    return borders
