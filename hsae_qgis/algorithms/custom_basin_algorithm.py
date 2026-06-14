"""
algorithms/custom_basin_algorithm.py — HSAE v6.0.13
====================================================
QGIS Processing Algorithm: Custom Basin AWSI Calculator

Allows running HSAE analysis on any user-defined basin
directly from the QGIS Processing Toolbox or graphical modeller.

Author:  Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFields,
    QgsField,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant
from hsae_qgis.custom_basin_tool import estimate_runoff_c
from hsae_qgis.core.indices import compute_all


class CustomBasinAlgorithm(QgsProcessingAlgorithm):
    """QGIS Processing Algorithm for custom basin AWSI analysis."""

    # Input parameter IDs
    NAME = "NAME"
    LAT = "LAT"
    LON = "LON"
    CAP_BCM = "CAP_BCM"
    RUNOFF_C = "RUNOFF_C"
    N_CNTRY = "N_COUNTRIES"
    DISP_LVL = "DISPUTE_LEVEL"
    OUTPUT = "OUTPUT"

    # Output IDs
    OUT_ATDI = "ATDI"
    OUT_AHIFD = "AHIFD"
    OUT_ATCI = "ATCI"
    OUT_CI = "CI"
    OUT_RISK = "RISK"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString(
            self.NAME, "Basin / Dam name", defaultValue="Custom Basin"))

        self.addParameter(QgsProcessingParameterNumber(
            self.LAT, "Latitude (decimal degrees, -90 to 90)",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.0, minValue=-90.0, maxValue=90.0))

        self.addParameter(QgsProcessingParameterNumber(
            self.LON, "Longitude (decimal degrees, -180 to 180)",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.0, minValue=-180.0, maxValue=180.0))

        self.addParameter(QgsProcessingParameterNumber(
            self.CAP_BCM, "Dam storage capacity (BCM)",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=10.0, minValue=0.1, maxValue=1000.0))

        self.addParameter(QgsProcessingParameterNumber(
            self.RUNOFF_C,
            "Runoff coefficient (0=auto-estimate from lat/lon)",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.0, minValue=0.0, maxValue=0.95))

        self.addParameter(QgsProcessingParameterNumber(
            self.N_CNTRY, "Number of riparian countries",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=3, minValue=2, maxValue=15))

        self.addParameter(QgsProcessingParameterNumber(
            self.DISP_LVL,
            "Dispute intensity level (1=Low, 2=Moderate, 3=High, 4=Critical)",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=2, minValue=1, maxValue=4))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, "Output point layer",
            QgsProcessing.TypeVectorPoint))

        self.addOutput(QgsProcessingOutputNumber(self.OUT_ATDI, "ATDI (%)"))
        self.addOutput(QgsProcessingOutputNumber(self.OUT_AHIFD, "AHIFD (%)"))
        self.addOutput(QgsProcessingOutputNumber(self.OUT_ATCI, "ATCI (0-100)"))
        self.addOutput(QgsProcessingOutputNumber(self.OUT_CI, "Conflict Index"))
        self.addOutput(QgsProcessingOutputString(self.OUT_RISK, "Risk level"))

    def processAlgorithm(self, parameters, context, feedback):
        name = self.parameterAsString(parameters, self.NAME, context)
        lat = self.parameterAsDouble(parameters, self.LAT, context)
        lon = self.parameterAsDouble(parameters, self.LON, context)
        cap_bcm = self.parameterAsDouble(parameters, self.CAP_BCM, context)
        rc_input = self.parameterAsDouble(parameters, self.RUNOFF_C, context)
        nc = self.parameterAsInt(parameters, self.N_CNTRY, context)
        disp = self.parameterAsInt(parameters, self.DISP_LVL, context)

        # Auto-estimate runoff if not provided (0 = auto)
        rc = rc_input if rc_input > 0.01 else estimate_runoff_c(lat, lon)
        feedback.pushInfo(f"Using runoff coefficient: {rc:.3f}")

        # Compute AWSI
        result = compute_all(
            runoff_c=rc, cap_bcm=cap_bcm,
            n_countries=nc, dispute_level=disp)

        feedback.pushInfo(
            f"ATDI={result['atdi']}% | AHIFD={result['ahifd']}% | "
            f"ATCI={result['atci']} | CI={result['ci']} | Risk={result['risk']}")

        if result["articles"]:
            feedback.pushInfo(
                f"Triggered: {', '.join(result['articles'])}")

        # Build output layer
        fields = QgsFields()
        for fname, ftype in [
            ("name", QVariant.String),
            ("lat", QVariant.Double),
            ("lon", QVariant.Double),
            ("cap_bcm", QVariant.Double),
            ("runoff_c", QVariant.Double),
            ("n_countries", QVariant.Int),
            ("dispute_level", QVariant.Int),
            ("atdi", QVariant.Double),
            ("ahifd", QVariant.Double),
            ("afsf", QVariant.Double),
            ("ahlb", QVariant.Double),
            ("asi", QVariant.Double),
            ("atci", QVariant.Double),
            ("ci", QVariant.Double),
            ("pneg", QVariant.Double),
            ("risk", QVariant.String),
            ("articles", QVariant.String),
        ]:
            fields.append(QgsField(fname, ftype))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            fields, QgsWkbTypes.Point, None)

        feat = QgsFeature(fields)
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        feat["name"] = name
        feat["lat"] = lat
        feat["lon"] = lon
        feat["cap_bcm"] = cap_bcm
        feat["runoff_c"] = rc
        feat["n_countries"] = nc
        feat["dispute_level"] = disp
        feat["atdi"] = result["atdi"]
        feat["ahifd"] = result["ahifd"]
        feat["afsf"] = result["afsf"]
        feat["ahlb"] = result["ahlb"]
        feat["asi"] = result["asi"]
        feat["atci"] = result["atci"]
        feat["ci"] = result["ci"]
        feat["pneg"] = result["pneg"]
        feat["risk"] = result["risk"]
        feat["articles"] = ", ".join(result["articles"])
        sink.addFeature(feat)

        return {
            self.OUTPUT: dest_id,
            self.OUT_ATDI: result["atdi"],
            self.OUT_AHIFD: result["ahifd"],
            self.OUT_ATCI: result["atci"],
            self.OUT_CI: result["ci"],
            self.OUT_RISK: result["risk"],
        }

    def name(self):
        return "custombasinanalyser"

    def displayName(self):
        return "Custom Basin AWSI Analyser"

    def group(self):
        return "HSAE — Custom Analysis"

    def groupId(self):
        return "hsae_custom"

    def shortHelpString(self):
        return (
            "Compute all 6 AWSI indices (ATDI, AHIFD, AFSF, AHLB, ASI, ATCI) "
            "for any user-defined transboundary basin.\n\n"
            "Set runoff coefficient to 0 to auto-estimate from lat/lon "
            "using a Koppen-Geiger climate zone lookup.\n\n"
            "Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991")

    def createInstance(self):
        return CustomBasinAlgorithm()
