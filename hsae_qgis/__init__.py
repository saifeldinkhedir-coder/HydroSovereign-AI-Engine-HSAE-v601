"""
HydroSovereign AI Engine (HSAE) v6.0.3 — QGIS Plugin
=====================================================
Author:  Seifeldin M.G. Alkedir
ORCID:   0000-0003-0821-2991
Email:   saifeldinkhedir@gmail.com
GitHub:  https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
DOI:     10.5281/zenodo.19180160
JOSS:    https://joss.theoj.org/papers/d6c37d0e07d1325e96c00d0844871a35
App:     https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app
"""


def classFactory(iface):
    from .plugin import HSAEPlugin
    return HSAEPlugin(iface)
