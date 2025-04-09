import os
import tempfile
import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import shape, box
import mercantile
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject



def download_ms_buildings_from_extent(extent, crs="EPSG:4326"):
    """
    Downloads Microsoft building footprints for the given extent (xmin, ymin, xmax, ymax).
    
    :param extent: Tuple (minx, miny, maxx, maxy)
    :param crs: Coordinate Reference System of input extent (defaults to EPSG:4326)
    :return: QgsVectorLayer loaded into memory
    """

    print(f"[INFO] Downloading MS buildings for {extent} ({crs})")

    # Convert extent to WGS84 (EPSG:4326) for tile lookup
    original_crs = QgsCoordinateReferenceSystem(crs)
    wgs84_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    transform = QgsCoordinateTransform(original_crs, wgs84_crs, QgsProject.instance())

    # Build bounding box polygon and transform
    minx, miny, maxx, maxy = extent
    rect_geom = box(minx, miny, maxx, maxy)
    gdf_rect = gpd.GeoDataFrame(geometry=[rect_geom], crs=crs)
    gdf_rect_wgs84 = gdf_rect.to_crs("EPSG:4326")
    bounds = gdf_rect_wgs84.total_bounds  # minx, miny, maxx, maxy in WGS84


    # Get Microsoft index
    index_url = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"
    df_index = pd.read_csv(index_url, dtype=str)
    df_index['QuadKey'] = df_index['QuadKey'].astype(str)

    # Determine tiles (zoom level 9 for performance)
    minx4326, miny4326, maxx4326, maxy4326 = bounds
    quad_keys = set()
    for tile in list(mercantile.tiles(minx4326, miny4326, maxx4326, maxy4326, zooms=9)):
        quad_keys.add(mercantile.quadkey(tile))
    quad_keys = list(quad_keys)

    # Download + filter each matching tile
    buildings_gdf = gpd.GeoDataFrame()
    for qk in quad_keys:
        row = df_index[df_index['QuadKey'] == qk]
        if row.empty:
            continue
        url = row.iloc[0]["Url"]
        try:
            print(f"[INFO] Fetching {url}")
            #r = requests.get(url)
            #r.raise_for_status()
            df = pd.read_json(url, lines=True)#(r.content, lines=True)
            df["geometry"] = df["geometry"].apply(shape)
            gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")

            # Reproject to original CRS for intersection
            gdf = gdf.to_crs(crs)
            gdf = gdf[gdf.geometry.intersects(rect_geom)]
            buildings_gdf = pd.concat([buildings_gdf, gdf], ignore_index=True)
            buildings_gdf = buildings_gdf.drop(['properties'], axis=1)

        except Exception as e:
            print(f"[ERROR] Could not download {qk}: {e}")

    if buildings_gdf.empty:
        print("[WARN] No buildings found.")
        return None

    # Save to file and return as QgsVectorLayer
    out_path = os.path.join(tempfile.gettempdir(), "ms_buildings.geojson")
    buildings_gdf.to_file(out_path, driver="GeoJSON")

    layer = QgsVectorLayer(out_path, "Microsoft Buildings", "ogr")
    return layer if layer.isValid() else None
