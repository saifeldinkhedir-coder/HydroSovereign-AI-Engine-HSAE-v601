"""
hifd_algorithm.py — HIFD Processing Algorithm for QGIS Toolbox
Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (
    QgsProcessingAlgorithm, QgsProcessingParameterNumber,
    QgsProcessingOutputNumber, QgsProcessingOutputString,
    QgsProcessingContext, QgsProcessingFeedback,
)


class HIFDAlgorithm(QgsProcessingAlgorithm):
    """
    Human-Induced Flow Deficit (HIFD) Calculator.
    Formula: HIFD = (Q_natural - Q_observed) / Q_natural × 100
    Maps result to UNWC 1997 Articles 5, 7, 12, 17, 33.
    """

    Q_NAT  = "Q_NAT"
    Q_OBS  = "Q_OBS"
    HIFD   = "HIFD"
    ARTICLE= "ARTICLE"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber(
            self.Q_NAT, "Natural (HBV) flow Q_nat (m³/s)", defaultValue=150.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.Q_OBS, "Observed outflow Q_obs (m³/s)", defaultValue=95.0,
            type=QgsProcessingParameterNumber.Double))
        self.addOutput(QgsProcessingOutputNumber(self.HIFD, "HIFD (%)"))
        self.addOutput(QgsProcessingOutputString(self.ARTICLE, "Triggered UNWC Article"))

    def processAlgorithm(self, parameters, context, feedback):
        q_nat = self.parameterAsDouble(parameters, self.Q_NAT, context)
        q_obs = self.parameterAsDouble(parameters, self.Q_OBS, context)

        if q_nat <= 0:
            feedback.reportError("Q_nat must be > 0")
            return {self.HIFD: 0.0, self.ARTICLE: "Invalid input"}

        hifd = max(0.0, (q_nat - q_obs) / q_nat * 100)
        hifd = round(hifd, 2)

        # HIFD → UNWC 1997 legal thresholds
        if hifd >= 80:
            article = "Art.33 — Emergency: ICJ/PCA referral required"
        elif hifd >= 60:
            article = "Art.17 — Critical: Mandatory consultations"
        elif hifd >= 40:
            article = "Art.12 — Violation: Prior notification obligation"
        elif hifd >= 20:
            article = "Art.7 — Concern: No-harm obligation triggered"
        elif hifd >= 10:
            article = "Art.5 — Review: Equitable utilisation assessment"
        else:
            article = "Compliant — No UNWC threshold triggered"

        feedback.pushInfo(f"Q_nat  = {q_nat:.3f} m³/s")
        feedback.pushInfo(f"Q_obs  = {q_obs:.3f} m³/s")
        feedback.pushInfo(f"HIFD   = {hifd:.2f}%")
        feedback.pushInfo(f"Status = {article}")

        return {self.HIFD: hifd, self.ARTICLE: article}

    def name(self):
        return "calculate_hifd"

    def displayName(self):
        return "Calculate HIFD (Human-Induced Flow Deficit)"

    def group(self):
        return "Water Sovereignty Indices"

    def groupId(self):
        return "hsae_indices"

    def shortHelpString(self):
        return (
            "Computes the Human-Induced Flow Deficit (HIFD) and maps it to "
            "UNWC 1997 legal articles.\n\n"
            "Formula:\n"
            "  HIFD = (Q_natural − Q_observed) / Q_natural × 100\n\n"
            "Q_natural is the HBV-modelled natural flow baseline.\n"
            "Q_observed is the measured downstream outflow.\n\n"
            "UNWC 1997 thresholds:\n"
            "  >10% → Art. 5 Equitable Use review\n"
            "  >20% → Art. 7 No-harm obligation\n"
            "  >40% → Art. 12 Prior notification\n"
            "  >60% → Art. 17 Mandatory consultations\n"
            "  >80% → Art. 33 ICJ/PCA/ITLOS referral\n\n"
            "Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991"
        )

    def createInstance(self):
        return HIFDAlgorithm()
