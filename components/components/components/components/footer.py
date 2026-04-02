import streamlit as st

def render_footer():
    st.markdown("""
    <div class="vv-footer">
        <div class="footer-links">
            <a href="/Explorer" target="_self">Explorer</a>
            <a href="/Survival" target="_self">Survival</a>
            <a href="/Immune_TME" target="_self">Immune TME</a>
            <a href="/Biomarker" target="_self">Biomarker</a>
            <a href="/About" target="_self">About</a>
            <a href="/About" target="_self">Cite Us</a>
            <a href="https://github.com" target="_blank">GitHub</a>
            <a href="#" target="_self">Google Scholar</a>
            <a href="/About" target="_self">Contact</a>
        </div>
        <p class="footer-copy">VenuViz · © 2026 Venugopal Mekala</p>
        <p class="footer-disclaimer">
            Data sourced from TCGA, TISCH2, and GEO public repositories.
            For research use only. Not intended for clinical decision making.
        </p>
    </div>
    """, unsafe_allow_html=True)
