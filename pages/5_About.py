import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.styles import inject_styles
from components.navbar import render_navbar
from components.footer import render_footer

st.set_page_config(page_title="VenuViz — About", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

st.markdown("""
<div class="page-header">
    <h1>About VenuViz</h1>
    <p>Built by a researcher, for researchers</p>
</div>
""", unsafe_allow_html=True)

# ── Tool description ──────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#243d2b;border:1px solid #3a5a3a;border-radius:12px;padding:1.5rem 2rem;margin-bottom:2rem'>
<p style='color:#a8c48a;font-size:0.95rem;line-height:1.8;margin:0'>
VenuViz is a free, open-access cancer genomics visualization platform that integrates
gene expression, survival analysis, single-cell immune landscape, and immunotherapy response
prediction in a single modern interface — with a built-in publication figure editor.
Designed to make complex multi-omics data accessible to all researchers, regardless of
coding background.
</p>
</div>
""", unsafe_allow_html=True)

# ── Developer card ────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>Developer</h2>", unsafe_allow_html=True)
dev_col, info_col = st.columns([1, 3])
with dev_col:
    st.markdown("""
    <div style='background:#243d2b;border:1px solid #3a5a3a;border-radius:12px;
    padding:2rem;text-align:center'>
    <div style='width:80px;height:80px;border-radius:50%;background:#7D9D33;
    margin:0 auto 1rem;display:flex;align-items:center;justify-content:center;
    font-size:1.8rem;font-weight:800;color:#fff'>VM</div>
    <h3 style='color:#E1EAD8;font-size:1rem;margin-bottom:0.2rem'>Venugopal Mekala</h3>
    <p style='color:#a8c48a;font-size:0.78rem;margin:0'>Postdoctoral Scholar</p>
    </div>
    """, unsafe_allow_html=True)

with info_col:
    st.markdown("""
    <div style='background:#243d2b;border:1px solid #3a5a3a;border-radius:12px;padding:1.5rem'>
    <p style='color:#a8c48a;font-size:0.88rem;line-height:1.8;margin-bottom:1rem'>
    Specializing in computational cancer biology, transcriptomics (bulk, small RNA, single-cell,
    and spatial), epigenomics, and tumor immunology. Developed machine learning models for
    immunotherapy response prediction and investigated immune cell sub-populations in lung
    adenocarcinoma and triple-negative breast cancer using scRNA-seq.
    </p>
    <div style='display:flex;gap:0.8rem;flex-wrap:wrap'>
        <a href='#' class='dev-link'>Google Scholar</a>
        <a href='#' class='dev-link'>ORCID</a>
        <a href='#' class='dev-link'>GitHub</a>
        <a href='#' class='dev-link'>LinkedIn</a>
        <a href='mailto:' class='dev-link'>Email</a>
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── What makes VenuViz different ─────────────────────────────────────────────
st.markdown("<h2 class='section-title'>What makes VenuViz different</h2>", unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)
diffs = [
    ("Integrated workflow", "Expression + survival + scRNA immune landscape + ML prediction in one platform. No tool switching."),
    ("Publication figure editor", "Customize colors, fonts, DPI, and dimensions to match any journal spec before export. Unique to VenuViz."),
    ("No coding required", "Designed for experimental biologists and clinical researchers — not just bioinformaticians."),
    ("Expert curated", "Built and maintained by a domain expert in lung, breast, and cervical cancer computational biology."),
]
for col, (title, desc) in zip([d1, d2, d3, d4], diffs):
    with col:
        st.markdown(f"""
        <div class='diff-card'>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Data sources ──────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>Data sources</h2>", unsafe_allow_html=True)
sources = [
    ("TCGA", "The Cancer Genome Atlas — 33 cancer types, bulk RNA-seq expression and clinical data", "https://portal.gdc.cancer.gov"),
    ("TISCH2", "Tumor Immune Single Cell Hub — 190 scRNA-seq datasets across 50 cancer types", "http://tisch.comp-genomics.org"),
    ("GEO", "Gene Expression Omnibus — public gene expression datasets", "https://ncbi.nlm.nih.gov/geo"),
    ("CCLE", "Cancer Cell Line Encyclopedia — cancer cell line expression profiles", "https://depmap.org"),
]
sc1, sc2, sc3, sc4 = st.columns(4)
for col, (name, desc, link) in zip([sc1, sc2, sc3, sc4], sources):
    with col:
        st.markdown(f"""
        <div style='background:#243d2b;border:1px solid #3a5a3a;border-radius:10px;padding:1.2rem'>
            <h4 style='color:#7D9D33;font-size:0.95rem;margin-bottom:0.4rem'>{name}</h4>
            <p style='color:#a8c48a;font-size:0.78rem;line-height:1.5;margin-bottom:0.8rem'>{desc}</p>
            <a href='{link}' target='_blank' style='color:#7D9D33;font-size:0.75rem;text-decoration:none'>Visit source →</a>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Citation ──────────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title' id='cite'>How to cite VenuViz</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='cite-banner'>
    <h3>Using VenuViz in your research?</h3>
    <p>VenuViz is free and open-access. If it contributes to your work, please cite us to support continued development.</p>
    <div class='cite-box'>
        Mekala, V. (2026). VenuViz: An integrated cancer genomics visualization platform
        with publication-ready figure export. <em>Bioinformatics</em>. DOI: pending
    </div>
</div>
""", unsafe_allow_html=True)

citation_text = "Mekala, V. (2026). VenuViz: An integrated cancer genomics visualization platform with publication-ready figure export. Bioinformatics. DOI: pending"
st.download_button("Copy / Download citation", citation_text, "venuviz_citation.txt", "text/plain")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Version history ───────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>Version history</h2>", unsafe_allow_html=True)
versions = [
    ("v1.0", "2026", "Initial launch — LUAD, BRCA (TNBC), CESC. All four analysis modules."),
    ("v1.1", "Planned", "Expanded cancer types across all TCGA cohorts."),
    ("v2.0", "Planned", "Spatial transcriptomics module and multi-omics integration."),
]
for v, date, notes in versions:
    st.markdown(f"""
    <div style='display:flex;gap:1.5rem;padding:0.8rem 0;border-bottom:1px solid #3a5a3a;
    align-items:flex-start;font-size:0.85rem'>
        <span style='color:#7D9D33;font-weight:700;min-width:40px'>{v}</span>
        <span style='color:#a8c48a;min-width:80px'>{date}</span>
        <span style='color:#E1EAD8'>{notes}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── Contact ───────────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>Contact</h2>", unsafe_allow_html=True)
st.markdown("""
<div style='background:#243d2b;border:1px solid #3a5a3a;border-radius:12px;padding:1.5rem'>
    <p style='color:#a8c48a;font-size:0.88rem;line-height:1.7;margin-bottom:1rem'>
    For bug reports, feature requests, or collaboration inquiries:
    </p>
    <div style='display:flex;gap:1rem;flex-wrap:wrap'>
        <a href='mailto:' class='dev-link'>Email</a>
        <a href='https://github.com' target='_blank' class='dev-link'>GitHub Issues</a>
    </div>
</div>
""", unsafe_allow_html=True)

render_footer()
