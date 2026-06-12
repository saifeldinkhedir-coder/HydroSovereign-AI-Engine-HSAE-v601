"""
export_tool.py — HSAE v6.0.10
Export Basin Data to Shapefile / GeoJSON / CSV
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
import json


def export_basins(basins: list, path: str) -> bool:
    """
    Export basin data to file.
    Supports: .geojson, .shp (via QGIS), .csv
    """
    if path.endswith('.csv'):
        return _export_csv(basins, path)
    elif path.endswith('.geojson'):
        return _export_geojson(basins, path)
    else:
        return _export_shapefile(basins, path)


def _export_geojson(basins: list, path: str) -> bool:
    features = []
    for b in basins:
        lat = float(b.get('lat', 0))
        lon = float(b.get('lon', 0))
        if not lat or not lon:
            continue
        clist = (
            ', '.join(
                b.get(
                    'country',
                    [])) if isinstance(
                b.get('country'),
                list) else b.get(
                    'country_up',
                ''))
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "id": b.get('id', ''),
                "name": b.get('name', ''),
                "river": b.get('river', ''),
                "dam": b.get('dam', ''),
                "continent": b.get('continent', b.get('region', '')),
                "countries": clist,
                "treaty": b.get('treaty', ''),
                "legal_arts": b.get('legal_arts', ''),
                "storage_bcm": float(b.get('cap', b.get('cap_bcm', 0))),
                "area_km2": float(b.get('eff_cat_km2', b.get('area_km2', 0))),
                "runoff_c": float(b.get('runoff_c', 0.3)),
                "context": b.get('context', ''),
            }
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": features}, f,
                  indent=2, ensure_ascii=False)
    return True


def _export_csv(basins: list, path: str) -> bool:
    with open(path, 'w', encoding='utf-8') as f:
        f.write("id,name,river,dam,continent,countries,treaty,legal_arts,"
                "storage_bcm,area_km2,runoff_c,lat,lon,context\n")
        for b in basins:
            clist = (
                ', '.join(
                    b.get(
                        'country',
                        [])) if isinstance(
                    b.get('country'),
                    list) else b.get(
                    'country_up',
                    ''))
            f.write(f"{b.get('id', '')},"
                    f"{b.get('name', '')},"
                    f"{b.get('river', '')},"
                    f"{b.get('dam', '')},"
                    f"{b.get('continent', b.get('region', ''))},"
                    f"\"{clist}\","
                    f"{b.get('treaty', '')},"
                    f"{b.get('legal_arts', '')},"
                    f"{float(b.get('cap', b.get('cap_bcm', 0)))},"
                    f"{float(b.get('eff_cat_km2', b.get('area_km2', 0)))},"
                    f"{float(b.get('runoff_c', 0.3))},"
                    f"{float(b.get('lat', 0))},"
                    f"{float(b.get('lon', 0))},"
                    f"\"{b.get('context', '')[:100]}\"\n")
    return True


def _export_shapefile(basins: list, path: str) -> bool:
    """Export to Shapefile via QGIS."""
    try:
        from .basin_loader import load_basin_layer
        from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem
        lyr = load_basin_layer(basins)
        err = QgsVectorFileWriter.writeAsVectorFormat(
            lyr, path, "UTF-8",
            QgsCoordinateReferenceSystem("EPSG:4326"),
            "ESRI Shapefile")
        return err[0] == QgsVectorFileWriter.NoError
    except Exception as e:
        print(f"Shapefile export error: {e}")
        return False
