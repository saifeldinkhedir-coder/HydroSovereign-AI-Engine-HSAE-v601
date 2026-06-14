# UNWC 1997 Articles Automated by HSAE

**HydroSovereign AI Engine (HSAE)** — automated article-by-article compliance triggering under the United Nations Convention on the Law of the Non-Navigational Uses of International Watercourses (New York, 21 May 1997).

Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991 · University of Khartoum
Package: `hydrosovereign` v6.7.1 (PyPI) · QGIS Plugin ID 5040, v6.0.12

---

## How automated triggering works

HSAE computes six original indices (the Alkhedir Water Sovereignty Indices, AWSI) from satellite-derived hydrology, then maps two of them — the Alkhedir Transparency Deficit Index (ATDI) and the Alkhedir Human-Induced Flow Deficit (AHIFD) — onto threshold tests that correspond to specific UNWC 1997 obligations. Each test is deterministic: a basin's index value either crosses the legal threshold or it does not, and the engine returns the resulting list of triggered articles together with a recommended diplomatic pathway.

Two articles are treated as baseline obligations that apply to every shared watercourse regardless of index values, and four further articles are conditional, activating only when the relevant index crosses its threshold. This mirrors the structure of the Convention itself, where some duties are continuous and others arise from the severity of a given situation.

This trigger logic is implemented once and shared across every HSAE surface: the `legal.py` module is the single source of truth, and the Python package (`indices.triggered_articles`), the QGIS plugin, and all Processing Algorithms delegate to the same thresholds and labels. The Article 33 threshold is aligned with the CRITICAL risk tier (ATDI ≥ 60%) so that the dispute-settlement article and the highest risk classification activate together, with no gap between them.

---

## Baseline articles (apply to all 26 basins)

These two obligations are returned for every transboundary basin HSAE assesses, because the Convention frames them as continuous duties rather than situation-dependent ones.

### Article 5 — Equitable and Reasonable Utilisation and Participation
Article 5 requires watercourse states to use an international watercourse in an equitable and reasonable manner and to participate in its use, development, and protection on that basis. In HSAE this is the foundational compliance lens: every basin is evaluated against the equitable-use principle, and the engine labels it `Art.5 ERU`. Because equitable utilisation is a standing obligation that does not depend on a harm threshold being crossed, it is always present in the output. The Alkhedir Sovereignty Index (ASI) provides the quantitative reading most closely associated with this article.

### Article 9 — Regular Exchange of Data and Information
Article 9 obliges watercourse states to exchange, on a regular basis, readily available data and information on the condition of the watercourse, particularly of a hydrological, meteorological, hydrogeological, and ecological nature. HSAE treats this as the second baseline duty, labelled `Art.9 Data Sharing`, and it is likewise returned for all basins. The Alkhedir Forensic Signal Factor (AFSF) is the index that speaks to the transparency and data-availability dimension that Article 9 governs.

---

## Conditional articles (triggered by index thresholds)

The following four articles activate only when a basin's indices cross documented thresholds. The thresholds are fixed in the engine's legal layer (`legal.py`) and are identical across the Python package, the QGIS plugin, and all Processing Algorithms — a single source of truth.

### Article 7 — Obligation Not to Cause Significant Harm
Article 7 requires states to take all appropriate measures to prevent the causing of significant harm to other watercourse states. HSAE triggers this article, labelled `Art.7 NSH`, when **ATDI ≥ 40%**. The transparency deficit reaching this level indicates that upstream behaviour is opaque enough, and downstream exposure high enough, that the no-significant-harm obligation becomes the operative legal question. Among the current 26 basins, four cross this threshold: Blue Nile (GERD) at 43.6%, Euphrates–Atatürk at 41.8%, Nile–High Aswan at 40.8%, and Syr Darya–Toktogul at 40.6%.

### Article 20 — Protection and Preservation of Ecosystems
Article 20 obliges states, individually and jointly, to protect and preserve the ecosystems of international watercourses. HSAE maps this to environmental-flow adequacy and triggers it, labelled `Art.20 Env.Flow`, when **AHIFD ≥ 25%** — that is, when the human-induced flow deficit is large enough that downstream ecosystems are presumptively at risk. Under current basin data no basin reaches this AHIFD level (the highest, GERD, sits at 19.7%), so the article is implemented and ready but not presently triggered; it would activate automatically if flow withholding increased.

### Article 33 — Settlement of Disputes
Article 33 sets out the dispute-settlement framework, including negotiation, good offices, mediation, conciliation, and, failing those, recourse to arbitration or the International Court of Justice. HSAE triggers this article, labelled `Art.33 Dispute`, when **ATDI ≥ 60%**, reflecting a transparency deficit severe enough (the CRITICAL legal tier) that bilateral technical cooperation is unlikely to resolve the situation on its own. No basin currently reaches this level, so while the trigger is active in the logic, it is not raised by present data.

### Article 35 — Emergency Situations
Article 35 addresses emergency situations that cause, or pose an imminent threat of causing, serious harm, and requires affected states to be notified without delay. HSAE reserves this as its most severe trigger, labelled `Art.35 Emergency`, activating when **ATDI ≥ 70%**. It is intended for acute crises rather than chronic tension, and no basin in the current dataset approaches it.

---

## Recommended pathways

Beyond listing triggered articles, HSAE returns a recommended diplomatic pathway that escalates with the transparency deficit. The mapping is deterministic:

When ATDI is below 40%, the engine recommends regular data exchange under Article 9, treating the situation as one of routine cooperative management. When ATDI reaches 40% but stays below 60% — the band that currently contains all four flagged basins — it recommends establishing a Joint Technical Committee, pairing Article 8 (general obligation to cooperate) with Article 24 (joint management mechanisms), and pairing information exchange with structured technical cooperation. When ATDI reaches 60% (the CRITICAL tier) but stays below 70%, it escalates to formal dispute resolution under Article 33, naming PCA arbitration or the ICJ as the pathway. At or above 70%, it calls for emergency notification under Article 35 together with ICJ emergency relief.

This means that although Articles 8 and 24 are not part of the index-trigger list, they appear in the recommended pathway as the cooperative instruments the Convention offers once the no-significant-harm threshold is crossed.

---

---

## Indicator → Article mapping

HSAE computes six indices (the AWSI family), but only two of them act as direct *triggers* that decide whether an article appears; the other four play supporting, interpretive, or composite roles. The table below makes this explicit.

| UNWC 1997 Article | Trigger indicator | Threshold | Supporting indicator | Role |
|---|---|---|---|---|
| Art. 5 — Equitable & Reasonable Utilisation | — (baseline, always) | every basin | **ASI** (Alkhedir Sovereignty Index) | ASI quantifies the equity dimension |
| Art. 9 — Regular Data Exchange | — (baseline, always) | every basin | **AFSF** (Alkhedir Forensic Signal Factor) | AFSF quantifies transparency / data availability |
| Art. 7 — No Significant Harm | **ATDI** | ≥ 40% | — | direct trigger |
| Art. 20 — Protection of Ecosystems | **AHIFD** | ≥ 25% | — | direct trigger |
| Art. 33 — Settlement of Disputes | **ATDI** | ≥ 60% (= CRITICAL tier) | — | direct trigger |
| Art. 35 — Emergency Situations | **ATDI** | ≥ 70% | — | direct trigger |

### How the six indices relate to the articles

Two indices do the triggering. **ATDI** (Alkhedir Transparency Deficit Index) drives three articles through three rising thresholds — Article 7 at 40%, Article 33 at 60%, and Article 35 at 70% — so a single transparency measure escalates the legal response as it grows. **AHIFD** (Alkhedir Human-Induced Flow Deficit) drives one article, Article 20, at 25%, tying ecosystem protection to the size of the human-induced flow deficit.

The two baseline articles each have a dedicated index that does not gate their appearance but quantifies the obligation they express. **ASI** (Alkhedir Sovereignty Index) reads the equitable-utilisation dimension of Article 5, and **AFSF** (Alkhedir Forensic Signal Factor) reads the transparency and data-availability dimension of Article 9. Because Articles 5 and 9 are continuous duties, both are returned for every basin regardless of these values; the indices give the quantitative texture rather than the on/off decision.

The remaining two indices are not tied to a specific trigger. **AHLB** (Alkhedir HBV-Legal Bridge) is the interpretive link that connects the HBV-96 hydrological model output to the legal layer, expressing how modelled flow conditions translate into legal exposure across Articles 5, 6, and 7. **ATCI** (Alkhedir Treaty Compliance Index) is a composite score on a 0–100 scale that summarises overall compliance across the full set of relevant articles, providing a single headline figure rather than a per-article trigger.

### Worked reading — Blue Nile (GERD)

For GERD the engine returns ATDI = 43.6%, AHIFD = 19.7%, AFSF = 0.36, AHLB = 0.436, ASI = 0.64, ATCI = 70.3. Reading these through the mapping: the two baseline articles (5 and 9) are present; ATDI at 43.6% crosses the 40% Article 7 threshold but stays below the 60% Article 33 and 70% Article 35 thresholds; and AHIFD at 19.7% stays below the 25% Article 20 threshold. The triggered set is therefore Art.5 ERU, Art.9 Data Sharing, and Art.7 NSH, with ASI and AFSF colouring the two baseline duties and ATCI = 70.3 giving the composite headline.

---

## Threshold summary

| Article | HSAE label | Index | Threshold | Status across 26 basins |
|---|---|---|---|---|
| Art. 5 — Equitable & Reasonable Utilisation | `Art.5 ERU` | ASI | always (baseline) | 26 / 26 |
| Art. 9 — Regular Data Exchange | `Art.9 Data Sharing` | AFSF | always (baseline) | 26 / 26 |
| Art. 7 — No Significant Harm | `Art.7 NSH` | ATDI | ≥ 40% | 4 / 26 |
| Art. 20 — Protection of Ecosystems | `Art.20 Env.Flow` | AHIFD | ≥ 25% | 0 / 26 (ready) |
| Art. 33 — Settlement of Disputes | `Art.33 Dispute` | ATDI | ≥ 60% | 0 / 26 (ready) |
| Art. 35 — Emergency Situations | `Art.35 Emergency` | ATDI | ≥ 70% | 0 / 26 (ready) |

Articles 8 (general obligation to cooperate) and 24 (management) are not threshold-triggered but are returned within the recommended pathway once Article 7 activates.

---

## Worked example — Blue Nile (GERD)

For the Grand Ethiopian Renaissance Dam basin (runoff coefficient 0.38, dam capacity 74.0 BCM, three riparian states, dispute level 4), HSAE computes ATDI = 43.6% and AHIFD = 19.7%. Applying the thresholds above, the baseline Articles 5 and 9 are present, and because ATDI exceeds 40% while AHIFD stays below 25% and ATDI stays below 55%, Article 7 is triggered while Articles 20, 33, and 35 are not. The engine therefore returns the article set `Art.5 ERU`, `Art.9 Data Sharing`, and `Art.7 NSH`, and recommends a Joint Technical Committee under Article 24 paired with information exchange under Article 8 — the appropriate response for a basin where the no-significant-harm obligation is engaged but the situation has not escalated to formal dispute settlement.

```python
from hydrosovereign import indices, legal
from hydrosovereign.basins import BASINS_26

gerd = next(b for b in BASINS_26 if "GERD" in b["name"])
f = indices.compute_all_indices(
    gerd["runoff_c"], gerd["cap"], len(gerd["country"]), gerd["dispute_level"]
)
articles = legal.get_triggered_articles(f["atdi"], f["ahifd"])
assessment = legal.get_legal_assessment(
    f["atdi"], f["ahifd"], gerd["dispute_level"], len(gerd["country"])
)
# articles  -> ['Art.5 ERU', 'Art.9 Data Sharing', 'Art.7 NSH']
# pathway   -> 'Art.8 Information Exchange + Art.24 JMO'
```

---

## Notes and caveats

HSAE's article triggering is a screening and decision-support instrument, not a substitute for legal counsel or a formal adjudication. The thresholds encode a defensible quantitative reading of when each obligation becomes the operative question, but the Convention's application to any real dispute depends on facts, treaties, and customary law that lie beyond what indices can capture. The status column above reflects the current 26-basin dataset; because triggering is deterministic, any update to basin parameters (for example, increased flow withholding raising AHIFD past 25%) will automatically activate the corresponding article on the next run.

UNWC 1997 entered into force on 17 August 2014. HSAE references the Convention text as the legal framework for its triggers; users should confirm the ratification status of specific riparian states, since the Convention binds parties to it and informs customary practice more broadly.
