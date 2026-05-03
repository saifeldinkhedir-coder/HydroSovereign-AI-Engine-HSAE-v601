"""
hifd_algorithm.py — HSAE v6.01 QGIS Processing Algorithm
HIFD: Human-Induced Flow Deficit
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterNumber,
                       QgsProcessingOutputNumber)


class HIFDAlgorithm(QgsProcessingAlgorithm):

    RC = 'RC'
    CAP = 'CAP'
    NC = 'NC'
    DISP = 'DISP'
    OUT = 'HIFD'

    def name(self): return 'hifdcalculator'
    def displayName(self): return 'HIFD Calculator'
    def group(self): return 'HSAE Indices'
    def groupId(self): return 'hsaeindices'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber(
            self.RC, 'Runoff Coefficient (0-1)', defaultValue=0.38,
            minValue=0.01, maxValue=0.99,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.CAP, 'Dam Storage Capacity (BCM)', defaultValue=74.0,
            minValue=0.1, maxValue=500.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.NC, 'Number of Riparian Countries', defaultValue=3,
            minValue=1, maxValue=20))
        self.addParameter(QgsProcessingParameterNumber(
            self.DISP, 'Dispute Level (0-4)', defaultValue=0,
            minValue=0, maxValue=4))
        self.addOutput(QgsProcessingOutputNumber(self.OUT, 'HIFD (%)'))

    def processAlgorithm(self, parameters, context, feedback):
        rc = self.parameterAsDouble(parameters, self.RC, context)
        cap = self.parameterAsDouble(parameters, self.CAP, context)
        nc = self.parameterAsInt(parameters, self.NC, context)
        disp = self.parameterAsInt(parameters, self.DISP, context)
        hifd = min(80.0, max(5.0, 8 + min(cap / 3, 15) +
                   (1 - rc) * 12 + disp * 5 + (nc - 2) * 3))
        feedback.pushInfo(f'HIFD = {hifd:.2f}%')
        return {self.OUT: hifd}

    def createInstance(self):
        return HIFDAlgorithm()
