"""
legal.py — HSAE v6.01 UN Watercourses Convention 1997 Legal Engine
====================================================================
Automated UNWC Article triggering and legal assessment.

Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""

from __future__ import annotations
from typing import List


def check_art7_nsh(atdi: float) -> bool:
    """Art.7 — No Significant Harm. Triggered when ATDI >= 40%."""
    return atdi >= 40.0


def check_art20_envflow(hifd: float) -> bool:
    """Art.20 — Environmental Flows. Triggered when HIFD >= 25%."""
    return hifd >= 25.0


def check_art33_dispute(atdi: float) -> bool:
    """Art.33 — Dispute Resolution. Triggered when ATDI >= 55%."""
    return atdi >= 55.0


def check_art35_emergency(atdi: float) -> bool:
    """Art.35 — Emergency Situations. Triggered when ATDI >= 70%."""
    return atdi >= 70.0


def get_triggered_articles(atdi: float, hifd: float) -> List[str]:
    """
    Return list of all UNWC 1997 articles triggered by basin indices.

    Parameters
    ----------
    atdi : float
        ATDI percentage (5–95).
    hifd : float
        HIFD percentage (5–80).

    Returns
    -------
    list of str
        Triggered UNWC articles.

    Examples
    --------
    >>> get_triggered_articles(49.2, 33.4)
    ['Art.5 ERU', 'Art.9 Data Sharing', 'Art.7 NSH', 'Art.20 Env.Flow']
    """
    arts = ["Art.5 ERU", "Art.9 Data Sharing"]
    if check_art7_nsh(atdi):     arts.append("Art.7 NSH")
    if check_art20_envflow(hifd): arts.append("Art.20 Env.Flow")
    if check_art33_dispute(atdi): arts.append("Art.33 Dispute")
    if check_art35_emergency(atdi): arts.append("Art.35 Emergency")
    return arts


def get_legal_assessment(atdi: float, hifd: float,
                          dispute_level: int, n_countries: int) -> dict:
    """
    Full legal assessment under UNWC 1997.

    Returns triggered articles, recommended actions,
    and ICJ/PCA pathway if needed.
    """
    articles = get_triggered_articles(atdi, hifd)

    if atdi >= 70:
        recommendation = "Emergency notification under Art.35 UNWC required"
        pathway = "ICJ Emergency Relief + Art.35"
    elif atdi >= 55:
        recommendation = "Formal dispute resolution under Art.33 UNWC"
        pathway = "PCA Arbitration or ICJ"
    elif atdi >= 40:
        recommendation = "Joint Technical Committee under Art.24 UNWC"
        pathway = "Art.8 Information Exchange + Art.24 JMO"
    else:
        recommendation = "Regular data exchange under Art.9 UNWC"
        pathway = "Art.9 Regular Exchange"

    return {
        "articles":       articles,
        "n_articles":     len(articles),
        "recommendation": recommendation,
        "pathway":        pathway,
        "art7_nsh":       check_art7_nsh(atdi),
        "art20_envflow":  check_art20_envflow(hifd),
        "art33_dispute":  check_art33_dispute(atdi),
        "art35_emergency":check_art35_emergency(atdi),
    }
