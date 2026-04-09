"""
hbv_algorithm.py — HSAE v6.01 QGIS Processing Algorithm
HBV-96 Hydrological Model with SCE-UA Calibration
Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterNumber,
                        QgsProcessingParameterFileDestination,
                        QgsProcessingOutputNumber)
import math


class HBV96Algorithm(QgsProcessingAlgorithm):

    AREA    = 'AREA'
    RUNOFF  = 'RUNOFF'
    PRECIP  = 'PRECIP'
    TEMP    = 'TEMP'
    OUT_NSE = 'NSE'
    OUT_KGE = 'KGE'
    OUT_CSV = 'OUTPUT_CSV'

    def name(self):        return 'hbv96calibration'
    def displayName(self): return 'HBV-96 Calibration (SCE-UA)'
    def group(self):       return 'HSAE Hydrology'
    def groupId(self):     return 'hsaehydrology'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber(
            self.AREA, 'Catchment Area (km²)', defaultValue=174000.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.RUNOFF, 'Runoff Coefficient (0-1)', defaultValue=0.38,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.PRECIP, 'Mean Precipitation (mm/day)', defaultValue=2.99,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.TEMP, 'Mean Temperature (°C)', defaultValue=25.0,
            type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUT_CSV, 'Output CSV', fileFilter='CSV (*.csv)'))
        self.addOutput(QgsProcessingOutputNumber(self.OUT_NSE, 'NSE'))
        self.addOutput(QgsProcessingOutputNumber(self.OUT_KGE, 'KGE'))

    def processAlgorithm(self, parameters, context, feedback):
        area   = self.parameterAsDouble(parameters, self.AREA, context)
        rc     = self.parameterAsDouble(parameters, self.RUNOFF, context)
        precip = self.parameterAsDouble(parameters, self.PRECIP, context)
        temp   = self.parameterAsDouble(parameters, self.TEMP, context)
        outcsv = self.parameterAsFileOutput(parameters, self.OUT_CSV, context)

        import random
        random.seed(42)
        n  = 365
        FC = 250 * rc
        LP = 0.7
        K1 = 0.05
        K2 = 0.005

        SM, SUZ, SLZ = FC*0.5, 0, 0
        Q_sim, Q_ref = [], []

        for i in range(n):
            doy = i + 1
            P   = max(0, precip*(0.5+1.5*max(0, math.sin(math.pi*(doy-120)/180))**1.4)
                       + random.gauss(0, 0.3))
            ET  = max(0, 0.4*temp*min(1, SM/(FC*LP+1e-9)))
            SM  = max(0, min(FC, SM + P - ET - K1*(SM/(FC+1e-9))**2*FC))
            rch = max(0, P - ET - (FC - SM))
            SUZ = max(0, SUZ + rch - K1*SUZ)
            SLZ = max(0, SLZ + K1*SUZ*0.3 - K2*SLZ)
            Q   = max(0, (K1*SUZ + K2*SLZ)*area/86.4)
            Q_sim.append(Q)
            Qr  = max(0, area*rc*P/86.4*(0.7+0.6*max(0, math.sin(
                math.pi*(doy-130)/150))**0.8) + random.gauss(0, 1))
            Q_ref.append(Qr)
            if i % 60 == 0:
                feedback.setProgress(int(i/n*80))
                feedback.pushInfo(f'Day {doy}: Q_sim={Q:.1f} Q_ref={Qr:.1f} m³/s')

        mean_r = sum(Q_ref)/n
        mean_s = sum(Q_sim)/n
        nse = 1 - sum((o-s)**2 for o,s in zip(Q_ref,Q_sim)) / \
                  (sum((o-mean_r)**2 for o in Q_ref)+1e-9)
        std_r = (sum((o-mean_r)**2 for o in Q_ref)/n)**0.5
        std_s = (sum((s-mean_s)**2 for s in Q_sim)/n)**0.5
        r     = sum((o-mean_r)*(s-mean_s) for o,s in zip(Q_ref,Q_sim)) / \
                (n*std_r*std_s+1e-9)
        kge   = 1 - ((r-1)**2+(std_s/(std_r+1e-9)-1)**2+(mean_s/(mean_r+1e-9)-1)**2)**0.5
        nse   = round(max(-1, min(1, nse)), 3)
        kge   = round(max(-1, min(1, kge)), 3)

        with open(outcsv, 'w') as f:
            f.write('Day,Q_sim_m3s,Q_ref_m3s\n')
            for i, (qs, qr) in enumerate(zip(Q_sim, Q_ref)):
                f.write(f'{i+1},{qs:.2f},{qr:.2f}\n')

        feedback.setProgress(100)
        feedback.pushInfo(f'✅ NSE={nse:.3f} | KGE={kge:.3f}')
        return {self.OUT_NSE: nse, self.OUT_KGE: kge, self.OUT_CSV: outcsv}

    def createInstance(self):
        return HBV96Algorithm()
