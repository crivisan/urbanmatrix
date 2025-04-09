import geopandas as gpd
from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsFields,
    QgsProject,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    QgsVectorDataProvider
)
from qgis.PyQt.QtCore import QVariant
import tempfile
import os
import pandas as pd

def calculate_coverage(grid_layer, feature_layer, output_field="coverage_pct"):
    """
    Calculates % coverage of features within each grid cell and returns a memory layer.
    """
    # Save layers to temporary GeoJSONs
    temp_dir = tempfile.gettempdir()
    grid_path = os.path.join(temp_dir, "temp_grid.geojson")
    feature_path = os.path.join(temp_dir, "temp_buildings.geojson")

    QgsVectorFileWriter.writeAsVectorFormat(grid_layer, grid_path, "UTF-8", grid_layer.crs(), "GeoJSON")
    QgsVectorFileWriter.writeAsVectorFormat(feature_layer, feature_path, "UTF-8", feature_layer.crs(), "GeoJSON")

    # Load into GeoDataFrames
    grid = gpd.read_file(grid_path)
    features = gpd.read_file(feature_path)

    if grid.crs != features.crs:
        features = features.to_crs(grid.crs)

    # Compute area
    grid["cell_area"] = grid.geometry.area
    grid = grid.reset_index().rename(columns={"index": "grid_id"})

    # Clip and compute area
    clipped = gpd.overlay(features, grid, how="intersection")
    clipped["building_area"] = clipped.geometry.area

    # Aggregate
    stats = clipped.groupby("grid_id")["building_area"].sum().reset_index()
    grid = grid.merge(stats, on="grid_id", how="left").fillna(0)
    grid[output_field] = (grid["building_area"] / grid["cell_area"]) * 100

    # Build QGIS memory layer
    crs = QgsCoordinateReferenceSystem(grid_layer.crs().authid())
    fields = QgsFields()
    for col in grid.columns:
        if col == "geometry":
            continue
        dtype = QVariant.String
        if pd.api.types.is_numeric_dtype(grid[col]):
            dtype = QVariant.Double
        fields.append(QgsField(col, dtype))

    mem_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "Grid with Coverage", "memory")
    mem_provider = mem_layer.dataProvider()
    mem_provider.addAttributes(fields)
    mem_layer.updateFields()

    for _, row in grid.iterrows():
        feat = QgsFeature()
        feat.setFields(fields)
        feat.setGeometry(QgsGeometry.fromWkt(row.geometry.wkt))
        feat.setAttributes([row[col] for col in grid.columns if col != "geometry"])
        mem_provider.addFeature(feat)

    mem_layer.updateExtents()
    return mem_layer
