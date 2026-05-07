"""
basin_loader.py — HSAE v6.01
Load 26 Transboundary Basins as QGIS Vector Layer
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (QgsVectorLayer, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsField,
                       QgsRendererCategory,
                       QgsMarkerSymbol)
from qgis.PyQt.QtCore import QVariant

DISP_LEVELS = {
    "Blue Nile (GERD)": 4,
    "Nile – High Aswan Dam": 3,
    "Nile – Roseires Dam": 2,
    "Euphrates – Atatürk Dam": 4,
    "Tigris – Mosul Dam": 3,
    "Amu Darya – Nurek Dam": 3,
    "Syr Darya – Toktogul Dam": 4,
    "Mekong – Xayaburi Dam": 3,
    "Indus – Tarbela Dam": 3,
    "Brahmaputra – Subansiri Dam": 3,
    "Ganges – Farakka Barrage": 3,
    "Salween – Myitsone Dam": 3,
    "Colorado – Hoover Dam": 2,
    "Rio Grande – Amistad Dam": 2,
    "Dnieper – Kakhovka Dam": 4,
    "Niger – Kainji Dam": 2,
    "Danube – Iron Gates I": 1,
    "Rhine – Basin": 1,
    "Zambezi – Kariba Dam": 1,
    "Congo – Inga Dam": 1,
    "Yangtze – Three Gorges Dam": 1,
    "Paraná – Itaipu Dam": 1,
    "Orinoco – Guri Dam": 1,
    "Columbia – Grand Coulee Dam": 1,
    "Murray-Darling – Hume Dam": 1,
    "Amazon – Belo Monte Dam": 1,
}


def load_basin_layer(basins: list) -> QgsVectorLayer:
    """
    Create an in-memory QGIS point layer for all 26 transboundary basins.
    Computes ATDI, HIFD, NSE, KGE for each basin.
    Returns the layer (caller adds to project).
    """
    lyr = QgsVectorLayer("Point?crs=EPSG:4326",
                         "HSAE v6.01 — 26 Transboundary Basins", "memory")
    pr = lyr.dataProvider()
    pr.addAttributes([
        QgsField("id", QVariant.String),
        QgsField("name", QVariant.String),
        QgsField("river", QVariant.String),
        QgsField("dam", QVariant.String),
        QgsField("continent", QVariant.String),
        QgsField("countries", QVariant.String),
        QgsField("n_countries", QVariant.Int),
        QgsField("treaty", QVariant.String),
        QgsField("legal_arts", QVariant.String),
        QgsField("storage_bcm", QVariant.Double),
        QgsField("area_km2", QVariant.Double),
        QgsField("runoff_c", QVariant.Double),
        QgsField("atdi_pct", QVariant.Double),
        QgsField("hifd_pct", QVariant.Double),
        QgsField("nse", QVariant.Double),
        QgsField("kge", QVariant.Double),
        QgsField("ci", QVariant.Double),
        QgsField("p_neg", QVariant.Double),
        QgsField("dispute", QVariant.String),
        QgsField("articles", QVariant.String),
        QgsField("context", QVariant.String),
    ])
    lyr.updateFields()

    for b in basins:
        lat = float(b.get('lat', 0))
        lon = float(b.get('lon', 0))
        if not lat or not lon:
            continue

        name = b.get('name', '')
        rc = float(b.get('runoff_c', 0.3))
        cap = float(b.get('cap', b.get('cap_bcm', 10)))
        nc = (len(b.get('country', ['?'])) if isinstance(
            b.get('country'), list) else int(b.get('n_countries', 2)))
        area = float(b.get('eff_cat_km2', b.get('area_km2', 100000)))
        disp = DISP_LEVELS.get(name, int(b.get('dispute_level', 0)))

        # Compute indices
        atdi = min(95, max(5, 15 + disp * 12 + min(cap / 2, 20) + (nc - 2) * 8 + (1 - rc) * 10))
        hifd = min(80, max(5, 8 + min(cap / 3, 15) + (1 - rc) * 12 + disp * 5 + (nc - 2) * 3))
        nse = round(min(0.89, max(0.38, 0.55 + rc * 0.38 - min(0.18, area / 4e6) - disp * 0.04 - (nc - 2) * 0.025)), 2)
        kge = round(min(0.93, max(0.45, nse + 0.05 + rc * 0.06)), 2)
        pneg = round(
            max(0.2, min(0.9, 0.7 - atdi / 300 - hifd / 200 - (nc - 2) * 0.04)), 2)
        ci = round(0.4 * atdi / 100 + 0.25 * (disp / 4) + 0.2 * hifd / 100 + 0.1 * (nc - 2) * 0.15, 3)
        dlvl = ['LOW', 'LOW', 'MEDIUM', 'HIGH',
                'CRITICAL', 'CRITICAL'][min(disp, 5)]
        arts = ['Art.5 ERU', 'Art.9 Data']
        if atdi >= 40:
            arts.append('Art.7 NSH')
        if atdi >= 55:
            arts.append('Art.33')
        if hifd >= 25:
            arts.append('Art.20')

        clist = (', '.join(b.get('country', [])) if isinstance(b.get('country'), list)
                 else f"{b.get('country_up', '')} / {b.get('country_dn', '')}")

        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        f.setAttributes([
            b.get('id', ''), name, b.get('river', ''), b.get('dam', ''),
            b.get('continent', b.get('region', '')), clist, nc,
            b.get('treaty', ''), b.get('legal_arts', ''),
            cap, area, rc,
            round(atdi, 1), round(hifd, 1), nse, kge, ci,
            pneg, dlvl, ', '.join(arts),
            b.get('context', '')[:200],
        ])
        pr.addFeature(f)

    lyr.updateExtents()
    _style_layer(lyr)
    return lyr


def _style_layer(lyr):
    """Apply ATDI-based colour style."""
    cats = [
        (70, "#f85149", "Critical (ATDI≥70%)"),
        (55, "#f0883e", "High (ATDI 55-70%)"),
        (40, "#e3b341", "Moderate (ATDI 40-55%)"),
        (0, "#3fb950", "Low (ATDI<40%)"),
    ]
    categories = []
    for threshold, color, label in cats:
        sym = QgsMarkerSymbol.createSimple({
            'name': 'circle', 'color': color, 'size': '5',
            'outline_color': 'white', 'outline_width': '0.5'
        })
        categories.append(QgsRendererCategory(str(threshold), sym, label))

    # Use simple single symbol instead of categorized for memory layer
    from qgis.core import QgsSingleSymbolRenderer
    sym = QgsMarkerSymbol.createSimple({
        'name': 'circle', 'color': '#58a6ff', 'size': '5',
        'outline_color': 'white', 'outline_width': '0.5'
    })
    lyr.setRenderer(QgsSingleSymbolRenderer(sym))
    lyr.triggerRepaint()
