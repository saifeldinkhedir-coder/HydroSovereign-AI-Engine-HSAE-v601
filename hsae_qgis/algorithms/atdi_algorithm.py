"""
atdi_algorithm.py — ATDI Processing Algorithm for QGIS Toolbox
Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (
    QgsProcessingAlgorithm, QgsProcessingParameterNumber,
    QgsProcessingParameterString, QgsProcessingOutputNumber,
    QgsProcessingOutputString, QgsProcessingContext, QgsProcessingFeedback,
)


class ATDIAlgorithm(QgsProcessingAlgorithm):
    """
    Alkedir Transparency Deficit Index (ATDI) Calculator.
    Formula: ATDI = clip((I_adj - Q_out) / (I_adj + 0.001), 0, 1) × 100
    where: I_adj = max(0, I_in - 0.30 × (ET_PM + ET_MODIS))
    """

    I_IN    = "I_IN"
    ET_PM   = "ET_PM"
    ET_MODIS= "ET_MODIS"
    Q_OUT   = "Q_OUT"
    ATDI    = "ATDI"
    STATUS  = "STATUS"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber(
            self.I_IN, "Inflow I_in (m³/s)", defaultValue=100.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.ET_PM, "Penman-Monteith ET (mm/day)", defaultValue=3.5,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.ET_MODIS, "MODIS ET (mm/day)", defaultValue=2.8,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.Q_OUT, "Observed outflow Q_out (m³/s)", defaultValue=40.0,
            type=QgsProcessingParameterNumber.Double))
        self.addOutput(QgsProcessingOutputNumber(self.ATDI, "ATDI (%)"))
        self.addOutput(QgsProcessingOutputString(self.STATUS, "Legal Status"))

    def processAlgorithm(self, parameters, context, feedback):
        i_in     = self.parameterAsDouble(parameters, self.I_IN, context)
        et_pm    = self.parameterAsDouble(parameters, self.ET_PM, context)
        et_modis = self.parameterAsDouble(parameters, self.ET_MODIS, context)
        q_out    = self.parameterAsDouble(parameters, self.Q_OUT, context)

        # α = 0.30 (Alkedir MODIS ET Correction Coefficient)
        ALPHA = 0.30
        i_adj = max(0.0, i_in - ALPHA * (et_pm + et_modis))
        tdi   = max(0.0, min(1.0, (i_adj - q_out) / (i_adj + 0.001)))
        atdi  = round(tdi * 100, 2)

        # UNWC 1997 legal thresholds
        if atdi >= 85:
            status = "EMERGENCY — Art.33 ICJ Referral"
        elif atdi >= 70:
            status = "CRITICAL — Art.12 Mandatory Notification"
        elif atdi >= 55:
            status = "CONCERN — Art.9 Data Exchange Required"
        elif atdi >= 40:
            status = "VIOLATION — Art.7 No-Harm Triggered"
        elif atdi >= 25:
            status = "REVIEW — Art.5 Equitable Use Review"
        else:
            status = "COMPLIANT — No threshold triggered"

        feedback.pushInfo(f"I_adj  = {i_adj:.3f} m³/s")
        feedback.pushInfo(f"TDI    = {tdi:.4f}")
        feedback.pushInfo(f"ATDI   = {atdi:.2f}%")
        feedback.pushInfo(f"Status = {status}")

        return {self.ATDI: atdi, self.STATUS: status}

    def name(self):
        return "calculate_atdi"

    def displayName(self):
        return "Calculate ATDI (Alkedir Transparency Deficit Index)"

    def group(self):
        return "Water Sovereignty Indices"

    def groupId(self):
        return "hsae_indices"

    def shortHelpString(self):
        return (
            "Computes the Alkedir Transparency Deficit Index (ATDI) for a "
            "transboundary river basin and maps the result to UNWC 1997 legal "
            "thresholds.\n\n"
            "Formula:\n"
            "  I_adj = max(0, I_in − 0.30 × (ET_PM + ET_MODIS))\n"
            "  ATDI  = clip((I_adj − Q_out) / (I_adj + 0.001), 0, 1) × 100\n\n"
            "Legal thresholds (UNWC 1997):\n"
            "  ≥25% → Art. 5 Equitable Use\n"
            "  ≥40% → Art. 7 No Harm\n"
            "  ≥55% → Art. 9 Data Exchange\n"
            "  ≥70% → Art. 12 Notification\n"
            "  ≥85% → Art. 33 ICJ/PCA/ITLOS\n\n"
            "Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991"
        )

    def createInstance(self):
        return ATDIAlgorithm()
