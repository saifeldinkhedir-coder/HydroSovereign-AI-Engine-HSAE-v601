"""
basin_report_algorithm.py — Full Basin Analysis Report
Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (
    QgsProcessingAlgorithm, QgsProcessingParameterString,
    QgsProcessingParameterNumber, QgsProcessingParameterFileDestination,
    QgsProcessingOutputString, QgsProcessingContext, QgsProcessingFeedback,
)
import json
from pathlib import Path


class BasinReportAlgorithm(QgsProcessingAlgorithm):
    """Generate a full HSAE basin analysis report (TXT/JSON)."""

    BASIN_ID = "BASIN_ID"
    Q_NAT    = "Q_NAT"
    Q_OBS    = "Q_OBS"
    I_IN     = "I_IN"
    ET_PM    = "ET_PM"
    ET_MODIS = "ET_MODIS"
    OUTPUT   = "OUTPUT"
    REPORT   = "REPORT"

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString(
            self.BASIN_ID, "Basin ID (e.g. blue_nile_gerd)", defaultValue="blue_nile_gerd"))
        self.addParameter(QgsProcessingParameterNumber(
            self.Q_NAT, "Natural flow Q_nat (m³/s)", defaultValue=1500.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.Q_OBS, "Observed flow Q_obs (m³/s)", defaultValue=820.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.I_IN, "Satellite inflow I_in (m³/s)", defaultValue=1200.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.ET_PM, "Penman-Monteith ET (mm/day)", defaultValue=4.2,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.ET_MODIS, "MODIS ET (mm/day)", defaultValue=3.1,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, "Output Report File", fileFilter="JSON (*.json);;Text (*.txt)"))
        self.addOutput(QgsProcessingOutputString(self.REPORT, "Report Summary"))

    def processAlgorithm(self, parameters, context, feedback):
        basin_id = self.parameterAsString(parameters, self.BASIN_ID, context)
        q_nat    = self.parameterAsDouble(parameters, self.Q_NAT, context)
        q_obs    = self.parameterAsDouble(parameters, self.Q_OBS, context)
        i_in     = self.parameterAsDouble(parameters, self.I_IN, context)
        et_pm    = self.parameterAsDouble(parameters, self.ET_PM, context)
        et_modis = self.parameterAsDouble(parameters, self.ET_MODIS, context)
        output   = self.parameterAsString(parameters, self.OUTPUT, context)

        # Compute indices
        ALPHA = 0.30
        i_adj = max(0.0, i_in - ALPHA * (et_pm + et_modis))
        tdi   = max(0.0, min(1.0, (i_adj - q_obs) / (i_adj + 0.001)))
        atdi  = round(tdi * 100, 2)
        hifd  = round(max(0.0, (q_nat - q_obs) / q_nat * 100), 2) if q_nat > 0 else 0.0
        adts  = round(max(0.0, 100 - atdi), 2)

        # Legal mapping
        def legal_status(val, thresholds):
            for pct, label in sorted(thresholds.items(), reverse=True):
                if val >= pct:
                    return label
            return "Compliant"

        atdi_articles = {25:"Art.5",40:"Art.7",55:"Art.9",70:"Art.12",85:"Art.33"}
        hifd_articles = {10:"Art.5",20:"Art.7",40:"Art.12",60:"Art.17",80:"Art.33"}

        report = {
            "hsae_version": "10.0.0",
            "basin_id":     basin_id,
            "author":       "Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991",
            "inputs": {
                "q_nat_m3s": q_nat, "q_obs_m3s": q_obs,
                "i_in_m3s": i_in, "et_pm_mm_day": et_pm, "et_modis_mm_day": et_modis,
            },
            "computed": {
                "i_adj_m3s": round(i_adj, 3),
                "ATDI_pct":  atdi,
                "HIFD_pct":  hifd,
                "ADTS_pct":  adts,
                "alpha":     ALPHA,
            },
            "legal": {
                "ATDI_article": legal_status(atdi, atdi_articles),
                "HIFD_article": legal_status(hifd, hifd_articles),
                "UNWC_1997":    "UN Watercourses Convention 1997",
            },
        }

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        summary = f"ATDI={atdi}% | HIFD={hifd}% | ADTS={adts}% | {report['legal']['ATDI_article']}"
        feedback.pushInfo(summary)

        return {self.REPORT: summary}

    def name(self):
        return "basin_full_report"

    def displayName(self):
        return "Generate Full Basin Analysis Report"

    def group(self):
        return "Reports & Export"

    def groupId(self):
        return "hsae_reports"

    def shortHelpString(self):
        return (
            "Generates a complete HSAE basin analysis report including "
            "ATDI, HIFD, ADTS indices and UNWC 1997 legal mapping.\n\n"
            "Output: JSON report file with all computed indices.\n\n"
            "Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991"
        )

    def createInstance(self):
        return BasinReportAlgorithm()
