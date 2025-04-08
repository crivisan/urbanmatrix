import os
from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget, QMessageBox,
    QDesktopWidget,QFileDialog,
)
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsProject, QgsRasterLayer
from .utils.grid_tools import create_grid_from_raster


class UrbanMatrixDockWidget(QDockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
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


    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def populate_raster_combo(self):
        self.rasterCombo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer):
                self.rasterCombo.addItem(layer.name(), layer.id())

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
            create_grid_from_raster(raster_layer, cell_size)
            self.show_message("Grid created successfully.")
        except Exception as e:
            self.show_message(f"Error: {e}")

    def show_message(self, message):
        QMessageBox.information(self, "UrbanMatrix", message)

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