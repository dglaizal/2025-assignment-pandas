"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_merge = regions[['code', 'name']].rename(columns={
        'code': 'code_reg',
        'name': 'name_reg'
        })
    departments_merge = departments[['code', 'name', 'region_code']].rename(
        columns={'code': 'code_dep', 'name': 'name_dep'}
    )

    regions_department = departments_merge.merge(
        regions_merge,
        left_on='region_code',
        right_on='code_reg',
        how='left'
    )

    # Select columns in expected order
    regions_department = regions_department[['code_reg',
                                             'name_reg', 'code_dep',
                                             'name_dep']]
    return regions_department


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    # Drop unwanted codes in referendum first
    referendum['Department code'] = \
        referendum['Department code'].astype(str).str.zfill(2)
    referendum = referendum[
        (~referendum['Department code'].astype(str).str.startswith('Z'))
        ]
    rad = regions_and_departments[~regions_and_departments['code_reg'].isin
                                  (["DOM", "COM", "TOM"])]
    rrd = referendum.merge(
        rad,
        left_on="Department code",
        right_on="code_dep",
    )
    return rrd


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region."""
    cols = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    # Ensure numeric columns
    for col in cols:
        referendum_and_areas[col] = pd.to_numeric(referendum_and_areas[col],
                                                  errors='coerce')

    # Group by region
    df = referendum_and_areas.groupby('name_reg', as_index=False)[cols].sum()
    print(df)
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file('data/regions.geojson')
    sumAB = (referendum_result_by_regions["Choice A"] +
             referendum_result_by_regions["Choice B"])
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions['Choice A']/sumAB)
    table_ratio = referendum_result_by_regions.merge(
        regions_geo,
        left_on="name_reg",
        right_on="nom")
    table_ratio = table_ratio[["name_reg", "ratio", "geometry"]]
    print(table_ratio)
    graph = gpd.GeoDataFrame(table_ratio)
    graph.plot("ratio")
    return graph


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
         df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )

#   print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
