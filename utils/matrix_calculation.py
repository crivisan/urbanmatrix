from qgis.core import QgsField, QgsFeature
from qgis.PyQt.QtCore import QVariant

def assign_matrix_scores(layer, input_field="coverage_pct", output_field="density_class"):
    """
    Assigns Matrix Method risk category based on coverage percentage.
    """
    # Ensure the output field exists
    field_names = [field.name() for field in layer.fields()]
    if output_field not in field_names:
        layer.dataProvider().addAttributes([QgsField(output_field, QVariant.String)])
        layer.updateFields()

    print("[DEBUG] Starting matrix classification...")
    field_index = layer.fields().indexOf(output_field)

    # Update each feature with a class based on coverage_pct
    for feature in layer.getFeatures():
        coverage = feature[input_field]

        # Handle missing/invalid coverage values
        try:
            coverage = float(coverage)
        except (TypeError, ValueError):
            coverage = None

        if coverage is None or coverage == 0:
            category = "NoData"
        elif coverage < 33:
            category = "Low"
        elif coverage < 66:
            category = "Moderate"
        elif coverage <= 100:
            category = "High"
        else:
            category = "Unknown"

        print(f"[DEBUG] FID={feature.id()}, coverage={coverage}, category={category}")

        # Update the feature
        feature.setAttribute(field_index, category)
        layer.dataProvider().changeAttributeValues({feature.id(): {field_index: category}})

    layer.updateFields()
    layer.updateExtents()
    print("[DEBUG] Matrix classification complete.")

    return layer
