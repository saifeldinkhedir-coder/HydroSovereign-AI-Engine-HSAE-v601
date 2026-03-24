"""
hsae_processing_provider.py — HSAE v10.0 QGIS Processing Provider
==================================================================
Registers HSAE algorithms in the QGIS Processing Toolbox.
Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import QgsProcessingProvider
from .algorithms.atdi_algorithm import ATDIAlgorithm
from .algorithms.hifd_algorithm import HIFDAlgorithm
from .algorithms.basin_report_algorithm import BasinReportAlgorithm


class HSAEProcessingProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        self.addAlgorithm(ATDIAlgorithm())
        self.addAlgorithm(HIFDAlgorithm())
        self.addAlgorithm(BasinReportAlgorithm())

    def id(self):
        return "hsae_v10"

    def name(self):
        return "HydroSovereign AI Engine v10.0"

    def longName(self):
        return "HSAE v10.0 — Transboundary Water Sovereignty Analysis"

    def icon(self):
        from qgis.PyQt.QtGui import QIcon
        from pathlib import Path
        icon_path = Path(__file__).parent / "icon.png"
        return QIcon(str(icon_path)) if icon_path.exists() else super().icon()
