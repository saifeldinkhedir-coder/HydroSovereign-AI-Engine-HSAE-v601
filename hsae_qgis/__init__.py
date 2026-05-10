"""
HydroSovereign AI Engine (HSAE) v6.0.5 — QGIS Plugin
=====================================================
Author:  Seifeldin M.G. Alkhedir
ORCID:   0000-0003-0821-2991
Email:   saifeldinkhedir@gmail.com
GitHub:  https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
DOI:     10.5281/zenodo.19180160
Preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6661396
App:     https://hydrosovereign-ai-engine-hsae-v6.0.8-6euz2zxcmerkzxgordmvxf.streamlit.app
"""


def classFactory(iface):
    from .plugin import HSAEPlugin
    return HSAEPlugin(iface)
