import streamlit as st
import json
from typing import Optional

from hsae_intro import intro_page
from hsae_v430 import page_v430, GLOBAL_BASINS_V430
from hsae_v990 import page_v990

st.set_page_config(
    page_title="HSAE – HydroSovereign AI Engine",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

_BASIN_NAMES = list(GLOBAL_BASINS_V430.keys())


def _init_session_defaults():
    defaults = {
        "active_page":            "Intro",
        "data_mode":              "Indirect CSV (Archive)",
        "active_basin_name":      _BASIN_NAMES[0],
        "active_basin_name_v430": _BASIN_NAMES[0],
        "custom_geom":            None,
        "custom_geom_name":       None,
        "time_start":             "2020-01-01",
        "time_end":               "2021-01-01",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _safe_basin_index(name: str) -> int:
    try:
        return _BASIN_NAMES.index(name)
    except ValueError:
        st.session_state["active_basin_name"]      = _BASIN_NAMES[0]
        st.session_state["active_basin_name_v430"] = _BASIN_NAMES[0]
        return 0


def _parse_uploaded_geo(file) -> Optional[dict]:
    if file is None:
        return None
    name = file.name.lower()
    data = file.read()
    if name.endswith(".geojson") or name.endswith(".json"):
        try:
            return json.loads(data.decode("utf-8"))
        except Exception:
            st.error("Failed to parse GeoJSON file.")
            return None
    st.error("Only GeoJSON (.geojson / .json) is supported currently.")
    return None


def main():
    _init_session_defaults()

    # ── Navigation ──────────────────────────────────────────────────────────
    _PAGES = ["Intro", "v430 – Hybrid DSS", "v990 – Legal Nexus"]
    active_page = st.session_state.get("active_page", "Intro")
    if active_page not in _PAGES:
        active_page = "Intro"

    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Module", _PAGES,
        index=_PAGES.index(active_page),
        key="nav_radio",
    )
    st.session_state["active_page"] = page

    # ── Global Basin Selector ────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Global Basin")

    current_basin = st.session_state.get("active_basin_name", _BASIN_NAMES[0])
    safe_idx      = _safe_basin_index(current_basin)

    basin_name = st.sidebar.selectbox(
        "Predefined Basin / Reservoir",
        _BASIN_NAMES,
        index=safe_idx,
        key="app_basin_selector",
    )
    st.session_state["active_basin_name"]      = basin_name
    st.session_state["active_basin_name_v430"] = basin_name
    st.session_state["active_basin_cfg"]       = GLOBAL_BASINS_V430[basin_name]

    # ── Custom Basin GeoJSON ─────────────────────────────────────────────────
    st.sidebar.markdown("### Custom Basin Geometry")
    uploaded = st.sidebar.file_uploader(
        "Upload custom basin (GeoJSON). Overrides predefined geometry in GEE mode.",
        type=["json", "geojson"],
        key="custom_basin_uploader",
    )
    custom_geom = _parse_uploaded_geo(uploaded) if uploaded else None
    if custom_geom is not None:
        st.session_state["custom_geom"]      = custom_geom
        st.session_state["custom_geom_name"] = uploaded.name
        st.sidebar.success("✅ Custom basin geometry loaded.")
    else:
        st.session_state.setdefault("custom_geom",      None)
        st.session_state.setdefault("custom_geom_name", None)

    if st.session_state.get("custom_geom") is not None:
        st.sidebar.info(f"📐 Using: {st.session_state['custom_geom_name']}")

    # ── Time Window (GEE) ────────────────────────────────────────────────────
    st.sidebar.markdown("### Time Window (GEE)")
    col_t1, col_t2 = st.sidebar.columns(2)
    with col_t1:
        t_start = st.text_input(
            "Start (YYYY-MM-DD)",
            value=st.session_state["time_start"],
            key="time_start_input",
        )
    with col_t2:
        t_end = st.text_input(
            "End (YYYY-MM-DD)",
            value=st.session_state["time_end"],
            key="time_end_input",
        )
    st.session_state["time_start"] = t_start
    st.session_state["time_end"]   = t_end

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Mode A: Offline CSV archive — fast replay.\n"
        "Mode B: Direct GEE — live global analysis."
    )

    # ── Page routing ─────────────────────────────────────────────────────────
    if page == "Intro":
        intro_page()
    elif page == "v430 – Hybrid DSS":
        page_v430()
    elif page == "v990 – Legal Nexus":
        page_v990()


if __name__ == "__main__":
    main()
