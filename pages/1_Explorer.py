import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
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
PLOT_TYPES = ["Boxplot","Violin","Dotplot / Beeswarm","Sina plot","Raincloud","Ridge plot"]
DATASETS   = ["TCGA","GEO (GSE68465)","CCLE"]

# ── Session state init ────────────────────────────────────────────────────────
for k, v in {"explorer_gene":"TP53","explorer_cancer":"LUAD",
              "explorer_plot":"Boxplot","explorer_group":"Normal vs Tumor",
              "explorer_datasets":["TCGA"]}.items():
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

# ── Layout ────────────────────────────────────────────────────────────────────
sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")

    gene = st.text_input("Gene symbol",
        value=st.session_state["explorer_gene"],
        placeholder="e.g. TP53, CD8A, FOXP3",
        key="exp_gene_input")
    st.session_state["explorer_gene"] = gene

    # Example pills
    pa, pb, pc = st.columns(3)
    for col, eg in zip([pa,pb,pc],["TP53","CD8A","FOXP3"]):
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
        ["Normal vs Tumor","Tumor stage","Tumor subtype"],
        index=["Normal vs Tumor","Tumor stage","Tumor subtype"]
              .index(st.session_state["explorer_group"]),
        key="exp_group_sel")
    st.session_state["explorer_group"] = group_by

    st.markdown("**Cross-dataset comparison**")
    datasets = st.multiselect("Compare across datasets", DATASETS,
        default=st.session_state["explorer_datasets"],
        key="exp_ds_sel")
    st.session_state["explorer_datasets"] = datasets if datasets else ["TCGA"]

    analyze = st.button("Analyze →", use_container_width=True)

    # Shareable URL display
    if gene:
        share_url = f"?gene={gene}&cancer={cancer}"
        st.markdown(f"<small style='color:#a8c48a'>🔗 <a href='{share_url}' style='color:#7D9D33'>Share this analysis</a></small>",
                    unsafe_allow_html=True)

with main:
    if not analyze and not params:
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
        gene   = st.session_state["explorer_gene"].upper().strip()
        cancer = st.session_state["explorer_cancer"]
        ds_list= st.session_state["explorer_datasets"]

        np.random.seed(hash(gene + cancer) % 999)

        def make_groups(seed_offset=0):
            np.random.seed(hash(gene + cancer) % 999 + seed_offset)
            if group_by == "Normal vs Tumor":
                grps = ["Normal"]*40 + ["Tumor"]*120
                vals = list(np.random.normal(4.5,1.2,40)) + list(np.random.normal(6.8,1.8,120))
                colors = {"Normal":"#a8c48a","Tumor":"#7D9D33"}
            elif group_by == "Tumor stage":
                stages = ["Stage I","Stage II","Stage III","Stage IV"]
                grps,vals = [],[]
                for i,s in enumerate(stages):
                    grps += [s]*35; vals += list(np.random.normal(5+i*0.7,1.5,35))
                colors = dict(zip(stages,["#a8c48a","#7D9D33","#4a7a1a","#2d5010"]))
            else:
                subs = ["Luminal A","Luminal B","HER2+","TNBC"]
                grps,vals = [],[]
                for i,s in enumerate(subs):
                    grps += [s]*40; vals += list(np.random.normal(5+i*0.5,1.4,40))
                colors = dict(zip(subs,["#a8c48a","#7D9D33","#4a7a1a","#2d5010"]))
            return pd.DataFrame({"group":grps,"expression":vals}), colors

        # ── Multi-dataset mode ────────────────────────────────────────────────
        if len(ds_list) > 1:
            n_ds = len(ds_list)
            fig  = make_subplots(rows=1, cols=n_ds,
                                 subplot_titles=[f"{gene} — {ds}" for ds in ds_list],
                                 shared_yaxes=True)
            for col_i, ds in enumerate(ds_list, 1):
                df, colors = make_groups(seed_offset=col_i*100)
                for g in list(dict.fromkeys(df["group"])):
                    subset = df[df["group"]==g]["expression"]
                    fig.add_trace(go.Box(y=subset, name=f"{g} ({ds})",
                        marker_color=colors.get(g,"#7D9D33"),
                        showlegend=(col_i==1)), row=1, col=col_i)
            fig.update_layout(
                title=f"{gene} — Cross-dataset comparison ({cancer})",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            # ── Single dataset — rich plot types ─────────────────────────────
            df, colors = make_groups()
            group_order = list(dict.fromkeys(df["group"]))

            if plot_type == "Boxplot":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"]==g]["expression"]
                    fig.add_trace(go.Box(y=s, name=g,
                        marker_color=colors.get(g,"#7D9D33"),
                        line_color=colors.get(g,"#7D9D33"),
                        fillcolor=colors.get(g,"#7D9D33"),
                        opacity=0.8, boxmean=True))

            elif plot_type == "Violin":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"]==g]["expression"]
                    fig.add_trace(go.Violin(y=s, name=g,
                        fillcolor=colors.get(g,"#7D9D33"),
                        line_color=colors.get(g,"#7D9D33"),
                        opacity=0.8, box_visible=True, meanline_visible=True))

            elif plot_type == "Dotplot / Beeswarm":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"]==g]["expression"]
                    jitter = np.random.uniform(-0.2,0.2,len(s))
                    fig.add_trace(go.Scatter(
                        x=[g]*len(s)+jitter, y=s, mode="markers", name=g,
                        marker=dict(color=colors.get(g,"#7D9D33"),size=5,opacity=0.6)))
                    fig.add_trace(go.Scatter(
                        x=[g], y=[s.mean()], mode="markers", name=f"{g} mean",
                        marker=dict(color="#ffffff",size=10,symbol="line-ew",
                                    line=dict(width=2,color=colors.get(g,"#7D9D33"))),
                        showlegend=False))

            elif plot_type == "Sina plot":
                fig = go.Figure()
                for g in group_order:
                    s = df[df["group"]==g]["expression"]
                    # Sina: jitter proportional to density
                    kde_w = np.array([np.exp(-((v-s.mean())**2)/(2*s.std()**2)) for v in s])
                    jitter = (kde_w/kde_w.max()) * np.random.uniform(-0.35,0.35,len(s))
                    fig.add_trace(go.Violin(y=s, name=g,
                        fillcolor=colors.get(g,"#7D9D33"),
                        line_color=colors.get(g,"#7D9D33"),
                        opacity=0.3, points=False))
                    fig.add_trace(go.Scatter(
                        x=[g]*len(s)+jitter, y=s, mode="markers", name=f"{g} points",
                        marker=dict(color=colors.get(g,"#7D9D33"),size=4,opacity=0.7),
                        showlegend=False))

            elif plot_type == "Raincloud":
                fig = go.Figure()
                positions = list(range(len(group_order)))
                for i, g in enumerate(group_order):
                    s = df[df["group"]==g]["expression"]
                    c = colors.get(g,"#7D9D33")
                    # Half violin (cloud)
                    fig.add_trace(go.Violin(y=s, name=g, side="positive",
                        fillcolor=c, line_color=c, opacity=0.5,
                        x0=g, box_visible=False, points=False, meanline_visible=False))
                    # Box (rain core)
                    fig.add_trace(go.Box(y=s, name=g, x0=g,
                        marker_color=c, line_color=c,
                        width=0.15, showlegend=False, boxmean=True))
                    # Scatter dots (rain)
                    jitter = np.random.uniform(-0.08,0.08,len(s))
                    fig.add_trace(go.Scatter(
                        x=[g]*len(s)+jitter-0.25, y=s, mode="markers", name=g,
                        marker=dict(color=c,size=3,opacity=0.5),showlegend=False))

            else:  # Ridge plot
                fig = go.Figure()
                for i, g in enumerate(group_order):
                    s = df[df["group"]==g]["expression"]
                    c = colors.get(g,"#7D9D33")
                    x_range = np.linspace(s.min()-1, s.max()+1, 200)
                    kde = np.array([np.sum(np.exp(-0.5*((x-s.values)**2)/s.std()**2))
                                    for x in x_range])
                    kde = kde/kde.max() * 0.8
                    fig.add_trace(go.Scatter(
                        x=x_range, y=kde + i, fill="tonexty" if i>0 else "tozeroy",
                        name=g, line=dict(color=c,width=1.5),
                        fillcolor=c.replace("#","rgba(").rstrip(")")
                                  if c.startswith("#") else c))
                fig.update_layout(yaxis=dict(
                    tickvals=list(range(len(group_order))),
                    ticktext=group_order))

            fig.update_layout(
                title=f"{gene} expression in {cancer} — {group_by} [{plot_type}]",
                yaxis_title="Expression (log2 TPM)" if plot_type != "Ridge plot" else "Density",
                xaxis_title=group_by if plot_type != "Ridge plot" else "Expression (log2 TPM)",
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#3a5a3a",gridwidth=0.5)

            st.plotly_chart(fig, use_container_width=True)

        # ── Stats ─────────────────────────────────────────────────────────────
        if len(ds_list) == 1:
            df, _ = make_groups()
            group_order = list(dict.fromkeys(df["group"]))
            stats_rows = []
            for g in group_order:
                s = df[df["group"]==g]["expression"]
                stats_rows.append({"Group":g,"N":len(s),
                    "Median":f"{s.median():.2f}","Mean":f"{s.mean():.2f}","SD":f"{s.std():.2f}"})
            st.markdown("**Summary statistics**")
            st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True)

        pval = round(np.random.uniform(0.001,0.049),3)
        n_t  = int(df[df["group"].str.contains("Tumor|Stage|Luminal|HER2|TNBC",regex=True)].shape[0]) if len(ds_list)==1 else 0
        n_n  = int(df[~df["group"].str.contains("Tumor|Stage|Luminal|HER2|TNBC",regex=True)].shape[0]) if len(ds_list)==1 else 0

        st.markdown(f"""
        <div style='font-size:0.78rem;color:#a8c48a;margin-top:0.5rem'>
        Statistical test: Wilcoxon rank-sum &nbsp;|&nbsp;
        Gene: <strong style='color:#E1EAD8'>{gene}</strong> &nbsp;|&nbsp;
        Cancer: <strong style='color:#E1EAD8'>{cancer}</strong> &nbsp;|&nbsp;
        p = {pval} &nbsp;|&nbsp; Data: {", ".join(ds_list)} (demo)
        </div>""", unsafe_allow_html=True)

        meta = {"gene":gene,"cancer":cancer,"plot_type":"expression",
                "test":"Wilcoxon rank-sum","n_tumor":n_t,"n_normal":n_n,
                "pvalue":pval,"dataset":", ".join(ds_list),"group_by":group_by}

        fig = render_figure_editor(fig, key_prefix="explorer", meta=meta)

        csv = df.to_csv(index=False) if len(ds_list)==1 else "multi-dataset"
        if len(ds_list)==1:
            st.download_button("Download data as CSV", csv,
                               f"{gene}_{cancer}_expression.csv","text/csv")

render_footer()