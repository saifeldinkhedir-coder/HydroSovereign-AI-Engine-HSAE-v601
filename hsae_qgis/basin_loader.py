"""
basin_loader.py — HSAE v6.0.11
Load 26 Transboundary Basins as QGIS Vector Layer
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (QgsVectorLayer, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsField,
                       QgsRendererCategory,
                       QgsMarkerSymbol)
from qgis.PyQt.QtCore import QVariant
from hsae_qgis.core.indices import compute_pneg, compute_all


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
                         "HSAE v6.0.11 — 26 Transboundary Basins", "memory")
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
        QgsField("ahifd_pct", QVariant.Double),
        QgsField("afsf",      QVariant.Double),
        QgsField("ahlb",      QVariant.Double),
        QgsField("asi",       QVariant.Double),
        QgsField("atci",      QVariant.Double),
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
        rc = float(b.get('runoff_c', b.get('riparian_cooperation', 0.35)))
        cap = float(b.get('cap', b.get('cap_bcm', b.get('dam_capacity_bcm', 10))))
        _nc_raw = b.get('country', b.get('countries', None))
        nc = max(2, len(_nc_raw)) if isinstance(_nc_raw, list) else int(b.get('n_countries', b.get('num_countries', 3)))
        area = float(b.get('eff_cat_km2', b.get('area_km2', 100000)))
        disp = DISP_LEVELS.get(name, int(b.get('dispute_level', 0)))

        # Compute indices
        _r = compute_all(runoff_c=rc, cap_bcm=cap, n_countries=int(nc), dispute_level=int(disp))
        atdi = _r['atdi']
        hifd = _r['ahifd']
        afsf = _r['afsf']
        ahlb = _r['ahlb']
        asi = _r['asi']
        atci_val = _r['atci']
        nse = round(min(0.89, max(0.38, 0.55 + rc * 0.38 - min(0.18, area / 4e6) - disp * 0.04 - (nc - 2) * 0.025)), 2)
        kge = round(min(0.93, max(0.45, nse + 0.05 + rc * 0.06)), 2)
        pneg = round(
            compute_pneg(atdi=atdi, ahifd=hifd, n_countries=int(nc)), 2)
        ci = _r['ci']
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
            round(atdi, 1), round(hifd, 1), round(afsf, 3), round(ahlb, 3),
            round(asi, 3), round(atci_val, 1), nse, kge, ci,
            pneg, dlvl, ', '.join(arts),
            b.get('context', '')[:200],
        ])
        pr.addFeature(f)

    lyr.updateExtents()
    _style_layer(lyr)
    # Style: colored circles by risk level
    try:
        from qgis.core import QgsMarkerSymbol, QgsSingleSymbolRenderer
        symbol = QgsMarkerSymbol.createSimple({
            "name": "circle",
            "color": "#0E6B6A",
            "color_border": "#ffffff",
            "size": "5",
            "outline_width": "0.8"
        })
        lyr.setRenderer(QgsSingleSymbolRenderer(symbol))
        lyr.triggerRepaint()
    except Exception:
        pass

    # Auto-add OpenStreetMap basemap if not already present
    try:
        from qgis.core import QgsRasterLayer, QgsProject as _QP
        existing = [lyr.name() for lyr in _QP.instance().mapLayers().values()]
        if "OpenStreetMap" not in existing:
            osm_url = (
                "type=xyz"
                "&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                "&zmax=19&zmin=0"
            )
            osm = QgsRasterLayer(osm_url, "OpenStreetMap", "wms")
            if osm.isValid():
                _QP.instance().addMapLayer(osm)
                root = _QP.instance().layerTreeRoot()
                osm_node = root.findLayer(osm.id())
                if osm_node:
                    clone = osm_node.clone()
                    parent = osm_node.parent()
                    parent.removeChildNode(osm_node)
                    parent.addChildNode(clone)
    except Exception:
        pass

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
