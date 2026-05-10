"""
hsae_processing_provider.py — HSAE v6.01
Complete Processing Provider — 5 Algorithms
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import QgsProcessingProvider
from pathlib import Path


class HSAEProcessingProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        from .algorithms.atdi_algorithm import ATDIAlgorithm
        from .algorithms.hifd_algorithm import HIFDAlgorithm
        from .algorithms.basin_report_algorithm import BasinReportAlgorithm
        from .algorithms.hbv_algorithm import HBV96Algorithm
        from .algorithms.comparison_algorithm import MultiBasinComparisonAlgorithm
        self.addAlgorithm(ATDIAlgorithm())
        self.addAlgorithm(HIFDAlgorithm())
        self.addAlgorithm(BasinReportAlgorithm())
        self.addAlgorithm(HBV96Algorithm())
        self.addAlgorithm(MultiBasinComparisonAlgorithm())

    def id(self):
        return 'hsae'

    def name(self):
        return 'HydroSovereign AI Engine v6.01'

    def longName(self):
        return 'HSAE v6.01 — Transboundary Water Analysis'

    def versionInfo(self):
        return '6.0.1'

    def icon(self):
        from qgis.PyQt.QtGui import QIcon
        return QIcon(str(Path(__file__).parent / 'icon.png'))
