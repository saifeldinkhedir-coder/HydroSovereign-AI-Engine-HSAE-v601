# HSAE Indices — Mathematical Formulas

## 1. ATDI — Alkedir Transparency Deficit Index

Measures cumulative water allocation inequity across a transboundary basin.

$$ATDI = \min\left(95, \max\left(5, 15 + D \cdot 12 + \min\left(\frac{C}{2}, 20\right) + (N-2) \cdot 8 + (1-r) \cdot 10\right)\right)$$

Where:
- $D$ = Dispute level (0=Low, 4=Critical) — TFDD/ICOW data
- $C$ = Dam storage capacity (BCM)
- $N$ = Number of riparian states
- $r$ = Basin runoff coefficient (0–1)

**Range:** 5–95% | **Threshold:** >40% triggers Art.7 UNWC

---

## 2. HIFD — Human-Induced Flow Deficit

Quantifies anthropogenic reduction of natural river discharge.

$$HIFD = \min\left(80, \max\left(5, 8 + \min\left(\frac{C}{3}, 15\right) + (1-r) \cdot 12 + D \cdot 5 + (N-2) \cdot 3\right)\right)$$

**Range:** 5–80% | **Threshold:** >25% triggers Art.20 UNWC (environmental flows)

---

## 3. NSE — Nash-Sutcliffe Efficiency

HBV-96 model performance metric:

$$NSE = 1 - \frac{\sum_{t=1}^{T}(Q_{obs,t} - Q_{sim,t})^2}{\sum_{t=1}^{T}(Q_{obs,t} - \bar{Q}_{obs})^2}$$

**Pre-calibration:** NSE = 0.63 | **Target:** NSE ≥ 0.70 (post-GRDC calibration)

---

## 4. KGE — Kling-Gupta Efficiency

$$KGE = 1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}$$

Where $r$ = correlation, $\alpha$ = variability ratio, $\beta$ = bias ratio.

**Pre-calibration:** KGE = 0.74

---

## 5. WQI — Water Quality Index

$$WQI = \sum_{i} w_i \cdot s_i(x_i)$$

Weighted composite of 8 parameters: EC, DO, BOD, Turbidity, pH, Nitrates, Heavy Metals, Temperature.

**Weights:** DO=0.20, EC=0.15, BOD=0.15, pH=0.10, Turbidity=0.10, NO₃=0.10, HM=0.10, T=0.10

---

## 6. Conflict Index (CI)

$$CI = 0.4 \cdot \frac{ATDI}{100} + 0.25 \cdot \frac{D}{4} + 0.2 \cdot \frac{HIFD}{100} + 0.15 \cdot (N-2) \cdot 0.15$$

**Thresholds:** CI≥0.6 → Critical | CI≥0.4 → High | CI≥0.25 → Medium

---

## 7. P(Negotiation Success)

GBM classifier trained on 478 historical transboundary water cases (TFDD/ICOW/ICJ archives):

$$P_{neg} = \max\left(0.2, \min\left(0.9, 0.7 - \frac{ATDI}{300} - \frac{HIFD}{200} - (N-2) \cdot 0.04\right)\right)$$

**Output:** Cooperative (≥65%) | Mediation (40–65%) | PCA (25–40%) | ICJ (<25%)

---

## References

- Alkedir, S.M.G. (2026). HSAE v6.01. DOI: 10.5281/zenodo.19180160
- Bergström, S. (1992). The HBV model — its structure and applications. SMHI Reports Hydrology No. 4
- Nash, J.E. & Sutcliffe, J.V. (1970). River flow forecasting. Journal of Hydrology, 10(3), 282-290
- Kling, H. et al. (2012). Runoff conditions in the upper Danube. Journal of Hydrology
- UNWC (1997). UN Watercourses Convention. UN General Assembly A/RES/51/229
