from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
    QgsSymbol,
    QgsSingleSymbolRenderer,
    
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

def style_by_density_class(layer, class_field="density_class"):
    """
    Applies predefined styling to the given layer based on density_class field.
    """
    categories = []

    # Define class-color pairs
    class_colors = {
        "Low": QColor("#66c2a5"),
        "Moderate": QColor("#ffd92f"),
        "High": QColor("#e41a1c"),
        "NoData": QColor(255, 255, 255, 0)  # Transparent
    }

    for class_name, color in class_colors.items():
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(color)
        category = QgsRendererCategory(class_name, symbol, class_name)
        categories.append(category)
    iface.layerTreeView().refreshLayerSymbology(layer.id())
    renderer = QgsCategorizedSymbolRenderer(class_field, categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()



def style_buildings_footprint(layer):
    """
    Styles building footprints with transparent fill and purple border.
    """
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())

    if symbol is not None and symbol.symbolLayerCount() > 0:
        sym_layer = symbol.symbolLayer(0)
        sym_layer.setFillColor(QColor(255, 255, 255, 0))  # Transparent fill
        sym_layer.setStrokeColor(QColor("#3704ba"))       # Purple border
        sym_layer.setStrokeWidth(0.8)

    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

def style_grid(layer):
    """
    Styles grid with no fill and subtle gray borders.
    """
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())

    if symbol is not None and symbol.symbolLayerCount() > 0:
        sym_layer = symbol.symbolLayer(0)
        sym_layer.setFillColor(QColor(255, 255, 255, 0))  # Transparent fill
        sym_layer.setStrokeColor(QColor("#888888"))       # Light gray border
        sym_layer.setStrokeWidth(0.3)

    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)
    layer.triggerRepaint()