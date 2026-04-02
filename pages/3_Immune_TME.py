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

st.set_page_config(page_title="VenuViz — Immune TME", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

CANCER_TYPES = ["LUAD", "BRCA", "CESC", "HNSC", "SKCM", "STAD", "LIHC", "KIRC", "BLCA", "OV"]
CELL_TYPES   = ["CD8+ T cells", "CD4+ T cells", "B cells", "Plasma cells", "NK cells", "Macrophages", "Dendritic cells", "Malignant cells", "Fibroblasts"]
CELL_COLORS  = ["#7D9D33","#a8c48a","#4DBBD5","#E64B35","#F39B7F","#3C5488","#00A087","#E1EAD8","#888888"]

st.markdown("""
<div class="page-header">
    <h1>Tumor immune microenvironment</h1>
    <p>Explore immune cell sub-populations using single-cell RNA-seq data — linked to patient survival outcome</p>
</div>
""", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")
    cancer      = st.selectbox("Cancer type", CANCER_TYPES)
    color_by    = st.radio("Color UMAP by", ["Cell type", "Sub-cluster", "Gene expression"])
    gene_overlay= st.text_input("Overlay gene expression (optional)", placeholder="e.g. CD8A, PD-L1")
    cells_filter= st.multiselect("Show cell types", CELL_TYPES, default=CELL_TYPES)
    generate    = st.button("Generate map →", use_container_width=True)

with main:
    if not generate:
        st.markdown("""
        <div class="empty-state">
            <h3>Select a cancer type to explore the immune landscape</h3>
            <p>UMAP of immune cell sub-populations linked to patient survival</p>
            <div class="pill-row">
                <span class="pill">LUAD</span>
                <span class="pill">TNBC</span>
                <span class="pill">CESC</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["UMAP", "Cell fractions", "Survival link", "Marker genes"])

        np.random.seed(hash(cancer) % 999)

        # ── Simulate UMAP data ────────────────────────────────────────────────
        cells_to_show = cells_filter if cells_filter else CELL_TYPES
        n_per_cell = 120
        umap_data = []
        for i, cell in enumerate(cells_to_show):
            cx = np.random.uniform(-8, 8)
            cy = np.random.uniform(-8, 8)
            x  = np.random.normal(cx, 1.2, n_per_cell)
            y  = np.random.normal(cy, 1.2, n_per_cell)
            for xi, yi in zip(x, y):
                umap_data.append({"x": xi, "y": yi, "cell_type": cell})
        df_umap = pd.DataFrame(umap_data)

        with tab1:
            fig_umap = go.Figure()
            for i, cell in enumerate(cells_to_show):
                subset = df_umap[df_umap["cell_type"] == cell]
                color  = CELL_COLORS[CELL_TYPES.index(cell)] if cell in CELL_TYPES else "#888888"

                if gene_overlay and color_by == "Gene expression":
                    expr_vals = np.random.exponential(1.5, len(subset))
                    fig_umap.add_trace(go.Scatter(
                        x=subset["x"], y=subset["y"], mode="markers",
                        marker=dict(color=expr_vals, colorscale="YlGn", size=4,
                                    colorbar=dict(title=gene_overlay, thickness=12)),
                        name=cell, showlegend=False,
                    ))
                else:
                    fig_umap.add_trace(go.Scatter(
                        x=subset["x"], y=subset["y"], mode="markers", name=cell,
                        marker=dict(color=color, size=4, opacity=0.75),
                    ))

            fig_umap.update_layout(
                title=f"UMAP — {cancer} Tumor Immune Microenvironment",
                xaxis_title="UMAP 1", yaxis_title="UMAP 2",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
            )
            fig_umap.update_xaxes(showgrid=False, zeroline=False)
            fig_umap.update_yaxes(showgrid=False, zeroline=False)

            st.plotly_chart(fig_umap, use_container_width=True)
            fig_umap = render_figure_editor(fig_umap, key_prefix="umap")

        with tab2:
            samples = [f"S{i+1:02d}" for i in range(12)]
            fractions = {}
            for cell in cells_to_show:
                fractions[cell] = np.random.dirichlet(np.ones(len(cells_to_show)), 1)[0][:12] if len(cells_to_show) > 0 else []

            fig_frac = go.Figure()
            raw = {cell: np.random.uniform(0.02, 0.3, 12) for cell in cells_to_show}
            totals = sum(raw.values())
            for i, cell in enumerate(cells_to_show):
                color = CELL_COLORS[CELL_TYPES.index(cell)] if cell in CELL_TYPES else "#888888"
                pct   = raw[cell] / totals * 100
                fig_frac.add_trace(go.Bar(name=cell, x=samples, y=pct, marker_color=color))

            fig_frac.update_layout(
                barmode="stack", title=f"Cell fractions per sample — {cancer}",
                xaxis_title="Sample", yaxis_title="Cell fraction (%)",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_frac, use_container_width=True)
            fig_frac = render_figure_editor(fig_frac, key_prefix="fractions")

            frac_df = pd.DataFrame(raw, index=samples)
            st.download_button("Download cell fraction data as CSV", frac_df.to_csv(), f"{cancer}_cell_fractions.csv", "text/csv")

        with tab3:
            selected_cell = st.selectbox("Select cell type for survival link", cells_to_show)
            n = 60
            t_hi = np.sort(np.random.exponential(40, n))
            t_lo = np.sort(np.random.exponential(22, n))

            def km(times):
                t = [0]; s = [1.0]; ar = len(times)
                for ti in np.unique(times):
                    d = np.sum(times == ti)
                    s.append(s[-1] * (1 - d/ar))
                    ar -= d; t.append(ti)
                return t, s

            th, sh = km(t_hi)
            tl, sl = km(t_lo)

            fig_km = go.Figure()
            fig_km.add_trace(go.Scatter(x=th, y=sh, mode="lines", name=f"High {selected_cell}", line=dict(color="#7D9D33", width=2.5)))
            fig_km.add_trace(go.Scatter(x=tl, y=sl, mode="lines", name=f"Low {selected_cell}",  line=dict(color="#a8c48a", width=2.5, dash="dash")))
            fig_km.update_layout(
                title=f"{selected_cell} infiltration — Survival in {cancer}",
                xaxis_title="Time (months)", yaxis_title="Survival probability",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"),
            )
            st.plotly_chart(fig_km, use_container_width=True)
            pval = round(np.random.uniform(0.001, 0.049), 3)
            hr   = round(np.random.uniform(1.2, 2.4), 2)
            st.markdown(f"**Log-rank p = {pval}** &nbsp;|&nbsp; **HR = {hr}** &nbsp;|&nbsp; Data: TCGA + TISCH2 (demo)")
            fig_km = render_figure_editor(fig_km, key_prefix="tme_km")

        with tab4:
            marker_data = []
            for cell in cells_to_show[:5]:
                genes = np.random.choice(["CD3D","CD8A","CD4","FOXP3","CD19","MS4A1","CD138","NKG7","FCGR3A","CD14","HLA-DRA","EPCAM","FAP","PECAM1"], 4, replace=False)
                for g in genes:
                    marker_data.append({
                        "Cell type": cell,
                        "Gene": g,
                        "Log2 FC": round(np.random.uniform(1.5, 5.0), 2),
                        "Adj. p-value": f"{np.random.uniform(0.0001, 0.05):.4f}",
                        "Avg expression": round(np.random.uniform(1.0, 6.0), 2),
                    })
            marker_df = pd.DataFrame(marker_data)
            st.dataframe(marker_df, use_container_width=True, hide_index=True)
            st.download_button("Download marker genes as CSV", marker_df.to_csv(index=False), f"{cancer}_markers.csv", "text/csv")

render_footer()
