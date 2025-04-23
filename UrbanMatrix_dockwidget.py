import os
from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget, QMessageBox,
    QDesktopWidget,QFileDialog,
)
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer
from .utils.grid_tools import create_grid_from_raster
from .utils.data_ingestion import download_ms_buildings_from_extent
from .utils.classification import calculate_coverage
from .utils.matrix_calculation import assign_matrix_scores
from .utils.styling import style_by_density_class, style_buildings_footprint


class UrbanMatrixDockWidget(QDockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        QgsProject.instance().layerWasAdded.connect(self.refresh_layer_dropdowns)
        super().__init__(parent)
        self.setFloating(True)
        #self.resize(400, 300)  # Optional: set initial size
        screen = QDesktopWidget().screenGeometry()
        widget_size = self.geometry()
        x = (screen.width() - widget_size.width()) // 2
        y = (screen.height() - widget_size.height()) // 2
        self.move(x, y)
        self.setWindowTitle("UrbanMatrix")

        # Create main layout
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # --- Raster Layer Selector ---
        self.raster_label = QLabel("Select raster layer:")
        self.rasterCombo = QComboBox()
        self.layout.addWidget(self.raster_label)
        self.layout.addWidget(self.rasterCombo)

        # --- Import Raster Button ---
        self.importRasterBtn = QPushButton("Import Raster Image")
        self.layout.addWidget(self.importRasterBtn)
        self.importRasterBtn.clicked.connect(self.import_raster)

        # --- Grid Cell Size Input ---
        self.size_label = QLabel("Grid cell size (map units):")
        self.cellSizeInput = QLineEdit()
        self.cellSizeInput.setPlaceholderText("e.g., 100")
        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.cellSizeInput)

        # --- Generate Button ---
        self.generateGridBtn = QPushButton("Generate Grid")
        self.layout.addWidget(self.generateGridBtn)

        # Connect button action
        self.generateGridBtn.clicked.connect(self.run_grid_generator)

        # Fill combo with raster layers
        self.populate_raster_combo()

        # --- External Layer Download Section ---
        self.downloadLabel = QLabel("Download external data:")
        self.externalSourceCombo = QComboBox()
        self.externalSourceCombo.addItems(["Microsoft Buildings"])  # Add more later
        self.downloadBtn = QPushButton("Download")

        self.layout.addWidget(self.downloadLabel)
        self.layout.addWidget(self.externalSourceCombo)
        self.layout.addWidget(self.downloadBtn)

        self.downloadBtn.clicked.connect(self.download_selected_layer)

        # --- Applicaitons: Classification Section ---
        #self.refresh_layer_dropdowns()
        self.gridLayerLabel = QLabel("Select Grid Layer:")
        self.gridLayerCombo = QComboBox()

        self.featureLayerLabel = QLabel("Select Feature Layer (e.g. buildings):")
        self.classifyLayerCombo = QComboBox()

        self.layout.addWidget(self.gridLayerLabel)
        self.layout.addWidget(self.gridLayerCombo)
        self.layout.addWidget(self.featureLayerLabel)
        self.layout.addWidget(self.classifyLayerCombo)
        self.runClassificationBtn = QPushButton("Run Matrix Method classification") #Matrix Method classification (coverage + risk score)
        ### add classification thresholds
        self.thresholdLabel = QLabel("Set classification thresholds (%):")
        self.lowThreshInput = QLineEdit()
        self.lowThreshInput.setPlaceholderText("Low / Moderate (default: 25)")
        self.lowThreshInput.setText("25")
        self.midThreshInput = QLineEdit()
        self.midThreshInput.setPlaceholderText("Moderate / High (default: 50)")
        self.midThreshInput.setText("50")
        self.highThreshInput = QLineEdit()
        self.highThreshInput.setPlaceholderText("High / Very High (default: 75)")
        self.highThreshInput.setText("75")
        self.layout.addWidget(self.thresholdLabel)
        self.layout.addWidget(self.lowThreshInput)
        self.layout.addWidget(self.midThreshInput)
        self.layout.addWidget(self.highThreshInput)
        ## Connect button action
        self.layout.addWidget(self.runClassificationBtn)
        self.runClassificationBtn.clicked.connect(self.classify_grid_coverage)


    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def populate_raster_combo(self):
        self.rasterCombo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer):
                self.rasterCombo.addItem(layer.name(), layer.id())

    def refresh_layer_dropdowns(self):
        """Refresh both grid and feature layer dropdowns based on current project layers."""
        self.gridLayerCombo.clear()
        self.classifyLayerCombo.clear()

        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsVectorLayer.VectorLayer:
                self.gridLayerCombo.addItem(layer.name(), layer.id())
                if layer.geometryType() in [1, 2]:  # Line or Polygon
                    self.classifyLayerCombo.addItem(layer.name(), layer.id())


    def show_message(self, message):
        QMessageBox.information(self, "UrbanMatrix", message)

    def run_grid_generator(self):
        layer_id = self.rasterCombo.currentData()
        cell_size_str = self.cellSizeInput.text()

        if not cell_size_str.strip():
            self.show_message("Please enter a grid cell size.")
            return

        try:
            cell_size = float(cell_size_str)
        except ValueError:
            self.show_message("Cell size must be a number.")
            return

        raster_layer = QgsProject.instance().mapLayer(layer_id)
        if not raster_layer:
            self.show_message("No valid raster selected.")
            return

        try:
            create_grid_from_raster(raster_layer, cell_size, "UrbanMatrix_Grid")
            self.show_message("Grid created successfully.")
        except Exception as e:
            self.show_message(f"Error: {e}")

    def import_raster(self):
        """Browse and load a raster file into the QGIS project."""

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Raster Image",
            "", "Raster Files (*.tif *.tiff *.vrt *.jpg *.jpeg *.png);;All Files (*)"
        )

        if not file_path:
            return  # user cancelled

        layer_name = os.path.basename(file_path)
        raster_layer = QgsRasterLayer(file_path, layer_name)

        if not raster_layer.isValid():
            self.show_message("Failed to load raster. Make sure it's a supported format.")
            return

        QgsProject.instance().addMapLayer(raster_layer)
        self.populate_raster_combo()
        #Auto-Select It in the Dropdown
        index = self.rasterCombo.findText(layer_name)
        if index >= 0:
            self.rasterCombo.setCurrentIndex(index)
        self.show_message(f"Raster '{layer_name}' loaded successfully.")

    def download_selected_layer(self):
        source = self.externalSourceCombo.currentText()
        # Try to get the grid layer by name
        grid_layer = QgsProject.instance().mapLayersByName("UrbanMatrix_Grid")
        if not grid_layer:
            self.show_message("No grid found. Please generate one first.")
            return

        grid_layer = grid_layer[0]
        extent_ = grid_layer.extent()
        extent = (extent_.xMinimum(), extent_.yMinimum(), extent_.xMaximum(), extent_.yMaximum())
        crs = grid_layer.crs().authid()

        if source == "Microsoft Buildings":
            layer = download_ms_buildings_from_extent(extent, crs)
            if layer:
                QgsProject.instance().addMapLayer(layer)
                style_buildings_footprint(layer)
                self.show_message("Microsoft buildings downloaded.")
            else:
                self.show_message("Download failed.")

    def classify_grid_coverage(self):
        grid_id = self.gridLayerCombo.currentData()
        feature_id = self.classifyLayerCombo.currentData()

        if not grid_id or not feature_id:
            self.show_message("Please select both grid and feature layers.")
            return

        grid_layer = QgsProject.instance().mapLayer(grid_id)
        feature_layer = QgsProject.instance().mapLayer(feature_id)

        if not grid_layer or not feature_layer:
            self.show_message("Invalid layers selected.")
            return

        try:
            updated_grid = calculate_coverage(grid_layer, feature_layer)
            # Get threshold values
            try:
                low = float(self.lowThreshInput.text())
                mid = float(self.midThreshInput.text())
                high = float(self.highThreshInput.text())
            except ValueError:
                self.show_message("Please enter valid numeric thresholds.")
                return
            #Validate Threshold Logic
            if not (0 <= low < mid < high <= 100):
                self.show_message("Thresholds must be in increasing order between 0 and 100.")
                return
            assign_matrix_scores(updated_grid, low, mid, high)
            QgsProject.instance().addMapLayer(updated_grid)
            style_by_density_class(updated_grid)
        except Exception as e:
            self.show_message(f"Classification failed: {e}")
