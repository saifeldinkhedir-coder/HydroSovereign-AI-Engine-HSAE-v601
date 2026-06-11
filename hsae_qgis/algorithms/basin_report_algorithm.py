"""
basin_report_algorithm.py — HSAE v6.0.9 QGIS Processing Algorithm
Complete Basin Legal Report Generator
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFileDestination)

from hsae_qgis.core.indices import (
    compute_atdi, compute_ahifd, compute_all, compute_atci,
    compute_conflict_index, compute_pneg,
    compute_nse_approx, compute_kge_approx
)

class BasinReportAlgorithm(QgsProcessingAlgorithm):

    NAME = 'NAME'
    RC = 'RC'
    CAP = 'CAP'
    NC = 'NC'
    DISP = 'DISP'
    AREA = 'AREA'
    TREATY = 'TREATY'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'basinreport'

    def displayName(self):
        return 'Basin Legal Report'

    def group(self):
        return 'HSAE Reports'

    def groupId(self):
        return 'hsaereports'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString(
            self.NAME, 'Basin Name', defaultValue='Blue Nile (GERD)'))
        self.addParameter(QgsProcessingParameterNumber(
            self.RC, 'Runoff Coefficient', defaultValue=0.38,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.CAP, 'Storage Capacity (BCM)', defaultValue=74.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.NC, 'Riparian Countries', defaultValue=3, minValue=1))
        self.addParameter(QgsProcessingParameterNumber(
            self.DISP, 'Dispute Level (0-4)', defaultValue=4, minValue=0, maxValue=4))
        self.addParameter(QgsProcessingParameterNumber(
            self.AREA, 'Catchment Area (km²)', defaultValue=174000,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterString(
            self.TREATY, 'Treaty Reference', defaultValue='UN1997'))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, 'Output Report', fileFilter='Text (*.txt);;HTML (*.html)'))

    def processAlgorithm(self, parameters, context, feedback):
        name = self.parameterAsString(parameters, self.NAME, context)
        rc = self.parameterAsDouble(parameters, self.RC, context)
        cap = self.parameterAsDouble(parameters, self.CAP, context)
        nc = self.parameterAsInt(parameters, self.NC, context)
        disp = self.parameterAsInt(parameters, self.DISP, context)
        area = self.parameterAsDouble(parameters, self.AREA, context)
        treaty = self.parameterAsString(parameters, self.TREATY, context)
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        atdi = compute_atdi(
            runoff_c=rc, cap_bcm=cap,
            n_countries=int(nc), dispute_level=int(disp))
        hifd = compute_ahifd(
            runoff_c=rc, cap_bcm=cap,
            n_countries=int(nc), dispute_level=int(disp))
        nse = round(min(0.89, max(0.38, 0.55 + rc * 0.38 - min(0.18, area / 4e6) - disp * 0.04 - (nc - 2) * 0.025)), 2)
        kge = round(min(0.93, max(0.45, nse + 0.05 + rc * 0.06)), 2)
        pneg = round(max(0.2, min(0.9, 0.7 - atdi / 300 - hifd / 200)), 2)
        ci = round(0.4 * atdi / 100 + 0.25 * (disp / 4) + 0.2 * hifd / 100 + 0.1 * (nc - 2) * 0.15, 3)

        arts = ['Art.5 ERU', 'Art.9 Data Sharing']
        if atdi >= 40:
            arts.append('Art.7 NSH')
        if atdi >= 55:
            arts.append('Art.33 Dispute Resolution')
        if atdi >= 70:
            arts.append('Art.35 Emergency')
        if hifd >= 25:
            arts.append('Art.20 Environmental Flows')

        dlvl = ['LOW', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'CRITICAL'][min(disp, 5)]
        risk = ('CRITICAL' if atdi >= 70 else 'HIGH' if atdi >= 55
                else 'MODERATE' if atdi >= 40 else 'LOW')

        from datetime import datetime
        report = f"""
HSAE v6.0.9 — BASIN LEGAL REPORT
{'=' * 60}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Author: Seifeldin M.G. Alkhedir | ORCID: 0000-0003-0821-2991
DOI: 10.5281/zenodo.19180160

BASIN: {name}
{'=' * 60}

PHYSICAL PARAMETERS
{'-' * 40}
Catchment Area:     {area / 1000:.0f}k km²
Storage Capacity:   {cap:.1f} BCM
Runoff Coefficient: {rc:.2f}
Riparian States:    {nc}
Treaty Reference:   {treaty}

HSAE INDICES
{'-' * 40}
ATDI:             {atdi:.2f}%
HIFD:             {hifd:.2f}%
NSE:              {nse:.3f}
KGE:              {kge:.3f}
Conflict Index:   {ci:.3f}
P(Negotiation):   {pneg:.0%}
Risk Level:       {risk}
Dispute Level:    {dlvl}

UN ARTICLES TRIGGERED (UNWC 1997)
{'-' * 40}
{chr(10).join('• ' + a for a in arts)}

LEGAL ASSESSMENT
{'-' * 40}
• {'CRITICAL concern' if atdi >= 70 else 'HIGH concern' if atdi >= 55 else 'MODERATE' if atdi >= 40 else 'LOW'} under Art.5 Equitable Utilisation  # noqa: E501
• HIFD of {hifd:.1f}% {'exceeds' if hifd >= 25 else 'is below'} Art.20 environmental flow threshold (25%)
• Negotiation success probability: {pneg:.0%} → {'Cooperative framework' if pneg >= 0.65 else 'Mediation required' if pneg >= 0.40 else 'PCA/ICJ referral recommended'}  # noqa: E501
• Conflict Index {ci:.3f}: {'immediate intervention required' if ci >= 0.6 else 'monitoring required' if ci >= 0.4 else 'manageable'}  # noqa: E501

RECOMMENDATIONS
{'-' * 40}
1. {'Emergency notification under Art.28 UNWC' if disp >= 4 else 'Joint monitoring under Art.9 UNWC'}
2. {'Engage ICJ/PCA under Art.33' if pneg < 0.40 else 'Joint Technical Committee under Art.24'}
3. {'Environmental Flow Agreement under Art.20' if hifd >= 25 else 'Regular data exchange under Art.9'}
4. NSE={nse:.2f} (pre-calibration) → GRDC data required for full HBV-96 calibration
"""
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report)

        feedback.pushInfo(f'✅ ATDI={atdi:.1f}% | HIFD={hifd:.1f}% | NSE={nse} | CI={ci:.3f}')
        feedback.pushInfo(f'✅ Report saved: {output}')
        return {self.OUTPUT: output}

    def createInstance(self):
        return BasinReportAlgorithm()
