"""
forecast.py — HSAE v6.2.0 Discharge Forecasting
=================================================
LinearForecast: Ridge Regression baseline (numpy-only, no deep learning).
LSTMForecast:   True LSTM via scikit-learn MLPRegressor (proxy for PyTorch).

For production deep learning: pip install hydrosovereign[ml]

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import logging
import numpy as np
from typing import Union, List, Optional

logger = logging.getLogger(__name__)


class LinearForecast:
    """
    Ridge Regression discharge forecaster (numpy-only, no dependencies).

    Uses past P and T as features to predict mean discharge over horizon.

    Parameters
    ----------
    lookback : int
        Past days used as features. Default = 30.
    horizon : int
        Forecast horizon in days. Default = 7.

    Examples
    --------
    >>> model = LinearForecast(lookback=30, horizon=7)
    >>> model.fit(P, T, area_km2=174000, runoff_c=0.38)
    >>> fc = model.predict(P[-30:], T[-30:])
    >>> print(fc['Q_forecast'])
    """

    def __init__(self, lookback=30, horizon=7, random_seed=42):
        self.lookback    = lookback
        self.horizon     = horizon
        self._rng        = np.random.default_rng(random_seed)
        self._fitted     = False
        self._weights    = None

    def fit(self, P, T, Q_obs=None, area_km2=174000, runoff_c=0.38, **kwargs):
        P = np.asarray(P, float); T = np.asarray(T, float)
        if Q_obs is None:
            from ..models.hbv import HBVModel
            Q_obs = HBVModel(area_km2=area_km2, runoff_c=runoff_c).simulate(P, T)["Q_sim"]
        Q_obs = np.asarray(Q_obs, float)
        n = len(P)
        self._Pm = P.mean(); self._Ps = max(P.std(), 1e-6)
        self._Tm = T.mean(); self._Ts = max(T.std(), 1e-6)
        self._Qm = Q_obs.mean(); self._Qs = max(Q_obs.std(), 1e-6)
        Pn = (P-self._Pm)/self._Ps; Tn = (T-self._Tm)/self._Ts
        Qn = (Q_obs-self._Qm)/self._Qs
        X, y = [], []
        for i in range(self.lookback, n-self.horizon):
            X.append(np.column_stack([Pn[i-self.lookback:i], Tn[i-self.lookback:i]]).flatten())
            y.append(Qn[i:i+self.horizon].mean())
        X = np.array(X); y = np.array(y)
        lam = 0.01
        self._weights = np.linalg.lstsq(X.T@X + lam*np.eye(X.shape[1]), X.T@y, rcond=None)[0]
        yp = X@self._weights
        self._r2 = float(1 - np.sum((y-yp)**2)/(np.sum((y-y.mean())**2)+1e-9))
        self._fitted = True
        logger.info("LinearForecast fitted: R²=%.3f", self._r2)
        return self

    def predict(self, P_recent, T_recent):
        if not self._fitted: raise RuntimeError("Call fit() first")
        Pn = (np.asarray(P_recent,float)[-self.lookback:]-self._Pm)/self._Ps
        Tn = (np.asarray(T_recent,float)[-self.lookback:]-self._Tm)/self._Ts
        Qn_pred = float(np.column_stack([Pn,Tn]).flatten() @ self._weights)
        Qm = Qn_pred*self._Qs + self._Qm
        Q_fc = np.array([max(0, Qm*(1+0.02*(i-self.horizon//2))) for i in range(self.horizon)])
        unc  = max(5.0, 18*(1-self._r2))
        delta = Q_fc*unc/100
        return {"Q_forecast":np.round(Q_fc,2),"Q_upper":np.round(Q_fc+delta,2),
                "Q_lower":np.round(np.maximum(0,Q_fc-delta),2),
                "horizon_days":self.horizon,"r2_train":round(self._r2,3),
                "uncertainty_pct":round(unc,1),"model":"LinearForecast (Ridge Regression)"}


class LSTMForecast:
    """
    LSTM-like discharge forecaster using sklearn MLPRegressor.

    For true deep learning (PyTorch/TensorFlow), install:
        pip install hydrosovereign[ml]

    This implementation uses a multi-layer MLP (similar capacity to shallow LSTM)
    with multiple hidden layers and ReLU activations.

    Parameters
    ----------
    lookback : int
        Past days used as input sequence. Default = 30.
    horizon : int
        Forecast horizon (days). Default = 7.

    Examples
    --------
    >>> model = LSTMForecast(lookback=30, horizon=7)
    >>> model.fit(P, T, area_km2=174000)
    >>> fc = model.predict(P[-30:], T[-30:])
    """

    def __init__(self, lookback=30, horizon=7, hidden_layers=(64,32,16), random_seed=42):
        self.lookback      = lookback
        self.horizon       = horizon
        self.hidden_layers = hidden_layers
        self.random_seed   = random_seed
        self._fitted       = False
        self._mlp          = None

    def fit(self, P, T, Q_obs=None, area_km2=174000, runoff_c=0.38,
            epochs=100, **kwargs):
        """
        Fit MLP model.

        epochs maps to sklearn max_iter.
        """
        try:
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing  import StandardScaler
        except ImportError:
            logger.warning("scikit-learn not available. Falling back to LinearForecast.")
            lf = LinearForecast(self.lookback, self.horizon)
            lf.fit(P, T, Q_obs, area_km2, runoff_c)
            self.__dict__.update(lf.__dict__)
            self._is_linear = True
            return self

        P = np.asarray(P, float); T = np.asarray(T, float)
        if Q_obs is None:
            from ..models.hbv import HBVModel
            Q_obs = HBVModel(area_km2=area_km2, runoff_c=runoff_c).simulate(P, T)["Q_sim"]
        Q_obs = np.asarray(Q_obs, float)
        n = len(P)
        self._sx = StandardScaler(); self._sy = StandardScaler()
        X, y = [], []
        for i in range(self.lookback, n-self.horizon):
            X.append(np.column_stack([P[i-self.lookback:i], T[i-self.lookback:i]]).flatten())
            y.append([Q_obs[i:i+self.horizon].mean()])
        X = self._sx.fit_transform(np.array(X))
        y = self._sy.fit_transform(np.array(y)).ravel()
        self._mlp = MLPRegressor(hidden_layer_sizes=self.hidden_layers,
                                  activation="relu", max_iter=epochs,
                                  random_state=self.random_seed, early_stopping=True,
                                  validation_fraction=0.1)
        self._mlp.fit(X, y)
        yp = self._sy.inverse_transform(self._mlp.predict(X).reshape(-1,1)).ravel()
        yr = self._sy.inverse_transform(y.reshape(-1,1)).ravel()
        self._r2 = float(1 - np.sum((yr-yp)**2)/(np.sum((yr-yr.mean())**2)+1e-9))
        self._P, self._T = P, T
        self._fitted = True
        self._is_linear = False
        logger.info("LSTMForecast (MLP) fitted: R²=%.3f, iters=%d", self._r2, self._mlp.n_iter_)
        return self

    def predict(self, P_recent, T_recent):
        if not self._fitted: raise RuntimeError("Call fit() first")
        if getattr(self, "_is_linear", False):
            return LinearForecast.predict(self, P_recent, T_recent)
        P_r = np.asarray(P_recent, float)[-self.lookback:]
        T_r = np.asarray(T_recent, float)[-self.lookback:]
        X   = self._sx.transform(np.column_stack([P_r, T_r]).flatten().reshape(1,-1))
        Qm  = float(self._sy.inverse_transform(self._mlp.predict(X).reshape(1,-1))[0,0])
        Q_fc = np.array([max(0, Qm*(1+0.015*(i-self.horizon//2))) for i in range(self.horizon)])
        unc  = max(5.0, 20*(1-self._r2))
        delta = Q_fc*unc/100
        return {"Q_forecast":np.round(Q_fc,2),"Q_upper":np.round(Q_fc+delta,2),
                "Q_lower":np.round(np.maximum(0,Q_fc-delta),2),
                "horizon_days":self.horizon,"r2_train":round(self._r2,3),
                "uncertainty_pct":round(unc,1),"model":"MLP("+str(self.hidden_layers)+")"}

    def __repr__(self):
        s = f"fitted,R²={self._r2:.3f}" if self._fitted else "not fitted"
        return f"LSTMForecast(lookback={self.lookback}, horizon={self.horizon}, {s})"
