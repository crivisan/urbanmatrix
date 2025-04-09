def calculate_coverage(grid_layer, feature_layer, output_field="coverage_pct"):
    import geopandas as gpd
    import pandas as pd
    import tempfile
    import os
    from qgis.core import (
        QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFields,
        QgsCoordinateReferenceSystem, QgsVectorFileWriter
    )
    from qgis.PyQt.QtCore import QVariant

    # Save both layers to temp files
    temp_dir = tempfile.gettempdir()
    grid_path = os.path.join(temp_dir, "temp_grid.geojson")
    feature_path = os.path.join(temp_dir, "temp_features.geojson")
    QgsVectorFileWriter.writeAsVectorFormat(grid_layer, grid_path, "UTF-8", grid_layer.crs(), "GeoJSON")
    QgsVectorFileWriter.writeAsVectorFormat(feature_layer, feature_path, "UTF-8", feature_layer.crs(), "GeoJSON")

    # Load into GeoPandas
    grid = gpd.read_file(grid_path)
    features = gpd.read_file(feature_path)

    if grid.crs != features.crs:
        features = features.to_crs(grid.crs)

    # Add grid_id from original index
    grid["grid_id"] = grid.index
    grid["cell_area"] = grid.geometry.area

    # Clip buildings to grid cells
    clipped = gpd.overlay(features, grid, how="intersection")

    # Calculate clipped area
    clipped["building_area"] = clipped.geometry.area

    # Sum building area per grid cell
    stats = clipped.groupby("grid_id")["building_area"].sum().reset_index()

    # Merge back into grid
    grid = pd.merge(grid, stats, on="grid_id", how="left")
    grid["building_area"] = grid["building_area"].fillna(0)

    # Calculate coverage %
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

    mem_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "Building Density", "memory")
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
