"""
negotiation.py — HSAE v6.3.0 NegotiationAI
============================================
Trained on REAL TFDD/ICOW historical cases.
Sources: Wolf 2003 (TFDD), Hensel 2006 (ICOW).

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import csv, logging
import numpy as np
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"
_CSV_PATH = _DATA_DIR / "tfdd_icow_cases.csv"
_FEATURES = ["atdi","hifd","n_countries","dispute_level",
              "has_treaty","gdp_gap","shared_history","aridity_index"]


class NegotiationAI:
    """
    Negotiation outcome predictor trained on empirical TFDD/ICOW data.

    Training data: 306 cases from Wolf 2003 (TFDD) + Hensel 2006 (ICOW).
    Model: GradientBoostingRegressor (sklearn) + calibrated formula blend.

    Examples
    --------
    >>> ai = NegotiationAI()
    >>> r  = ai.predict(atdi=53.5, hifd=35.7, n_countries=3, dispute_level=4)
    >>> print(r['p_success'])   # ~0.38
    >>> print(ai.training_summary())
    """

    def __init__(self, model_path=None):
        self._model=None; self._scaler=None
        self._is_trained=False; self._n_cases=0; self._cv_r2=None
        if model_path and Path(model_path).exists():
            self.load(model_path)
        else:
            self._train_from_csv()

    def _load_csv(self):
        if not _CSV_PATH.exists():
            raise FileNotFoundError(f"Training CSV not found: {_CSV_PATH}")
        X, y = [], []
        with open(_CSV_PATH, newline='') as f:
            for row in csv.DictReader(f):
                X.append([float(row[k]) for k in _FEATURES])
                y.append(float(row["outcome_cooperative"]))
        return np.array(X), np.array(y)

    def _train_from_csv(self):
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import cross_val_score
        except ImportError:
            logger.warning("scikit-learn not available — using formula only")
            return
        try:
            X, y = self._load_csv()
        except FileNotFoundError as e:
            logger.warning("%s", e)
            return
        self._n_cases = len(X)
        self._scaler  = StandardScaler().fit(X)
        self._model   = GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.06,
            subsample=0.8, min_samples_leaf=4, random_state=42)
        Xs = self._scaler.transform(X)
        self._model.fit(Xs, y)
        self._is_trained = True
        self._cv_r2 = float(cross_val_score(self._model, Xs, y, cv=5, scoring="r2").mean())
        logger.info("NegotiationAI: n=%d TFDD/ICOW cases, CV-R²=%.3f",
                    self._n_cases, self._cv_r2)

    def predict(self, atdi, hifd, n_countries, dispute_level,
                has_treaty=False, gdp_gap=0.0, shared_history=0.5, aridity_index=0.3):
        """Predict negotiation success. Returns dict with p_success, strategy, risk, etc."""
        p_f = float(np.clip(
            0.846 - atdi/190 - hifd/240 - max(0,n_countries-2)*0.045
            + float(has_treaty)*0.05 - gdp_gap*0.03 + shared_history*0.04,
            0.20, 0.90))

        if self._is_trained and self._model is not None:
            try:
                X   = np.array([[atdi,hifd,n_countries,dispute_level,
                                  float(has_treaty),gdp_gap,shared_history,aridity_index]])
                p_g = float(np.clip(self._model.predict(self._scaler.transform(X))[0], 0.05, 0.95))
                # Adaptive blend: weight by CV-R² (low CV-R² = trust formula more)
                gbm_weight = float(max(0.20, min(0.55, 0.20 + (self._cv_r2 or 0)*3)))
                p   = float(np.clip(gbm_weight*p_g + (1-gbm_weight)*p_f, 0.20, 0.90))
                mt  = f"GBM(TFDD/ICOW n={self._n_cases} CV-R²={self._cv_r2:.2f})"
            except Exception as e:
                logger.warning("GBM failed (%s)", e)
                p, mt = p_f, "calibrated_formula"
        else:
            p, mt = p_f, "calibrated_formula"

        if   p>=0.65: s,u,r="Cooperative Framework","Art.8+Art.24 JMO","LOW"
        elif p>=0.45: s,u,r="Mediation","Art.17 Mediation","MEDIUM"
        elif p>=0.28: s,u,r="PCA Arbitration","Art.33 → PCA","HIGH"
        else:         s,u,r="ICJ Referral","Art.33+ICJ Art.36","CRITICAL"

        recs={"LOW":"Establish JMO (Art.24). High probability of cooperative agreement.",
              "MEDIUM":"Third-party mediation (Art.17). Joint technical committee.",
              "HIGH":"Art.33 formal dispute. Prepare PCA with HIFD/ATDI evidence.",
              "CRITICAL":"File ICJ Art.36. Invoke Art.35 emergency clause."}

        return {"p_success":round(p,3),"strategy":s,"un_path":u,"risk":r,
                "recommendation":recs[r],"confidence":round(min(1,.4+abs(p-.45)*1.5),2),
                "model_type":mt,"n_training_cases":self._n_cases,"cv_r2":self._cv_r2}

    def batch_predict(self, basins):
        results=[]
        for b in basins:
            r=self.predict(b.get("atdi",30),b.get("hifd",15),b.get("n_countries",2),
                           b.get("dispute_level",0),b.get("has_treaty",False),
                           b.get("gdp_gap",0.),b.get("shared_history",.5))
            r["name"]=b.get("name",""); results.append(r)
        return results

    def save(self, path):
        import joblib
        joblib.dump({"model":self._model,"scaler":self._scaler,
                     "n_cases":self._n_cases,"cv_r2":self._cv_r2}, path)

    def load(self, path):
        import joblib
        d=joblib.load(path)
        self._model=d["model"]; self._scaler=d.get("scaler")
        self._n_cases=d.get("n_cases",0); self._cv_r2=d.get("cv_r2")
        self._is_trained=True

    def feature_importance(self):
        if not self._is_trained or not self._model: return None
        return dict(sorted(zip(_FEATURES,self._model.feature_importances_.tolist()),key=lambda x:-x[1]))

    def training_summary(self):
        try:
            X,y=self._load_csv()
            nc=int(y.sum())
            return (f"Training: {len(X)} cases | TFDD/ICOW empirical data\n"
                    f"  Cooperative: {nc} ({nc/len(X):.1%}) | Escalated: {len(X)-nc} ({(len(X)-nc)/len(X):.1%})\n"
                    f"  CV R²: {self._cv_r2:.3f}" if self._cv_r2 else "")
        except: return "CSV not found"

    def __repr__(self):
        src = f"TFDD/ICOW n={self._n_cases} CV-R²={self._cv_r2:.3f}" if self._is_trained else "formula"
        return f"NegotiationAI(model=GBM({src}))"
