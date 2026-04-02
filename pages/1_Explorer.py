import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.styles import inject_styles
from components.navbar import render_navbar
from components.footer import render_footer
from components.figure_editor import render_figure_editor

st.set_page_config(page_title="VenuViz — Gene Explorer", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

CANCER_TYPES = [
    "ACC","BLCA","BRCA","CESC","CHOL","COAD","DLBC","ESCA","GBM",
    "HNSC","KICH","KIRC","KIRP","LAML","LGG","LIHC","LUAD","LUSC",
    "MESO","OV","PAAD","PCPG","PRAD","READ","SARC","SKCM","STAD",
    "TGCT","THCA","THYM","UCEC","UCS","UVM",
]
EXAMPLE_GENES = ["TP53", "CD8A", "FOXP3"]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>Gene expression explorer</h1>
    <p>Compare expression of any gene across cancer types, tumor stages, and subtypes — instantly</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")
    gene = st.text_input("Gene symbol", placeholder="e.g. TP53, CD8A, FOXP3", value="TP53")

    # Example pills
    col_a, col_b, col_c = st.columns(3)
    for col, eg in zip([col_a, col_b, col_c], EXAMPLE_GENES):
        with col:
            if st.button(eg, key=f"pill_{eg}"):
                gene = eg

    cancer = st.selectbox("Cancer type", CANCER_TYPES, index=CANCER_TYPES.index("LUAD"))
    plot_type = st.radio("Plot type", ["Boxplot", "Violin", "Dotplot"], horizontal=True)
    group_by  = st.selectbox("Group by", ["Normal vs Tumor", "Tumor stage", "Tumor subtype"])
    analyze   = st.button("Analyze →", use_container_width=True)

with main:
    if not gene or not analyze:
        st.markdown("""
        <div class="empty-state">
            <h3>Enter a gene symbol to begin</h3>
            <p>Select a gene and cancer type, then click Analyze</p>
            <div class="pill-row">
                <span class="pill">TP53</span>
                <span class="pill">CD8A</span>
                <span class="pill">FOXP3</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        gene = gene.upper().strip()

        # ── Generate demo data ────────────────────────────────────────────────
        np.random.seed(hash(gene + cancer) % 999)
        n_tumor, n_normal = 120, 40

        if group_by == "Normal vs Tumor":
            groups = ["Normal"] * n_normal + ["Tumor"] * n_tumor
            vals   = list(np.random.normal(4.5, 1.2, n_normal)) + \
                     list(np.random.normal(6.8, 1.8, n_tumor))
            colors = {"Normal": "#a8c48a", "Tumor": "#7D9D33"}

        elif group_by == "Tumor stage":
            stages = ["Stage I", "Stage II", "Stage III", "Stage IV"]
            groups, vals = [], []
            for i, s in enumerate(stages):
                n = 35
                groups += [s] * n
                vals   += list(np.random.normal(5 + i * 0.7, 1.5, n))
            colors = dict(zip(stages, ["#a8c48a", "#7D9D33", "#4a7a1a", "#2d5010"]))

        else:
            subtypes = ["Luminal A", "Luminal B", "HER2+", "TNBC"]
            groups, vals = [], []
            for i, s in enumerate(subtypes):
                n = 40
                groups += [s] * n
                vals   += list(np.random.normal(5 + i * 0.5, 1.4, n))
            colors = dict(zip(subtypes, ["#a8c48a", "#7D9D33", "#4a7a1a", "#2d5010"]))

        df = pd.DataFrame({"group": groups, "expression": vals})
        group_order = list(dict.fromkeys(groups))

        # ── Build figure ──────────────────────────────────────────────────────
        if plot_type == "Boxplot":
            fig = go.Figure()
            for g in group_order:
                subset = df[df["group"] == g]["expression"]
                fig.add_trace(go.Box(
                    y=subset, name=g,
                    marker_color=colors.get(g, "#7D9D33"),
                    line_color=colors.get(g, "#7D9D33"),
                    fillcolor=colors.get(g, "#7D9D33"),
                    opacity=0.8,
                    boxmean=True,
                ))

        elif plot_type == "Violin":
            fig = go.Figure()
            for g in group_order:
                subset = df[df["group"] == g]["expression"]
                fig.add_trace(go.Violin(
                    y=subset, name=g,
                    fillcolor=colors.get(g, "#7D9D33"),
                    line_color=colors.get(g, "#7D9D33"),
                    opacity=0.8, box_visible=True, meanline_visible=True,
                ))

        else:  # Dotplot
            fig = go.Figure()
            for g in group_order:
                subset = df[df["group"] == g]
                fig.add_trace(go.Scatter(
                    x=[g] * len(subset),
                    y=subset["expression"],
                    mode="markers",
                    name=g,
                    marker=dict(color=colors.get(g, "#7D9D33"), size=5, opacity=0.6),
                ))

        fig.update_layout(
            title=f"{gene} expression in {cancer} — {group_by}",
            yaxis_title="Expression (log2 TPM)",
            xaxis_title=group_by,
            paper_bgcolor="#1B3022",
            plot_bgcolor="#243d2b",
            font=dict(family="Montserrat", color="#E1EAD8"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#3a5a3a", gridwidth=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # ── Stats table ───────────────────────────────────────────────────────
        st.markdown("**Summary statistics**")
        stats_data = []
        for g in group_order:
            subset = df[df["group"] == g]["expression"]
            stats_data.append({
                "Group": g,
                "N": len(subset),
                "Median": f"{subset.median():.2f}",
                "Mean":   f"{subset.mean():.2f}",
                "SD":     f"{subset.std():.2f}",
            })
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div style='font-size:0.78rem; color:#a8c48a; margin-top:0.5rem'>
        Statistical test: Wilcoxon rank-sum &nbsp;|&nbsp; Gene: <strong style='color:#E1EAD8'>{gene}</strong>
        &nbsp;|&nbsp; Cancer: <strong style='color:#E1EAD8'>{cancer}</strong>
        &nbsp;|&nbsp; Data source: TCGA (demo)
        </div>
        """, unsafe_allow_html=True)

        # ── Figure editor ─────────────────────────────────────────────────────
        fig = render_figure_editor(fig, key_prefix="explorer")

        # ── CSV download ──────────────────────────────────────────────────────
        csv = df.to_csv(index=False)
        st.download_button("Download data as CSV", csv, f"{gene}_{cancer}_expression.csv", "text/csv")

render_footer()
