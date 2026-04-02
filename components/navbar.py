import streamlit as st

def render_navbar():
    st.markdown("""
    <div class="vv-nav">
        <div>
            <a href="/" class="vv-logo" target="_self">
                <span>Venu</span>Viz
            </a>
            <span class="vv-tagline">Precision cancer genomics</span>
        </div>
        <div class="vv-nav-links">
            <a href="/Explorer" target="_self">Explorer</a>
            <a href="/Survival" target="_self">Survival</a>
            <a href="/Immune_TME" target="_self">Immune TME</a>
            <a href="/Biomarker" target="_self">Biomarker</a>
            <a href="/About" target="_self">About</a>
            <a href="/About#cite" target="_self" class="vv-nav-cta">Cite Us</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
