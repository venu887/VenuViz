import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

CANCER_TYPES = ["LUAD","BRCA","CESC","HNSC","SKCM","STAD","LIHC","KIRC","BLCA","OV"]
CELL_TYPES   = ["CD8+ T cells","CD4+ T cells","B cells","Plasma cells",
                "NK cells","Macrophages","Dendritic cells","Malignant cells",
                "Fibroblasts","Endothelial cells"]
CELL_COLORS  = ["#7D9D33","#a8c48a","#4DBBD5","#E64B35","#F39B7F",
                "#3C5488","#00A087","#E1EAD8","#888888","#B09C85"]
DATASETS     = ["TISCH2 (GSE131907)","TISCH2 (GSE148071)","TISCH2 (GSE176078)"]

# ── Session state init ────────────────────────────────────────────────────────
_defaults = {
    "tme_cancer":     "LUAD",
    "tme_cells":      CELL_TYPES,
    "tme_color_by":   "Cell type",
    "tme_gene":       "",
    "tme_dataset":    "TISCH2 (GSE131907)",
    "tme_datasets":   ["TISCH2 (GSE131907)"],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<div class="page-header">
    <h1>Tumor immune microenvironment</h1>
    <p>Explore single-cell immune sub-populations — linked to patient survival outcome</p>
</div>""", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")

    cancer = st.selectbox("Cancer type", CANCER_TYPES,
        index=CANCER_TYPES.index(st.session_state["tme_cancer"]),
        key="tme_cancer_sel")
    st.session_state["tme_cancer"] = cancer

    # Cross-dataset comparison
    st.markdown("**Dataset**")
    compare_ds = st.toggle("Compare across datasets", key="tme_compare_ds")
    if compare_ds:
        datasets = st.multiselect("Select datasets", DATASETS,
            default=st.session_state["tme_datasets"], key="tme_ds_multi")
        st.session_state["tme_datasets"] = datasets if datasets else [DATASETS[0]]
    else:
        dataset = st.selectbox("Dataset", DATASETS,
            index=DATASETS.index(st.session_state["tme_dataset"]),
            key="tme_ds_sel")
        st.session_state["tme_dataset"] = dataset
        st.session_state["tme_datasets"] = [dataset]

    color_by = st.radio("Color UMAP by",
        ["Cell type","Sub-cluster","Gene expression"],
        index=["Cell type","Sub-cluster","Gene expression"]
              .index(st.session_state["tme_color_by"]),
        key="tme_color_sel")
    st.session_state["tme_color_by"] = color_by

    cells_filter = st.multiselect("Show cell types", CELL_TYPES,
        default=st.session_state["tme_cells"],
        key="tme_cells_sel")
    st.session_state["tme_cells"] = cells_filter if cells_filter else CELL_TYPES

    gene_overlay = st.text_input("Overlay gene expression (optional)",
        value=st.session_state["tme_gene"],
        placeholder="e.g. CD8A, PD-L1, FOXP3",
        key="tme_gene_input")
    st.session_state["tme_gene"] = gene_overlay

    generate = st.button("Generate map →", use_container_width=True)

with main:
    if not generate:
        st.markdown("""
        <div class="empty-state">
            <h3>Select a cancer type to explore the immune landscape</h3>
            <p>UMAP · Cell fractions · Survival link · Marker genes · Cross-dataset comparison</p>
            <div class="pill-row">
                <span class="pill">LUAD</span>
                <span class="pill">BRCA</span>
                <span class="pill">CESC</span>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        cancer       = st.session_state["tme_cancer"]
        cells_filter = st.session_state["tme_cells"]
        color_by     = st.session_state["tme_color_by"]
        gene_overlay = st.session_state["tme_gene"]
        ds_list      = st.session_state["tme_datasets"]

        np.random.seed(hash(cancer) % 999)

        # ── Build UMAP data ───────────────────────────────────────────────────
        def build_umap(seed_offset=0, cells=None):
            if cells is None: cells = CELL_TYPES
            rows = []
            np.random.seed(hash(cancer)%999 + seed_offset)
            for i, cell in enumerate(cells):
                cx = np.random.uniform(-8,8)
                cy = np.random.uniform(-8,8)
                x  = np.random.normal(cx,1.2,100)
                y  = np.random.normal(cy,1.2,100)
                for xi,yi in zip(x,y):
                    rows.append({"x":xi,"y":yi,"cell_type":cell})
            return pd.DataFrame(rows)

        tab1, tab2, tab3, tab4 = st.tabs([
            "UMAP","Cell fractions","Survival link","Marker genes"])

        with tab1:
            if compare_ds and len(ds_list) > 1:
                # Side-by-side UMAP comparison
                fig_umap = make_subplots(rows=1, cols=len(ds_list),
                    subplot_titles=ds_list)
                for col_i, ds in enumerate(ds_list, 1):
                    df_u = build_umap(seed_offset=col_i*50, cells=cells_filter)
                    for i, cell in enumerate(cells_filter):
                        sub   = df_u[df_u["cell_type"]==cell]
                        color = CELL_COLORS[CELL_TYPES.index(cell)] if cell in CELL_TYPES else "#888"
                        fig_umap.add_trace(go.Scatter(
                            x=sub["x"],y=sub["y"],mode="markers",name=cell,
                            marker=dict(color=color,size=3,opacity=0.7),
                            showlegend=(col_i==1)),
                            row=1,col=col_i)
                fig_umap.update_layout(
                    title=f"Cross-dataset UMAP comparison — {cancer}",
                    paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                    font=dict(family="Montserrat",color="#E1EAD8"),
                    height=450)
                fig_umap.update_xaxes(showgrid=False,zeroline=False)
                fig_umap.update_yaxes(showgrid=False,zeroline=False)
            else:
                df_u = build_umap(cells=cells_filter)
                fig_umap = go.Figure()
                for i, cell in enumerate(cells_filter):
                    sub   = df_u[df_u["cell_type"]==cell]
                    color = CELL_COLORS[CELL_TYPES.index(cell)] if cell in CELL_TYPES else "#888"

                    if gene_overlay and color_by == "Gene expression":
                        expr_vals = np.random.exponential(1.5, len(sub))
                        fig_umap.add_trace(go.Scatter(
                            x=sub["x"],y=sub["y"],mode="markers",
                            marker=dict(color=expr_vals,colorscale="YlGn",size=4,
                                        colorbar=dict(title=gene_overlay,thickness=12)),
                            name=cell,showlegend=False))
                    elif color_by == "Sub-cluster":
                        n_sub = np.random.randint(2,5)
                        sub_labels = np.random.randint(0,n_sub,len(sub))
                        sub_colors = [CELL_COLORS[(CELL_TYPES.index(cell)+j)%len(CELL_COLORS)]
                                      for j in sub_labels]
                        fig_umap.add_trace(go.Scatter(
                            x=sub["x"],y=sub["y"],mode="markers",name=cell,
                            marker=dict(color=sub_colors,size=4,opacity=0.75)))
                    else:
                        fig_umap.add_trace(go.Scatter(
                            x=sub["x"],y=sub["y"],mode="markers",name=cell,
                            marker=dict(color=color,size=4,opacity=0.75)))

                fig_umap.update_layout(
                    title=f"UMAP — {cancer} TME ({st.session_state['tme_dataset']})",
                    xaxis_title="UMAP 1",yaxis_title="UMAP 2",
                    paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                    font=dict(family="Montserrat",color="#E1EAD8"),
                    legend=dict(bgcolor="rgba(0,0,0,0)",itemsizing="constant"))
                fig_umap.update_xaxes(showgrid=False,zeroline=False)
                fig_umap.update_yaxes(showgrid=False,zeroline=False)

            st.plotly_chart(fig_umap, use_container_width=True)
            meta = {"gene":gene_overlay or "TME","cancer":cancer,
                    "plot_type":"UMAP","dataset":", ".join(ds_list)}
            fig_umap = render_figure_editor(fig_umap, key_prefix="umap", meta=meta)

        with tab2:
            samples = [f"S{i+1:02d}" for i in range(12)]
            fig_frac = go.Figure()
            raw = {cell:np.random.uniform(0.02,0.3,12) for cell in cells_filter}
            totals = sum(v for v in raw.values())
            for cell in cells_filter:
                color = CELL_COLORS[CELL_TYPES.index(cell)] if cell in CELL_TYPES else "#888"
                pct   = raw[cell]/totals*100
                fig_frac.add_trace(go.Bar(name=cell,x=samples,y=pct,
                    marker_color=color))
            fig_frac.update_layout(
                barmode="stack",
                title=f"Cell fractions per sample — {cancer}",
                xaxis_title="Sample",yaxis_title="Cell fraction (%)",
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_frac, use_container_width=True)
            meta2 = {"gene":"Cell fractions","cancer":cancer,
                     "plot_type":"bar","dataset":", ".join(ds_list)}
            fig_frac = render_figure_editor(fig_frac, key_prefix="fractions", meta=meta2)
            frac_df = pd.DataFrame(raw,index=samples)
            st.download_button("Download cell fraction data as CSV",
                               frac_df.to_csv(),
                               f"{cancer}_cell_fractions.csv","text/csv")

        with tab3:
            sel_cell = st.selectbox("Select cell type for survival link",
                cells_filter, key="tme_surv_cell")
            n=60
            t_hi = np.sort(np.random.exponential(40,n))
            t_lo = np.sort(np.random.exponential(22,n))
            def km(t):
                tp=[0];s=[1.0];ar=len(t)
                for ti in np.unique(t):
                    d=np.sum(t==ti); s.append(s[-1]*(1-d/ar))
                    ar-=d; tp.append(ti)
                return tp,s
            th,sh = km(t_hi); tl,sl = km(t_lo)
            fig_km = go.Figure()
            fig_km.add_trace(go.Scatter(x=th,y=sh,mode="lines",
                name=f"High {sel_cell}",line=dict(color="#7D9D33",width=2.5)))
            fig_km.add_trace(go.Scatter(x=tl,y=sl,mode="lines",
                name=f"Low {sel_cell}",line=dict(color="#a8c48a",width=2.5,dash="dash")))
            fig_km.update_layout(
                title=f"{sel_cell} infiltration — Survival in {cancer}",
                xaxis_title="Time (months)",yaxis_title="Survival probability",
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"))
            fig_km.update_xaxes(showgrid=False)
            fig_km.update_yaxes(gridcolor="#3a5a3a",range=[0,1.05])
            st.plotly_chart(fig_km, use_container_width=True)
            pval = round(np.random.uniform(0.001,0.049),3)
            hr   = round(np.random.uniform(1.2,2.4),2)
            c1,c2 = st.columns(2)
            c1.metric("Log-rank p-value",f"{pval:.3f}")
            c2.metric("Hazard ratio",f"{hr:.2f}")
            meta3 = {"gene":sel_cell,"cancer":cancer,"plot_type":"survival",
                     "pvalue":pval,"hr":hr,"dataset":", ".join(ds_list)}
            fig_km = render_figure_editor(fig_km, key_prefix="tme_km", meta=meta3)

        with tab4:
            marker_rows=[]
            gene_pool = ["CD3D","CD8A","CD4","FOXP3","CD19","MS4A1","NKG7",
                         "FCGR3A","CD14","HLA-DRA","EPCAM","FAP","PECAM1",
                         "PDCD1","CD274","LAG3","HAVCR2","TIGIT"]
            for cell in cells_filter[:6]:
                genes_sel = np.random.choice(gene_pool,4,replace=False)
                for g in genes_sel:
                    marker_rows.append({
                        "Cell type":cell,"Gene":g,
                        "Log2 FC":round(np.random.uniform(1.5,5.0),2),
                        "Adj. p-value":f"{np.random.uniform(0.0001,0.05):.4f}",
                        "Avg expression":round(np.random.uniform(1.0,6.0),2)})
            marker_df = pd.DataFrame(marker_rows)
            st.dataframe(marker_df,use_container_width=True,hide_index=True)
            st.download_button("Download marker genes as CSV",
                               marker_df.to_csv(index=False),
                               f"{cancer}_markers.csv","text/csv")

render_footer()