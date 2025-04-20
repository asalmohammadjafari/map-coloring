import geopandas as gpd
import pandas as pd
from shapely import wkt
from typing import Dict
import matplotlib.pyplot as plt

def draw_colored_map(solution: Dict[str, str], gdf: gpd.GeoDataFrame, continent: str, assignments_number: int) -> None:
    """
    Visualizes the solution to a map coloring problem for a specified continent by coloring each country based on
    the solution provided. It annotates each country with its ISO A3 code, adjusts the map's view based on the continent,
    and displays the total number of assignments made by the CSP solver.

    Args:
        solution (Dict[str, str]): A dictionary mapping country ISO A3 codes to their assigned colors.
        gdf (gpd.GeoDataFrame): A GeoDataFrame containing the geographic data of countries, including their continents
                                and ISO A3 codes.
        continent (str): The name of the continent to visualize.
        assignments_number (int): The number of variable assignments made during the solution process.
    """
    # Filter for the selected continent and assign colors
    selected_continent = gdf[gdf['continent'] == continent].copy()
    #selected_continent['color'] = selected_continent['iso_a3'].apply(lambda x: solution.get(x, 'lightgrey'))
    if solution is not None:
        selected_continent['color'] = selected_continent['iso_a3'].apply(lambda x: solution.get(x, 'lightgrey'))
    else:
        selected_continent['color'] = 'lightgrey'

    
    fig, ax = plt.subplots(1, figsize=(12, 12))
    selected_continent.plot(ax=ax, color=selected_continent['color'], edgecolor='black')
    
    # Set map boundaries
    minx, miny, maxx, maxy = selected_continent.total_bounds
    if continent == "Europe":
        ax.set_xlim(-40, 60)
        ax.set_ylim(35, 80)
        text_x, text_y = -40, 82
    else:
        ax.set_xlim(minx - 1, maxx + 1)
        ax.set_ylim(miny - 1, maxy + 1)
        text_x, text_y = minx, maxy + 2

    # Annotate countries and display the assignment number
    for idx, row in selected_continent.iterrows():
        if row['iso_a3'] in solution:
            plt.text(row.geometry.centroid.x, row.geometry.centroid.y, row['iso_a3'], fontsize=6, ha='center', va='center')
    plt.text(text_x, text_y, f"Assignment Number: {assignments_number}", fontsize=12, ha='left', va='center')
    plt.show()

def draw(continent: str, solution: Dict[str, str], assignments_number: int) -> None:
    """
    Loads geographic data from a CSV file, transforms it into a GeoDataFrame, and then visualizes the map coloring
    solution for a specific continent. This function serves as a high-level interface to prepare data and call
    draw_colored_map with appropriate parameters.

    Args:
        continent (str): The name of the continent for which the map coloring solution should be visualized.
        solution (Dict[str, str]): A dictionary where each key is a country's ISO A3 code and its value is the color
                                   assigned to that country as part of the map coloring solution.
        assignments_number (int): The number of assignments made during the solution of the map coloring problem.
    """
    neighbors_df = pd.read_csv('./countries_dataset.csv')
    neighbors_df['geometry'] = neighbors_df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(neighbors_df, geometry='geometry')
    
    draw_colored_map(solution, gdf, continent, assignments_number)