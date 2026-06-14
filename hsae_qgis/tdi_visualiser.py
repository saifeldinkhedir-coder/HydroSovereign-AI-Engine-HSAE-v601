"""
tdi_visualiser.py — Apply TDI Graduated Colour Map to Basin Layer
"""
from qgis.core import (
    QgsGraduatedSymbolRenderer, QgsRendererRange,
    QgsMarkerSymbol, QgsProject
)
from qgis.PyQt.QtWidgets import QMessageBox


# ATDI thresholds (UN 1997 legal triggers)
TDI_BREAKS = [
    (0.00, 25.0, "#2ECC71", "MINIMAL  (< 25%)"),
    (25.0, 40.0, "#F1C40F", "LOW      — Art. 5  (25–40%)"),
    (40.0, 55.0, "#E67E22", "MEDIUM   — Art. 7  (40–55%)"),
    (55.0, 100.0, "#E74C3C", "HIGH     — Art. 9  (≥ 55%)"),
]


def apply_tdi_style(iface):
    """Find HSAE basin layer and apply TDI graduated style."""
    layer = _find_basin_layer()
    if layer is None:
        QMessageBox.warning(
            None,
            "HSAE TDI Visualiser — Layer Not Found",
            "No HSAE basin layer found in the current project.\n\n"
            "Please follow these steps:\n"
            "  1. Click: Plugins → HydroSovereign → 🌊 Load Basin Registry\n"
            "  2. Wait for 26 basins to load on the map\n"
            "  3. Then click: 📊 TDI Visualiser\n\n"
            "The TDI style will colour-code all 26 basins by risk level:\n"
            "  🔴 CRITICAL (ATDI ≥ 60%)\n"
            "  🟠 HIGH (40–60%)\n"
            "  🟡 MEDIUM (25–40%)\n"
            "  🟢 LOW (< 25%)"
        )
        return

    ranges = []
    for lo, hi, color, label in TDI_BREAKS:
        symbol = QgsMarkerSymbol.createSimple({
            "name": "circle",
            "color": color,
            "size": "5",
            "outline_color": "white",
            "outline_width": "0.5",
        })
        rng = QgsRendererRange(lo, hi, symbol, label)
        ranges.append(rng)

    renderer = QgsGraduatedSymbolRenderer("tdi_pct", ranges)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

    # Count features by risk tier
    atdi_vals = []
    for feat in layer.getFeatures():
        try:
            atdi_vals.append(float(feat["atdi_pct"]))
        except Exception:
            atdi_vals.append(50.0)

    n_crit = sum(1 for v in atdi_vals if v >= 60)
    n_high = sum(1 for v in atdi_vals if 40 <= v < 60)
    n_med = sum(1 for v in atdi_vals if 25 <= v < 40)
    n_low = sum(1 for v in atdi_vals if v < 25)

    iface.messageBar().pushSuccess(
        "HSAE TDI v6.0.13",
        f"✅ ATDI style applied: "
        f"🔴 {n_crit} CRITICAL · "
        f"🟠 {n_high} HIGH · "
        f"🟡 {n_med} MEDIUM · "
        f"🟢 {n_low} LOW"
    )


def _find_basin_layer():
    """Return the first HSAE basin layer in the project."""
    for layer in QgsProject.instance().mapLayers().values():
        if "HSAE" in layer.name() and "Basin" in layer.name():
            return layer
    return None
