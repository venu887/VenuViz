import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="VenuViz — Precision Cancer Genomics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from components.styles import inject_styles
from components.navbar import render_navbar
from components.footer import render_footer

inject_styles()
render_navbar()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">Open Access · Free · No Login Required</div>
    <h1 class="hero-title">Cancer genomics,<br>visualized in seconds</h1>
    <p class="hero-sub">
        Search any gene across lung, breast, and cervical cancers.
        Get publication-ready survival curves, expression plots, and immune
        cell maps — with a built-in figure editor for any journal.
    </p>
    <div class="hero-buttons">
        <a href="/Explorer" target="_self" class="btn-primary">Start Exploring →</a>
        <a href="/About" target="_self" class="btn-secondary">How to Cite</a>
    </div>
    <p class="hero-trust">
        Powered by TCGA · TISCH2 · GEO &nbsp;|&nbsp; MIT Licensed · Open Source
    </p>
</div>
""", unsafe_allow_html=True)

# ── Stats Bar ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
stats = [
    ("33", "Cancer types"),
    ("20,000+", "Genes searchable"),
    ("10,000+", "Patient samples"),
    ("100%", "Free access"),
]
for col, (val, label) in zip([col1, col2, col3, col4], stats):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{val}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>What VenuViz does</h2>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
features = [
    ("◈", "Gene expression",
     "Compare expression across tumor stages, subtypes, and normal tissue. Boxplots and violin plots generated instantly.",
     "/Explorer"),
    ("◉", "Survival analysis",
     "Kaplan-Meier curves with p-value, hazard ratio, and one-click publication export.",
     "/Survival"),
    ("◎", "Immune TME",
     "Single-cell immune sub-population maps linked to patient survival outcome.",
     "/Immune_TME"),
    ("◆", "Biomarker predictor",
     "ML-based immunotherapy response prediction with transparent feature importance.",
     "/Biomarker"),
]
for col, (icon, title, desc, link) in zip([c1, c2, c3, c4], features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3 class="feature-title">{title}</h3>
            <p class="feature-desc">{desc}</p>
            <a href="{link}" target="_self" class="feature-link">Explore →</a>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Differentiator ────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>The VenuViz difference</h2>", unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)
diffs = [
    ("⬡", "Integrated workflow",
     "Expression, survival, immune landscape, and biomarker prediction in one platform. No switching tools.", False),
    ("◈", "Publication figure editor",
     "Customize colors, fonts, and resolution to match any journal spec. No other tool offers this.", True),
    ("◉", "No coding required",
     "Designed for experimental biologists and clinical researchers — not just bioinformaticians.", False),
    ("◎", "Expert curated",
     "Built by a computational cancer biologist specializing in lung, breast, and cervical cancers.", False),
]
for col, (icon, title, desc, highlight) in zip([d1, d2, d3, d4], diffs):
    with col:
        cls = "diff-card highlight" if highlight else "diff-card"
        st.markdown(f"""
        <div class="{cls}">
            <div class="diff-icon">{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>How it works</h2>", unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
steps = [
    ("01", "Search",
     "Type any gene name — CD8A, FOXP3, TP53, or any biomarker of interest"),
    ("02", "Select",
     "Choose your cancer type and analysis — expression, survival, immune landscape, or biomarker prediction"),
    ("03", "Download",
     "Export a publication-ready figure customized to your journal's specifications"),
]
for col, (num, title, desc) in zip([s1, s2, s3], steps):
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">{num}</div>
            <h3 class="step-title">{title}</h3>
            <p class="step-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Citation Banner ───────────────────────────────────────────────────────────
st.markdown("""
<div class="cite-banner">
    <h3>Using VenuViz in your research?</h3>
    <p>VenuViz is free and open-access. If it contributes to your work, please cite us.</p>
    <div class="cite-box">
        Mekala, V. (2026). VenuViz: An integrated cancer genomics visualization platform
        with publication-ready figure export. <em>Bioinformatics</em>. DOI: pending
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Developer Section ─────────────────────────────────────────────────────────
st.markdown("""
<div class="dev-section">
    <h2 class="section-title">Built by a researcher, for researchers</h2>
    <p class="dev-bio">
        VenuViz was developed by <strong>Venugopal Mekala</strong>, a Postdoctoral Scholar
        specializing in computational cancer biology, transcriptomics, and tumor immunology.
        Built to make cancer genomic data accessible to all researchers regardless of coding background.
    </p>
    <div class="dev-links">
        <a href="#" class="dev-link">Google Scholar</a>
        <a href="#" class="dev-link">ORCID</a>
        <a href="#" class="dev-link">GitHub</a>
        <a href="#" class="dev-link">LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)

render_footer()
