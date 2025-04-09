import geopandas as gpd
import tempfile
import json
import os
from qgis.core import QgsVectorLayer, QgsProject, QgsVectorFileWriter
from qgis.PyQt.QtCore import QVariant

def calculate_coverage(grid_layer, feature_layer, output_field="coverage_pct"):
    """
    In-memory GeoPandas coverage calculation using QgsVectorLayer inputs.
    """
    # Step 1: Save both layers to temp GeoJSON
    temp_dir = tempfile.gettempdir()
    grid_path = os.path.join(temp_dir, "temp_grid.geojson")
    feature_path = os.path.join(temp_dir, "temp_buildings.geojson")
    output_path = os.path.join(temp_dir, "grid_with_coverage.geojson")

    QgsVectorFileWriter.writeAsVectorFormat(grid_layer, grid_path, "UTF-8", grid_layer.crs(), "GeoJSON")
    QgsVectorFileWriter.writeAsVectorFormat(feature_layer, feature_path, "UTF-8", feature_layer.crs(), "GeoJSON")

    # Step 2: Load into GeoPandas
    grid = gpd.read_file(grid_path)
    buildings = gpd.read_file(feature_path)

    # Ensure CRS match
    if grid.crs != buildings.crs:
        buildings = buildings.to_crs(grid.crs)

    # Step 3: Calculate area
    grid["cell_area"] = grid.geometry.area
    grid = grid.reset_index().rename(columns={"index": "grid_id"})

    # Clip buildings to grid
    clipped = gpd.overlay(buildings, grid, how="intersection")
    clipped["building_area"] = clipped.geometry.area

    # Aggregate per cell
    area_per_cell = clipped.groupby("grid_id")["building_area"].sum().reset_index()
    area_per_cell.columns = ["grid_id", "total_building_area"]

    # Merge and compute %
    grid = grid.merge(area_per_cell, on="grid_id", how="left")
    grid["total_building_area"] = grid["total_building_area"].fillna(0)
    grid[output_field] = (grid["total_building_area"] / grid["cell_area"]) * 100

    # Step 4: Save to temp file and reload as QgsVectorLayer
    grid.to_file(output_path, driver="GeoJSON")
    output_layer = QgsVectorLayer(output_path, "Grid with Coverage", "ogr")

    return output_layer
