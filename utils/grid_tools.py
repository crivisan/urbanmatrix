from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem
)
from qgis.utils import iface
import processing
from .styling import style_grid


def create_grid_from_raster(raster_layer, cell_size, grid_name="UrbanMatrix_Grid"):
    """
    Generate a grid layer over the extent of a raster image.
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
    style_grid(grid_layer) # CALLING IT HERE

    # Zoom to the new grid layer
    iface.mapCanvas().setExtent(grid_layer.extent())
    iface.mapCanvas().refresh()

    return grid_layer
