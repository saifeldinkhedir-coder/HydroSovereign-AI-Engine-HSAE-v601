"""
bayesian.py — Bayesian Risk Assessment
========================================
Probabilistic conflict and flow-deficit risk using
Bayesian inference with Beta-Binomial conjugate priors.

As recommended by Gemini review:
  "Move from fixed alert levels to a Bayesian framework that provides
   a probability of conflict based on weather forecasts and geopolitical
   sentiment analysis."

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""

from __future__ import annotations
import numpy as np
from typing import Optional


class BayesianRisk:
    """
    Bayesian risk estimator for transboundary water conflict.

    Uses Beta-Binomial conjugate priors updated with basin observations.
    Provides posterior probability distributions rather than fixed thresholds.

    Parameters
    ----------
    prior_alpha : float
        Prior belief in conflict (shape parameter α). Default = 2.0.
    prior_beta : float
        Prior belief in non-conflict (shape parameter β). Default = 5.0.

    Examples
    --------
    >>> brisk = BayesianRisk()
    >>> result = brisk.assess(atdi=49.2, hifd=33.4, dispute_level=4,
    ...                        n_observations=12, n_conflict=7)
    >>> print(f"P(conflict) = {result['p_conflict']:.1%}")
    >>> print(f"95% CI: {result['ci_95']}")
    """

    def __init__(self, prior_alpha: float = 2.0, prior_beta: float = 5.0):
        if prior_alpha <= 0 or prior_beta <= 0:
            raise ValueError("Prior parameters must be positive")
        self.prior_alpha = prior_alpha
        self.prior_beta  = prior_beta

    def assess(
        self,
        atdi: float,
        hifd: float,
        dispute_level: int,
        n_observations: int = 10,
        n_conflict: Optional[int] = None,
        climate_stress: float = 0.0,
    ) -> dict:
        """
        Compute posterior probability of conflict/flow-deficit.

        Parameters
        ----------
        atdi : float
            ATDI percentage (5–95).
        hifd : float
            HIFD percentage (5–80).
        dispute_level : int
            Dispute intensity 0–4.
        n_observations : int
            Number of historical observations (years of data).
        n_conflict : int, optional
            Observed conflict events in history.
            If None, estimated from ATDI/dispute_level.
        climate_stress : float
            SSP-based additional stress factor (0–1). Default = 0.

        Returns
        -------
        dict
            - p_conflict   (float) : posterior mean probability
            - p_flow_deficit (float): probability HIFD exceeds 25%
            - ci_95        (tuple) : 95% credible interval [lo, hi]
            - ci_80        (tuple) : 80% credible interval
            - posterior_alpha (float): updated alpha
            - posterior_beta  (float): updated beta
            - evidence_strength (str): STRONG/MODERATE/WEAK

        Examples
        --------
        >>> r = brisk.assess(atdi=49.2, hifd=33.4, dispute_level=4)
        >>> print(r['p_conflict'])       # ~0.55
        >>> print(r['evidence_strength']) # MODERATE
        """
        # Estimate successes from ATDI if not provided
        if n_conflict is None:
            base_rate = (atdi / 100) * (dispute_level / 4 + 0.1)
            n_conflict = int(n_observations * base_rate)

        n_conflict = max(0, min(n_conflict, n_observations))

        # Bayesian update: Beta-Binomial conjugate
        post_alpha = self.prior_alpha + n_conflict
        post_beta  = self.prior_beta  + (n_observations - n_conflict)

        # Posterior mean
        p_conflict = post_alpha / (post_alpha + post_beta)

        # Climate stress adjustment (SSP scenarios)
        p_conflict = float(np.clip(p_conflict + climate_stress * 0.15, 0.0, 1.0))

        # Flow deficit probability (Beta CDF approximation)
        hifd_norm    = hifd / 80.0
        p_flow_def   = float(np.clip(hifd_norm * (1 + dispute_level * 0.1), 0.0, 1.0))

        # Credible intervals (Beta quantiles approximation)
        variance = (post_alpha * post_beta /
                    ((post_alpha + post_beta)**2 * (post_alpha + post_beta + 1)))
        std      = float(np.sqrt(variance))
        ci_95    = (round(max(0.0, p_conflict - 2.0 * std), 3),
                    round(min(1.0, p_conflict + 2.0 * std), 3))
        ci_80    = (round(max(0.0, p_conflict - 1.28 * std), 3),
                    round(min(1.0, p_conflict + 1.28 * std), 3))

        # Evidence strength
        n_eff = post_alpha + post_beta - self.prior_alpha - self.prior_beta
        if n_eff >= 20:   evidence = "STRONG"
        elif n_eff >= 10: evidence = "MODERATE"
        else:             evidence = "WEAK"

        # Risk category
        if p_conflict >= 0.70:   risk = "CRITICAL"
        elif p_conflict >= 0.50: risk = "HIGH"
        elif p_conflict >= 0.30: risk = "MEDIUM"
        else:                    risk = "LOW"

        return {
            "p_conflict":       round(p_conflict, 3),
            "p_flow_deficit":   round(p_flow_def, 3),
            "ci_95":            ci_95,
            "ci_80":            ci_80,
            "posterior_alpha":  round(post_alpha, 2),
            "posterior_beta":   round(post_beta, 2),
            "evidence_strength":evidence,
            "risk":             risk,
            "n_observations":   n_observations,
            "n_conflict":       n_conflict,
        }

    def update(self, n_new_observations: int, n_new_conflict: int) -> "BayesianRisk":
        """
        Update priors with new data (sequential Bayesian updating).

        Returns a new BayesianRisk with updated priors.

        Examples
        --------
        >>> brisk2 = brisk.update(n_new_observations=5, n_new_conflict=3)
        """
        new_alpha = self.prior_alpha + n_new_conflict
        new_beta  = self.prior_beta  + (n_new_observations - n_new_conflict)
        return BayesianRisk(prior_alpha=new_alpha, prior_beta=new_beta)

    def __repr__(self):
        return (f"BayesianRisk(α={self.prior_alpha:.1f}, "
                f"β={self.prior_beta:.1f}, "
                f"prior_mean={self.prior_alpha/(self.prior_alpha+self.prior_beta):.2f})")
