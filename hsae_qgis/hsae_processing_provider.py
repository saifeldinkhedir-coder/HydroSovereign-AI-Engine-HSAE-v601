"""
hsae_processing_provider.py — HSAE v6.0.13
Complete Processing Provider — 6 Algorithms
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import QgsProcessingProvider


class HSAEProcessingProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        from .algorithms.atdi_algorithm import ATDIAlgorithm
        from .algorithms.hifd_algorithm import HIFDAlgorithm
        from .algorithms.basin_report_algorithm import BasinReportAlgorithm
        from .algorithms.hbv_algorithm import HBV96Algorithm
        from .algorithms.comparison_algorithm import MultiBasinComparisonAlgorithm
        from .algorithms.custom_basin_algorithm import CustomBasinAlgorithm

        self.addAlgorithm(ATDIAlgorithm())
        self.addAlgorithm(HIFDAlgorithm())
        self.addAlgorithm(BasinReportAlgorithm())
        self.addAlgorithm(HBV96Algorithm())
        self.addAlgorithm(MultiBasinComparisonAlgorithm())
        self.addAlgorithm(CustomBasinAlgorithm())

    def id(self):
        return "hsae"

    def name(self):
        return "HydroSovereign AI Engine"

    def icon(self):
        return QgsProcessingProvider.icon(self)

    def longName(self):
        return "HydroSovereign AI Engine — AWSI Indices v6.0.13"
