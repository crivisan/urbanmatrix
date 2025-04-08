from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem
)
from qgis.utils import iface
import processing


def create_grid_from_raster(raster_layer, cell_size, crs="EPSG:3857", grid_name="UrbanMatrix_Grid"):
    """
    Generate a grid layer over the extent of a raster image.

    :param raster_layer: QgsRasterLayer loaded in the QGIS project.
    :param cell_size: Grid cell size in map units.
    :param crs: Coordinate reference system (default: EPSG:3857).
    :param grid_name: Name for the output grid layer.
    :return: QgsVectorLayer grid layer.
    """
    if not raster_layer:
        raise ValueError("Raster layer is not provided.")

    extent = raster_layer.extent()
    extent_str = f"{extent.xMinimum()},{extent.xMaximum()},{extent.yMinimum()},{extent.yMaximum()}"
    crs = raster_layer.crs()  # 

    params = {
        'TYPE': 2,  # Polygon grid
        'EXTENT': extent_str,
        'HSPACING': cell_size,
        'VSPACING': cell_size,
        'CRS': crs,
        'OUTPUT': 'memory:' + grid_name
    }

    result = processing.run("qgis:creategrid", params)
    grid_layer = result['OUTPUT']
    QgsProject.instance().addMapLayer(grid_layer)

    # Zoom to the new grid layer
    iface.mapCanvas().setExtent(grid_layer.extent())
    iface.mapCanvas().refresh()

    return grid_layer
