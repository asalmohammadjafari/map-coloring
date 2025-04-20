import pandas as pd
from shapely import wkt
from typing import Dict, List

def generate_borders_by_continent(continent: str) -> Dict[str, List[str]]:
    """
    Generates a dictionary mapping each country in the specified continent to a list of its neighboring countries'
    ISO A3 codes. The function loads geographic and neighbor data from a CSV file, filters it by the specified
    continent, and then parses each country's neighbors.

    Args:
        continent (str): The name of the continent for which to generate borders and neighbors.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are country ISO A3 codes and values are lists of ISO A3 codes
                               of neighboring countries within the same continent.
    """
    neighbors_df = pd.read_csv('./countries_dataset.csv')
    neighbors_df['geometry'] = neighbors_df['geometry'].apply(wkt.loads)

    continent_df = neighbors_df[neighbors_df['continent'] == continent]

    borders = {}
    for _, row in continent_df.iterrows():
        neighbors = row['neighbors'].split(', ') if isinstance(row['neighbors'], str) else []
        borders[row['iso_a3']] = neighbors

    return borders