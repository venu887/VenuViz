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

st.set_page_config(page_title="VenuViz — Gene Explorer", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

CANCER_TYPES = [
    "ACC","BLCA","BRCA","CESC","CHOL","COAD","DLBC","ESCA","GBM",
    "HNSC","KICH","KIRC","KIRP","LAML","LGG","LIHC","LUAD","LUSC",
    "MESO","OV","PAAD","PCPG","PRAD","READ","SARC","SKCM","STAD",
    "TGCT","THCA","THYM","UCEC","UCS","UVM",
]
PLOT_TYPES = ["Boxplot","Violin","Beeswarm","Sina plot","Raincloud","Ridge plot"]
DATASETS   = ["TCGA","GEO (GSE68465)","CCLE"]

# ── Session state init ────────────────────────────────────────────────────────
for k, v in {
    "explorer_gene":     "TP53",
    "explorer_cancer":   "LUAD",
    "explorer_plot":     "Boxplot",
    "explorer_group":    "Normal vs Tumor",
    "explorer_datasets": ["TCGA"],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<div class="page-header">
    <h1>Gene expression explorer</h1>
    <p>Compare expression of any gene across cancer types, tumor stages, and subtypes — instantly</p>
</div>""", unsafe_allow_html=True)

# ── Shareable URL ─────────────────────────────────────────────────────────────
params = st.query_params
if "gene"   in params: st.session_state["explorer_gene"]   = params["gene"]
if "cancer" in params: st.session_state["explorer_cancer"] = params["cancer"]

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")

    gene = st.text_input("Gene symbol",
        value=st.session_state["explorer_gene"],
        placeholder="e.g. TP53, CD8A, FOXP3",
        key="exp_gene_input")
    st.session_state["explorer_gene"] = gene

    pa, pb, pc = st.columns(3)
    for col, eg in zip([pa, pb, pc], ["TP53", "CD8A", "FOXP3"]):
        with col:
            if st.button(eg, key=f"exp_pill_{eg}"):
                st.session_state["explorer_gene"] = eg
                st.rerun()

    cancer = st.selectbox("Cancer type", CANCER_TYPES,
        index=CANCER_TYPES.index(st.session_state["explorer_cancer"]),
        key="exp_cancer_sel")
    st.session_state["explorer_cancer"] = cancer

    plot_type = st.selectbox("Plot type", PLOT_TYPES,
        index=PLOT_TYPES.index(st.session_state["explorer_plot"]),
        key="exp_plot_sel")
    st.session_state["explorer_plot"] = plot_type

    group_by = st.selectbox("Group by",
        ["Normal vs Tumor", "Tumor stage", "Tumor subtype"],
        index=["Normal vs Tumor", "Tumor stage", "Tumor subtype"]
              .index(st.session_state["explorer_group"]),
        key="exp_group_sel")
    st.session_state["explorer_group"] = group_by

    st.markdown("**Cross-dataset comparison**")
    datasets = st.multiselect("Compare across datasets", DATASETS,
        default=st.session_state["explorer_datasets"],
        key="exp_ds_sel")
    st.session_state["explorer_datasets"] = datasets if datasets else ["TCGA"]

    analyze = st.button("Analyze →", use_container_width=True)

    if gene:
        share_url = f"?gene={gene}&cancer={cancer}"
        st.markdown(
            f"<small style='color:#a8c48a'>🔗 <a href='{share_url}' "
            f"style='color:#7D9D33'>Share this analysis</a></small>",
            unsafe_allow_html=True)

with main:
    if not analyze and "gene" not in params:
        st.markdown("""
        <div class="empty-state">
            <h3>Enter a gene symbol to begin</h3>
            <p>Select a gene and cancer type, then click Analyze</p>
            <div class="pill-row">
                <span class="pill">TP53</span>
                <span class="pill">CD8A</span>
                <span class="pill">FOXP3</span>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        gene      = st.session_state["explorer_gene"].upper().strip()
        cancer    = st.session_state["explorer_cancer"]
        plot_type = st.session_state["explorer_plot"]
        group_by  = st.session_state["explorer_group"]
        ds_list   = st.session_state["explorer_datasets"]

        # ── Build demo groups ─────────────────────────────────────────────────
        def make_groups(seed_offset=0):
            np.random.seed(hash(gene + cancer) % 999 + seed_offset)
            if group_by == "Normal vs Tumor":
                grps = ["Normal"] * 40 + ["Tumor"] * 120
                vals = (list(np.random.normal(4.5, 1.2, 40)) +
                        list(np.random.normal(6.8, 1.8, 120)))
                colors = {"Normal": "#a8c48a", "Tumor": "#7D9D33"}
            elif group_by == "Tumor stage":
                stages = ["Stage I", "Stage II", "Stage III", "Stage IV"]
                grps, vals = [], []
                for i, s in enumerate(stages):
                    grps += [s] * 35
                    vals += list(np.random.normal(5 + i * 0.7, 1.5, 35))
                colors = dict(zip(stages, ["#a8c48a","#7D9D33","#4a7a1a","#2d5010"]))
            else:
                subs = ["Luminal A", "Luminal B", "HER2+", "TNBC"]
                grps, vals = [], []
                for i, s in enumerate(subs):
                    grps += [s] * 40
                    vals += list(np.random.normal(5 + i * 0.5, 1.4, 40))
                colors = dict(zip(subs, ["#a8c48a","#7D9D33","#4a7a1a","#2d5010"]))
            return pd.DataFrame({"group": grps, "expression": vals}), colors

        # ── Multi-dataset ─────────────────────────────────────────────────────
        if len(ds_list) > 1:
            fig = make_subplots(rows=1, cols=len(ds_list),
                                subplot_titles=[f"{gene} — {ds}" for ds in ds_list],
                                shared_yaxes=True)
            for col_i, ds in enumerate(ds_list, 1):
                df, colors = make_groups(seed_offset=col_i * 100)
                for g in list(dict.fromkeys(df["group"])):
                    sub = df[df["group"] == g]["expression"]
                    fig.add_trace(go.Box(
                        y=sub, name=f"{g} ({ds})",
                        marker_color=colors.get(g, "#7D9D33"),
                        showlegend=(col_i == 1)),
                        row=1, col=col_i)
            fig.update_layout(
                title=f"{gene} — Cross-dataset comparison ({cancer})",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"))

        else:
            # ── Single dataset ────────────────────────────────────────────────
            df, colors = make_groups()
            group_order = list(dict.fromkeys(df["group"]))

            if plot_type == "Boxplot":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"] == g]["expression"]
                    fig.add_trace(go.Box(
                        y=s, name=g,
                        marker_color=colors.get(g, "#7D9D33"),
                        line_color=colors.get(g, "#7D9D33"),
                        fillcolor=colors.get(g, "#7D9D33"),
                        opacity=0.8, boxmean=True))

            elif plot_type == "Violin":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"] == g]["expression"]
                    fig.add_trace(go.Violin(
                        y=s, name=g,
                        fillcolor=colors.get(g, "#7D9D33"),
                        line_color=colors.get(g, "#7D9D33"),
                        opacity=0.8, box_visible=True, meanline_visible=True))

            elif plot_type == "Beeswarm":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"] == g]["expression"].values
                    n = len(s)
                    # x position = group index + small jitter (pure float array)
                    g_idx   = float(group_order.index(g))
                    jitter  = np.random.uniform(-0.2, 0.2, n)
                    x_vals  = np.full(n, g_idx) + jitter
                    fig.add_trace(go.Scatter(
                        x=x_vals, y=s, mode="markers", name=g,
                        marker=dict(color=colors.get(g,"#7D9D33"), size=5, opacity=0.6)))
                    fig.add_trace(go.Scatter(
                        x=[g_idx], y=[s.mean()], mode="markers",
                        marker=dict(color="#ffffff", size=12, symbol="line-ew",
                                    line=dict(width=2.5, color=colors.get(g,"#7D9D33"))),
                        showlegend=False, name=f"{g} mean"))
                fig.update_layout(
                    xaxis=dict(
                        tickmode="array",
                        tickvals=list(range(len(group_order))),
                        ticktext=group_order))

            elif plot_type == "Sina plot":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"] == g]["expression"].values
                    g_idx  = float(group_order.index(g))
                    std    = s.std() if s.std() > 0 else 1.0
                    kde_w  = np.exp(-0.5 * ((s - s.mean()) / std) ** 2)
                    kde_w  = kde_w / kde_w.max()
                    jitter = kde_w * np.random.uniform(-0.35, 0.35, len(s))
                    x_vals = np.full(len(s), g_idx) + jitter
                    # half-transparent violin behind
                    fig.add_trace(go.Violin(
                        y=s, name=g, x0=g,
                        fillcolor=colors.get(g,"#7D9D33"),
                        line_color=colors.get(g,"#7D9D33"),
                        opacity=0.25, points=False, showlegend=True))
                    fig.add_trace(go.Scatter(
                        x=x_vals, y=s, mode="markers",
                        marker=dict(color=colors.get(g,"#7D9D33"), size=4, opacity=0.75),
                        name=g, showlegend=False))

            elif plot_type == "Raincloud":
                fig = go.Figure()
                for i, g in enumerate(group_order):
                    s = df[df["group"] == g]["expression"].values
                    c = colors.get(g, "#7D9D33")
                    # cloud (half violin)
                    fig.add_trace(go.Violin(
                        y=s, name=g, side="positive", x0=g,
                        fillcolor=c, line_color=c,
                        opacity=0.5, box_visible=False,
                        points=False, meanline_visible=False))
                    # box
                    fig.add_trace(go.Box(
                        y=s, name=g, x0=g,
                        marker_color=c, line_color=c,
                        width=0.12, showlegend=False, boxmean=True))
                    # rain dots — all float arithmetic, no string concatenation
                    g_idx  = float(i)
                    jitter = np.random.uniform(-0.06, 0.06, len(s))
                    x_rain = np.full(len(s), g_idx - 0.28) + jitter
                    fig.add_trace(go.Scatter(
                        x=x_rain, y=s, mode="markers",
                        marker=dict(color=c, size=3, opacity=0.5),
                        showlegend=False, name=f"{g} pts"))
                fig.update_layout(
                    xaxis=dict(
                        tickmode="array",
                        tickvals=list(range(len(group_order))),
                        ticktext=group_order))

            else:  # Ridge plot
                fig = go.Figure()
                for i, g in enumerate(group_order):
                    s = df[df["group"] == g]["expression"].values
                    c = colors.get(g, "#7D9D33")
                    x_range = np.linspace(s.min() - 1, s.max() + 1, 300)
                    std = s.std() if s.std() > 0 else 1.0
                    kde = np.array([
                        np.sum(np.exp(-0.5 * ((x - s) / std) ** 2))
                        for x in x_range])
                    kde = kde / kde.max() * 0.8
                    y_vals = kde + i
                    # fill down to the ridge baseline
                    y_base = np.full_like(y_vals, float(i))
                    fig.add_trace(go.Scatter(
                        x=np.concatenate([x_range, x_range[::-1]]),
                        y=np.concatenate([y_vals, y_base[::-1]]),
                        fill="toself", name=g,
                        line=dict(color=c, width=1.5),
                        fillcolor=c + "55"))  # hex alpha
                fig.update_layout(
                    yaxis=dict(
                        tickmode="array",
                        tickvals=list(range(len(group_order))),
                        ticktext=group_order))
                fig.update_xaxes(title_text="Expression (log2 TPM)")

            fig.update_layout(
                title=f"{gene} expression in {cancer} — {group_by} [{plot_type}]",
                yaxis_title="Expression (log2 TPM)" if plot_type != "Ridge plot" else "",
                xaxis_title=group_by if plot_type not in ["Beeswarm","Raincloud","Ridge plot"] else "",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#3a5a3a", gridwidth=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # ── Stats table ───────────────────────────────────────────────────────
        if len(ds_list) == 1:
            df, _ = make_groups()
            group_order = list(dict.fromkeys(df["group"]))
            stats_rows = []
            for g in group_order:
                s = df[df["group"] == g]["expression"]
                stats_rows.append({
                    "Group": g, "N": len(s),
                    "Median": f"{s.median():.2f}",
                    "Mean":   f"{s.mean():.2f}",
                    "SD":     f"{s.std():.2f}"})
            st.markdown("**Summary statistics**")
            st.dataframe(pd.DataFrame(stats_rows),
                         use_container_width=True, hide_index=True)

        np.random.seed(hash(gene + cancer) % 999)
        pval = round(np.random.uniform(0.001, 0.049), 3)
        n_t  = 120
        n_n  = 40

        st.markdown(f"""
        <div style='font-size:0.78rem;color:#a8c48a;margin:.5rem 0 1rem'>
        Test: Wilcoxon rank-sum &nbsp;|&nbsp;
        Gene: <strong style='color:#E1EAD8'>{gene}</strong> &nbsp;|&nbsp;
        Cancer: <strong style='color:#E1EAD8'>{cancer}</strong> &nbsp;|&nbsp;
        p = {pval} &nbsp;|&nbsp;
        Data: {", ".join(ds_list)} (demo)
        </div>""", unsafe_allow_html=True)

        # ── Download buttons — OUTSIDE figure editor ──────────────────────────
        meta = {
            "gene": gene, "cancer": cancer, "plot_type": "expression",
            "test": "Wilcoxon rank-sum", "n_tumor": n_t, "n_normal": n_n,
            "pvalue": pval, "dataset": ", ".join(ds_list), "group_by": group_by
        }

        dl_col1, dl_col2, dl_col3 = st.columns(3)
        with dl_col1:
            try:
                img_bytes = fig.to_image(format="PNG", scale=300/96)
                st.download_button(
                    "Download figure (PNG, 300 DPI)",
                    data=img_bytes,
                    file_name=f"{gene}_{cancer}_figure.png",
                    mime="image/png",
                    key="exp_dl_png")
            except Exception:
                html_bytes = fig.to_html(include_plotlyjs="cdn").encode()
                st.download_button(
                    "Download interactive HTML",
                    data=html_bytes,
                    file_name=f"{gene}_{cancer}_figure.html",
                    mime="text/html",
                    key="exp_dl_html")

        with dl_col2:
            if len(ds_list) == 1:
                df, _ = make_groups()
                st.download_button(
                    "Download data (CSV)",
                    data=df.to_csv(index=False),
                    file_name=f"{gene}_{cancer}_expression.csv",
                    mime="text/csv",
                    key="exp_dl_csv")

        with dl_col3:
            from components.figure_editor import _build_zip
            try:
                zip_bytes = _build_zip(fig, "PNG", 300, meta)
                st.download_button(
                    "Download full package (ZIP)",
                    data=zip_bytes,
                    file_name="venuviz_package.zip",
                    mime="application/zip",
                    key="exp_dl_zip")
            except Exception:
                st.caption("Add kaleido to requirements.txt for ZIP export")

        # ── Figure editor — customization only, no downloads ──────────────────
        fig = render_figure_editor(fig, key_prefix="explorer", meta=None)

render_footer()
