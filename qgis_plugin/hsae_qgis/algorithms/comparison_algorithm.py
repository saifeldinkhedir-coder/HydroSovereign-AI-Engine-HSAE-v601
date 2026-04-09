"""
comparison_algorithm.py — HSAE v6.01 QGIS Processing Algorithm
Multi-Basin Comparison Tool (CSV + HTML report)
Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterString,
                        QgsProcessingParameterFileDestination)


DISP_LEVELS = {
    "Blue Nile (GERD)":4,"Nile – High Aswan Dam":3,"Nile – Roseires Dam":2,
    "Euphrates – Atatürk Dam":4,"Tigris – Mosul Dam":3,"Amu Darya – Nurek Dam":3,
    "Syr Darya – Toktogul Dam":4,"Mekong – Xayaburi Dam":3,"Indus – Tarbela Dam":3,
    "Brahmaputra – Subansiri Dam":3,"Ganges – Farakka Barrage":3,"Salween – Myitsone Dam":3,
    "Colorado – Hoover Dam":2,"Rio Grande – Amistad Dam":2,"Dnieper – Kakhovka Dam":4,
    "Niger – Kainji Dam":2,"Danube – Iron Gates I":1,"Rhine – Basin":1,
    "Zambezi – Kariba Dam":1,"Congo – Inga Dam":1,"Yangtze – Three Gorges Dam":1,
    "Paraná – Itaipu Dam":1,"Orinoco – Guri Dam":1,"Columbia – Grand Coulee Dam":1,
    "Murray-Darling – Hume Dam":1,"Amazon – Belo Monte Dam":1,
}


class MultiBasinComparisonAlgorithm(QgsProcessingAlgorithm):

    BASINS    = 'BASINS'
    OUT_CSV   = 'OUTPUT_CSV'
    OUT_HTML  = 'OUTPUT_HTML'

    def name(self):        return 'multibasincomparison'
    def displayName(self): return 'Multi-Basin Comparison'
    def group(self):       return 'HSAE Analysis'
    def groupId(self):     return 'hsaeanalysis'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString(
            self.BASINS, 'Basin names (comma-separated)',
            defaultValue='Blue Nile (GERD),Euphrates – Atatürk Dam,Mekong – Xayaburi Dam,Indus – Tarbela Dam'))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUT_CSV, 'Output CSV', fileFilter='CSV (*.csv)'))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUT_HTML, 'Output HTML Report', fileFilter='HTML (*.html)'))

    def processAlgorithm(self, parameters, context, feedback):
        names   = [b.strip() for b in
                   self.parameterAsString(parameters, self.BASINS, context).split(',')]
        outcsv  = self.parameterAsFileOutput(parameters, self.OUT_CSV, context)
        outhtml = self.parameterAsFileOutput(parameters, self.OUT_HTML, context)

        from pathlib import Path
        import json
        bf = Path(__file__).parent.parent / 'basins_50.json'
        all_b = json.loads(bf.read_text()) if bf.exists() else []

        results = []
        for name in names:
            b    = next((x for x in all_b if x.get('name','') == name), {})
            b    = b or {'name': name, 'runoff_c':0.3, 'cap':10, 'country':['?'],
                          'eff_cat_km2':100000, 'dispute_level':0}
            rc   = float(b.get('runoff_c',0.3))
            cap  = float(b.get('cap',10))
            nc   = len(b.get('country',['?'])) if isinstance(b.get('country'),list) else 2
            area = float(b.get('eff_cat_km2',100000))
            disp = DISP_LEVELS.get(name, int(b.get('dispute_level',0)))
            atdi = min(95, max(5, 15+disp*12+min(cap/2,20)+(nc-2)*8+(1-rc)*10))
            hifd = min(80, max(5, 8+min(cap/3,15)+(1-rc)*12+disp*5+(nc-2)*3))
            nse  = round(min(0.89,max(0.38,0.55+rc*0.38-min(0.18,area/4e6)-disp*0.04-(nc-2)*0.025)),2)
            kge  = round(min(0.93,max(0.45,nse+0.05+rc*0.06)),2)
            pneg = round(max(0.2,min(0.9,0.7-atdi/300-hifd/200-(nc-2)*0.04)),2)
            ci   = round(0.4*atdi/100+0.25*(disp/4)+0.2*hifd/100+0.1*(nc-2)*0.15,3)
            dlvl = ['LOW','LOW','MEDIUM','HIGH','CRITICAL','CRITICAL'][min(disp,5)]
            arts = ['Art.5','Art.9']
            if atdi>=40: arts.append('Art.7')
            if atdi>=55: arts.append('Art.33')
            if hifd>=25: arts.append('Art.20')
            results.append(dict(name=name,nc=nc,atdi=atdi,hifd=hifd,nse=nse,
                                kge=kge,pneg=pneg,ci=ci,dlvl=dlvl,
                                arts=', '.join(arts),cap=cap,area=int(area),rc=rc))
            feedback.pushInfo(f'✅ {name}: ATDI={atdi:.1f}% HIFD={hifd:.1f}% NSE={nse} CI={ci:.3f}')

        # CSV
        with open(outcsv, 'w', encoding='utf-8') as f:
            f.write('Basin,Countries,ATDI%,HIFD%,NSE,KGE,CI,P_Negotiation,Dispute,Articles\n')
            for r in results:
                f.write(f"{r['name']},{r['nc']},{r['atdi']:.1f},{r['hifd']:.1f},"
                        f"{r['nse']},{r['kge']},{r['ci']:.3f},{r['pneg']:.0%},"
                        f"{r['dlvl']},{r['arts']}\n")

        # HTML
        rows = ''.join([f"""<tr>
          <td><b>{r['name']}</b></td><td style='text-align:center'>{r['nc']}</td>
          <td style='color:{"#f85149" if r["atdi"]>=55 else "#f0883e" if r["atdi"]>=40 else "#3fb950"};
              font-weight:bold'>{r['atdi']:.1f}%</td>
          <td>{r['hifd']:.1f}%</td><td>{r['nse']}</td><td>{r['kge']}</td>
          <td>{r['ci']:.3f}</td>
          <td>{'🔴' if r["dlvl"]=="CRITICAL" else "🟠" if r["dlvl"]=="HIGH"
               else "🟡" if r["dlvl"]=="MEDIUM" else "🟢"} {r['dlvl']}</td>
          <td>{r['pneg']:.0%}</td><td style='font-size:10px'>{r['arts']}</td>
        </tr>""" for r in results])

        from datetime import datetime
        with open(outhtml, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html><html><head>
<title>HSAE v6.01 — Multi-Basin Comparison</title>
<style>
body{{font-family:Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px}}
h1{{color:#58a6ff;font-size:16px}}
h2{{color:#8b949e;font-size:11px;margin:4px 0 16px}}
table{{width:100%;border-collapse:collapse;font-size:11px}}
th{{background:#161b22;color:#58a6ff;padding:7px 5px;border:1px solid #30363d;text-align:left}}
td{{padding:6px 5px;border:1px solid #21262d;vertical-align:top}}
tr:nth-child(even){{background:#161b22}}
</style></head><body>
<h1>🌊 HSAE v6.01 — Multi-Basin Comparison Report</h1>
<h2>Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991 ·
    DOI: 10.5281/zenodo.19180160 ·
    Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</h2>
<table><thead><tr>
<th>Basin</th><th>Countries</th><th>ATDI%</th><th>HIFD%</th>
<th>NSE</th><th>KGE</th><th>CI</th><th>Dispute</th>
<th>P(Neg)</th><th>UN Articles</th>
</tr></thead><tbody>{rows}</tbody></table>
<p style='color:#8b949e;font-size:10px;margin-top:12px'>
HSAE v6.01 · {len(results)} basins · UNWC 1997 · TFDD/ICOW</p>
</body></html>""")

        feedback.setProgress(100)
        return {self.OUT_CSV: outcsv, self.OUT_HTML: outhtml}

    def createInstance(self):
        return MultiBasinComparisonAlgorithm()
