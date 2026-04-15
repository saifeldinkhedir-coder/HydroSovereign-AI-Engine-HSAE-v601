"""
forecast.py — HSAE v6.3.0 Discharge Forecasting
=================================================
LinearForecast : Ridge Regression baseline (numpy-only, honest)
LSTMForecast   : TRUE PyTorch LSTM with recurrent memory gates
                 3D tensors (batch, seq_len, features) — NOT MLP

For true LSTM: pip install hydrosovereign[ml]  (installs torch)

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import logging
import numpy as np

logger = logging.getLogger(__name__)


class LinearForecast:
    """Ridge Regression discharge forecaster (numpy-only baseline).

    Examples
    --------
    >>> m = LinearForecast(lookback=30, horizon=7)
    >>> m.fit(P, T, area_km2=174000)
    >>> fc = m.predict(P[-30:], T[-30:])
    """

    def __init__(self, lookback=30, horizon=7, lam=0.01):
        self.lookback=lookback; self.horizon=horizon; self.lam=lam; self._fitted=False

    def fit(self, P, T, Q_obs=None, area_km2=174000, runoff_c=0.38, **kwargs):
        P=np.asarray(P,float); T=np.asarray(T,float); n=len(P)
        if Q_obs is None:
            from ..models.hbv import HBVModel
            Q_obs = HBVModel(area_km2=area_km2,runoff_c=runoff_c).simulate(P,T)["Q_sim"]
        Q_obs=np.asarray(Q_obs,float)
        self._Pm,self._Ps=P.mean(),max(P.std(),1e-6)
        self._Tm,self._Ts=T.mean(),max(T.std(),1e-6)
        self._Qm,self._Qs=Q_obs.mean(),max(Q_obs.std(),1e-6)
        Pn=(P-self._Pm)/self._Ps; Tn=(T-self._Tm)/self._Ts; Qn=(Q_obs-self._Qm)/self._Qs
        X,y=[],[]
        for i in range(self.lookback,n-self.horizon):
            X.append(np.column_stack([Pn[i-self.lookback:i],Tn[i-self.lookback:i]]).flatten())
            y.append(Qn[i:i+self.horizon].mean())
        X=np.array(X); y=np.array(y)
        self._w=np.linalg.lstsq(X.T@X+self.lam*np.eye(X.shape[1]),X.T@y,rcond=None)[0]
        yp=X@self._w
        self._r2=float(1-np.sum((y-yp)**2)/(np.sum((y-y.mean())**2)+1e-9))
        self._fitted=True
        logger.info("LinearForecast fitted R²=%.3f",self._r2)
        return self

    def predict(self, P_recent, T_recent):
        if not self._fitted: raise RuntimeError("Call fit() first")
        Pn=(np.asarray(P_recent,float)[-self.lookback:]-self._Pm)/self._Ps
        Tn=(np.asarray(T_recent,float)[-self.lookback:]-self._Tm)/self._Ts
        Qm=float(np.column_stack([Pn,Tn]).flatten()@self._w)*self._Qs+self._Qm
        Q_fc=np.array([max(0,Qm*(1+0.02*(i-self.horizon//2))) for i in range(self.horizon)])
        unc=max(5.,18*(1-self._r2)); delta=Q_fc*unc/100
        return {"Q_forecast":np.round(Q_fc,2),"Q_upper":np.round(Q_fc+delta,2),
                "Q_lower":np.round(np.maximum(0,Q_fc-delta),2),
                "horizon_days":self.horizon,"r2_train":round(self._r2,3),
                "uncertainty_pct":round(unc,1),"model":"LinearForecast(Ridge)"}

    def __repr__(self):
        return f"LinearForecast(lb={self.lookback},R²={self._r2:.3f})" if self._fitted else f"LinearForecast(lb={self.lookback},not fitted)"


class LSTMForecast:
    """
    TRUE PyTorch LSTM discharge forecaster with recurrent memory gates.

    Processes 3D tensors (batch, seq_len, 2_features) through LSTM cells.
    This is a genuine recurrent network — NOT an MLP or Ridge Regression.

    Architecture: Input(2) → LSTM(hidden, layers) → Linear(horizon)

    Parameters
    ----------
    lookback : int
        Sequence length (days). Default = 30.
    horizon : int
        Forecast horizon (days). Default = 7.
    hidden_size : int
        LSTM hidden state size. Default = 64.
    n_layers : int
        Stacked LSTM layers. Default = 2.

    Examples
    --------
    >>> model = LSTMForecast(lookback=30, horizon=7)
    >>> model.fit(P, T, area_km2=174000, epochs=50)
    >>> fc = model.predict(P[-30:], T[-30:])
    >>> print(fc["model"])   # LSTM(hidden=64, layers=2, PyTorch)
    """

    def __init__(self, lookback=30, horizon=7, hidden_size=64, n_layers=2,
                 dropout=0.2, random_seed=42):
        self.lookback=lookback; self.horizon=horizon
        self.hidden_size=hidden_size; self.n_layers=n_layers
        self.dropout=dropout; self.random_seed=random_seed
        self._fitted=False; self._net=None; self._use_torch=False

    def _build_net(self):
        import torch.nn as nn
        import torch
        class _LSTM(nn.Module):
            def __init__(s,inp,hid,lay,hor,drop):
                super().__init__()
                s.lstm=nn.LSTM(inp,hid,lay,batch_first=True,dropout=drop if lay>1 else 0.)
                s.drop=nn.Dropout(drop)
                s.fc=nn.Linear(hid,hor)
            def forward(s,x):
                out,_=s.lstm(x)       # (B,T,H)
                return s.fc(s.drop(out[:,-1,:]))  # (B,horizon)
        torch.manual_seed(self.random_seed)
        return _LSTM(2, self.hidden_size, self.n_layers, self.horizon, self.dropout)

    def fit(self, P, T, Q_obs=None, area_km2=174000, runoff_c=0.38,
            epochs=50, lr=1e-3, batch_size=32, **kwargs):
        P=np.asarray(P,float); T=np.asarray(T,float); n=len(P)
        if Q_obs is None:
            from ..models.hbv import HBVModel
            Q_obs=HBVModel(area_km2=area_km2,runoff_c=runoff_c).simulate(P,T)["Q_sim"]
        Q_obs=np.asarray(Q_obs,float)

        try:
            import torch, torch.nn as nn, torch.optim as optim
            self._use_torch=True
        except ImportError:
            logger.warning("PyTorch not available — falling back to LinearForecast")
            lf=LinearForecast(self.lookback,self.horizon)
            lf.fit(P,T,Q_obs=Q_obs)
            self.__dict__.update({k:v for k,v in lf.__dict__.items()})
            self._fallback=True; self._fitted=True; return self

        self._fallback=False
        self._Pm,self._Ps=P.mean(),max(P.std(),1e-6)
        self._Tm,self._Ts=T.mean(),max(T.std(),1e-6)
        self._Qm,self._Qs=Q_obs.mean(),max(Q_obs.std(),1e-6)
        Pn=(P-self._Pm)/self._Ps; Tn=(T-self._Tm)/self._Ts; Qn=(Q_obs-self._Qm)/self._Qs

        # Build 3D sequences (N, lookback, 2)
        X_seq,y_seq=[],[]
        for i in range(self.lookback,n-self.horizon):
            X_seq.append(np.column_stack([Pn[i-self.lookback:i],Tn[i-self.lookback:i]]))
            y_seq.append(Qn[i:i+self.horizon].mean())
        X_t=torch.FloatTensor(np.array(X_seq))       # (N, lookback, 2)
        y_t=torch.FloatTensor(np.array(y_seq)).unsqueeze(1)  # (N,1)

        self._net=self._build_net()
        opt=optim.Adam(self._net.parameters(),lr=lr)
        sched=optim.lr_scheduler.ReduceLROnPlateau(opt,patience=5,factor=0.5)
        crit=nn.HuberLoss()
        N=len(X_t); best=float("inf")

        for ep in range(epochs):
            self._net.train()
            idx=torch.randperm(N); ep_loss=0.0
            for i in range(0,N,batch_size):
                bX=X_t[idx[i:i+batch_size]]; by=y_t[idx[i:i+batch_size]]
                opt.zero_grad()
                loss=crit(self._net(bX).mean(dim=1,keepdim=True),by)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self._net.parameters(),1.0)
                opt.step(); ep_loss+=loss.item()
            ep_loss/=max(1,N//batch_size)
            sched.step(ep_loss)
            if ep_loss<best: best=ep_loss

        self._net.eval()
        with torch.no_grad():
            yp=self._net(X_t).mean(dim=1).numpy()
        yr=y_t.squeeze().numpy()
        self._r2=float(1-np.sum((yr-yp)**2)/(np.sum((yr-yr.mean())**2)+1e-9))
        self._best_loss=best; self._fitted=True
        logger.info("LSTMForecast(PyTorch) R²=%.3f loss=%.4f hidden=%d layers=%d",
                    self._r2,best,self.hidden_size,self.n_layers)
        return self

    def predict(self, P_recent, T_recent):
        if not self._fitted: raise RuntimeError("Call fit() first")
        if getattr(self,"_fallback",False):
            return LinearForecast.predict(self,P_recent,T_recent)
        import torch
        self._net.eval()
        Pn=(np.asarray(P_recent,float)[-self.lookback:]-self._Pm)/self._Ps
        Tn=(np.asarray(T_recent,float)[-self.lookback:]-self._Tm)/self._Ts
        seq=torch.FloatTensor(np.column_stack([Pn,Tn])[None,:,:])  # (1,lb,2)
        with torch.no_grad():
            pred=self._net(seq).squeeze().numpy()   # (horizon,)
        Q_fc=np.maximum(0, pred*self._Qs+self._Qm)
        unc=max(5.,15*(1-self._r2)); delta=Q_fc*unc/100
        return {"Q_forecast":np.round(Q_fc,2),"Q_upper":np.round(Q_fc+delta,2),
                "Q_lower":np.round(np.maximum(0,Q_fc-delta),2),
                "horizon_days":self.horizon,"r2_train":round(self._r2,3),
                "uncertainty_pct":round(unc,1),
                "model":f"LSTM(hidden={self.hidden_size}, layers={self.n_layers}, PyTorch)"}

    def __repr__(self):
        if not self._fitted: return f"LSTMForecast(not fitted)"
        if getattr(self,"_fallback",False): return "LSTMForecast→LinearForecast(fallback)"
        return f"LSTMForecast(hidden={self.hidden_size},layers={self.n_layers},R²={self._r2:.3f},PyTorch)"
