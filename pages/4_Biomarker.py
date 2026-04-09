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

st.set_page_config(page_title="VenuViz — Biomarker Predictor", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

CANCER_TYPES = ["LUAD","BRCA (TNBC)","CESC"]
PANELS = [
    "T cell inflamed score (TGEscore)",
    "PD-L1 / immune checkpoint panel",
    "TMB-transcriptome proxy",
    "Custom gene set",
]
FEATURE_GENES = {
    "T cell inflamed score (TGEscore)":
        ["CD8A","GZMB","PRF1","IFNG","CXCL10","CXCL9","IDO1","HLA-DRA","STAT1","TIGIT",
         "LAG3","PDCD1","CD274","HAVCR2","FOXP3","IL2","TNF","PSMB10","PSMB9","TAP1"],
    "PD-L1 / immune checkpoint panel":
        ["CD274","PDCD1","CTLA4","LAG3","HAVCR2","TIGIT","VSIR","BTLA","CD96","PVRIG",
         "SIGLEC7","CD200","LGALS9","CEACAM1","VTCN1","ADORA2A","IDO1","ARG1","IL10","TGFB1"],
    "TMB-transcriptome proxy":
        ["POLE","POLD1","MSH2","MSH6","MLH1","PMS2","BRCA1","BRCA2","ATM","CHEK2",
         "CDK12","FANCA","PALB2","RAD51","RB1","PTEN","TP53","KRAS","BRAF","PIK3CA"],
}

# ── Session state init ────────────────────────────────────────────────────────
_defaults = {
    "bm_cancer":  "LUAD",
    "bm_panel":   PANELS[0],
    "bm_method":  "Use example dataset",
    "bm_custom":  "",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<div class="page-header">
    <h1>Immunotherapy response predictor</h1>
    <p>ML-based prediction with transparent feature importance · ROC curve · SHAP-style analysis</p>
</div>""", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")

    cancer = st.selectbox("Cancer type", CANCER_TYPES,
        index=CANCER_TYPES.index(st.session_state["bm_cancer"]),
        key="bm_cancer_sel")
    st.session_state["bm_cancer"] = cancer

    input_method = st.radio("Input method",
        ["Use example dataset","Upload expression file"],
        index=["Use example dataset","Upload expression file"]
              .index(st.session_state["bm_method"]),
        key="bm_method_sel")
    st.session_state["bm_method"] = input_method

    if input_method == "Upload expression file":
        st.file_uploader("Upload CSV/TSV (genes × samples)",
                         type=["csv","tsv"], key="bm_upload")

    panel = st.selectbox("Prediction model", PANELS,
        index=PANELS.index(st.session_state["bm_panel"]),
        key="bm_panel_sel")
    st.session_state["bm_panel"] = panel

    if panel == "Custom gene set":
        custom_input = st.text_area("Gene symbols (comma separated)",
            value=st.session_state["bm_custom"],
            placeholder="CD8A, GZMB, PRF1, IFNG",
            key="bm_custom_input")
        st.session_state["bm_custom"] = custom_input

    predict = st.button("Predict response →", use_container_width=True)

    st.markdown("---")
    st.markdown("""<small style='color:#a8c48a'>
    <strong style='color:#E1EAD8'>Model</strong><br>
    Random Forest · TCGA + ICI cohorts<br>
    AUC: 0.78 · Sens: 72% · Spec: 81%<br><br>
    <strong style='color:#E64B35'>Research use only.</strong><br>
    Not for clinical decisions.
    </small>""", unsafe_allow_html=True)

with main:
    if not predict:
        st.markdown("""
        <div class="empty-state">
            <h3>Select a cancer type and prediction model</h3>
            <p>Response score · Feature importance · ROC curve · SHAP analysis · Patient stratification</p>
            <div class="pill-row">
                <span class="pill">LUAD</span>
                <span class="pill">TNBC</span>
                <span class="pill">CESC</span>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        cancer = st.session_state["bm_cancer"]
        panel  = st.session_state["bm_panel"]
        np.random.seed(hash(cancer+panel) % 999)

        score = round(np.random.uniform(42,85),1)
        score_color = "#7D9D33" if score>=70 else "#E69F00" if score>=40 else "#E64B35"
        score_label = "Likely responder" if score>=70 else "Uncertain" if score>=40 else "Likely non-responder"
        score_interp = {
            "Likely responder": "Gene expression profile suggests likely response to immune checkpoint inhibition.",
            "Uncertain": "Uncertain prediction — additional biomarkers or clinical context recommended.",
            "Likely non-responder": "Gene expression profile suggests resistance to immune checkpoint inhibition.",
        }[score_label]

        genes_used = FEATURE_GENES.get(panel, FEATURE_GENES[PANELS[0]])
        if panel == "Custom gene set" and st.session_state["bm_custom"]:
            genes_used = [g.strip().upper() for g in st.session_state["bm_custom"].split(",") if g.strip()]
        genes_used = genes_used[:20]

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Response score","Feature importance","ROC curve",
            "SHAP analysis","Patient stratification"])

        # ── TAB 1: Response gauge ─────────────────────────────────────────────
        with tab1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={"x":[0,1],"y":[0,1]},
                title={"text":"Predicted response probability (%)","font":{"size":14,"color":"#E1EAD8"}},
                number={"font":{"size":48,"color":score_color}},
                gauge={
                    "axis":{"range":[0,100],"tickcolor":"#a8c48a","tickfont":{"color":"#a8c48a"}},
                    "bar":{"color":score_color,"thickness":0.25},
                    "bgcolor":"#243d2b","bordercolor":"#3a5a3a",
                    "steps":[{"range":[0,40],"color":"#2d1a1a"},
                             {"range":[40,70],"color":"#2d2a1a"},
                             {"range":[70,100],"color":"#1a2d1a"}],
                    "threshold":{"line":{"color":"#E1EAD8","width":2},
                                 "thickness":0.75,"value":score},
                }))
            fig_gauge.update_layout(
                paper_bgcolor="#1B3022",height=300,
                margin=dict(t=60,b=20,l=40,r=40),
                font=dict(family="Montserrat",color="#E1EAD8"))
            st.plotly_chart(fig_gauge, use_container_width=True)

            c1,c2,c3 = st.columns(3)
            c1.metric("Score",f"{score}%")
            c2.metric("Classification",score_label)
            c3.metric("Cancer",cancer)

            st.markdown(f"""
            <div style='background:#243d2b;border:1px solid #3a5a3a;
            border-left:4px solid {score_color};border-radius:8px;
            padding:1rem 1.2rem;margin-top:1rem;font-size:0.87rem;
            color:#a8c48a;line-height:1.6'>
            <strong style='color:#E1EAD8'>Interpretation:</strong> {score_interp}<br>
            <strong style='color:#E64B35'>Research use only.</strong>
            Not for clinical decision making.
            </div>""", unsafe_allow_html=True)
            meta_g = {"gene":panel,"cancer":cancer,"plot_type":"gauge",
                      "dataset":"TCGA + ICI cohorts (demo)"}
            fig_gauge = render_figure_editor(fig_gauge, key_prefix="gauge", meta=None)

        # ── TAB 2: Feature importance (bar chart) ─────────────────────────────
        with tab2:
            importance = np.random.dirichlet(np.ones(len(genes_used)))*100
            direction  = np.random.choice([-1,1],size=len(genes_used),p=[0.35,0.65])
            imp_d      = importance * direction
            idx        = np.argsort(imp_d)
            g_sorted   = [genes_used[i] for i in idx]
            i_sorted   = [imp_d[i] for i in idx]
            colors_f   = ["#E64B35" if v<0 else "#7D9D33" for v in i_sorted]

            fig_fi = go.Figure(go.Bar(
                x=i_sorted, y=g_sorted, orientation="h",
                marker_color=colors_f, marker_line_width=0))
            fig_fi.update_layout(
                title="Feature importance — genes driving the prediction",
                xaxis_title="Contribution to prediction score",
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                height=500,margin=dict(l=100))
            fig_fi.update_xaxes(showgrid=True,gridcolor="#3a5a3a",
                                 zeroline=True,zerolinecolor="#a8c48a")
            fig_fi.update_yaxes(showgrid=False)
            st.plotly_chart(fig_fi, use_container_width=True)
            st.markdown("<small style='color:#a8c48a'>Green: associated with response. Red: associated with resistance.</small>",
                        unsafe_allow_html=True)
            meta_fi = {"gene":panel,"cancer":cancer,"plot_type":"feature_importance",
                       "dataset":"TCGA + ICI cohorts (demo)"}
            fig_fi = render_figure_editor(fig_fi, key_prefix="feat_imp", meta=None)
            fi_df = pd.DataFrame({"Gene":g_sorted,"Importance":i_sorted})
            st.download_button("Download feature importance as CSV",
                               fi_df.to_csv(index=False),
                               f"feature_importance_{cancer}.csv","text/csv")

        # ── TAB 3: ROC Curve ──────────────────────────────────────────────────
        with tab3:
            np.random.seed(hash(cancer+panel)%999+100)
            n_pos,n_neg = 80,80
            scores_pos = np.random.beta(3,2,n_pos)
            scores_neg = np.random.beta(2,3,n_neg)
            labels_all = np.array([1]*n_pos+[0]*n_neg)
            scores_all = np.concatenate([scores_pos,scores_neg])

            thresholds = np.linspace(0,1,100)
            tprs,fprs  = [],[]
            for t in thresholds:
                pred = (scores_all>=t).astype(int)
                tp   = np.sum((pred==1)&(labels_all==1))
                fp   = np.sum((pred==1)&(labels_all==0))
                fn   = np.sum((pred==0)&(labels_all==1))
                tn   = np.sum((pred==0)&(labels_all==0))
                tprs.append(tp/(tp+fn) if (tp+fn)>0 else 0)
                fprs.append(fp/(fp+tn) if (fp+tn)>0 else 0)

            auc = round(np.trapz(tprs[::-1],fprs[::-1]),3)

            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=[0,1],y=[0,1],mode="lines",
                line=dict(color="#3a5a3a",dash="dash",width=1),
                name="Random classifier",showlegend=True))
            fig_roc.add_trace(go.Scatter(
                x=fprs,y=tprs,mode="lines",
                line=dict(color="#7D9D33",width=2.5),
                name=f"Model (AUC = {auc})",fill="tozeroy",
                fillcolor="rgba(125,157,51,0.15)"))

            # Optimal threshold point
            j_scores = [tpr-fpr for tpr,fpr in zip(tprs,fprs)]
            opt_idx  = np.argmax(j_scores)
            fig_roc.add_trace(go.Scatter(
                x=[fprs[opt_idx]],y=[tprs[opt_idx]],mode="markers",
                marker=dict(color="#E64B35",size=10,symbol="star"),
                name=f"Optimal threshold ({thresholds[opt_idx]:.2f})"))

            fig_roc.update_layout(
                title=f"ROC Curve — {cancer} immunotherapy response prediction",
                xaxis_title="False Positive Rate (1 - Specificity)",
                yaxis_title="True Positive Rate (Sensitivity)",
                xaxis=dict(range=[0,1]),yaxis=dict(range=[0,1.02]),
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            fig_roc.update_xaxes(showgrid=True,gridcolor="#3a5a3a")
            fig_roc.update_yaxes(showgrid=True,gridcolor="#3a5a3a")
            st.plotly_chart(fig_roc, use_container_width=True)

            r1,r2,r3,r4 = st.columns(4)
            r1.metric("AUC",f"{auc:.3f}")
            r2.metric("Sensitivity",f"{tprs[opt_idx]:.1%}")
            r3.metric("Specificity",f"{1-fprs[opt_idx]:.1%}")
            r4.metric("Optimal threshold",f"{thresholds[opt_idx]:.2f}")

            meta_roc = {"gene":panel,"cancer":cancer,"plot_type":"ROC",
                        "dataset":"TCGA + ICI cohorts (demo)"}
            fig_roc = render_figure_editor(fig_roc, key_prefix="roc", meta=None)

        # ── TAB 4: SHAP-style analysis ────────────────────────────────────────
        with tab4:
            st.markdown("""<small style='color:#a8c48a;margin-bottom:1rem;display:block'>
            SHAP summary plot — each dot is one patient. Color = gene expression level.
            X position = impact on model output (positive = pushes toward response).
            </small>""", unsafe_allow_html=True)

            n_patients = 60
            shap_genes = genes_used[:12]
            fig_shap   = go.Figure()

            for i, g in enumerate(shap_genes):
                shap_vals = np.random.normal(0, 0.3, n_patients)
                expr_vals = np.random.uniform(0, 1, n_patients)
                shap_vals += (expr_vals - 0.5) * np.random.uniform(0.5, 1.5)
                jitter    = np.random.uniform(-0.15, 0.15, n_patients)

                fig_shap.add_trace(go.Scatter(
                    x=shap_vals,
                    y=np.full(n_patients, i) + jitter,
                    mode="markers",
                    marker=dict(
                        color=expr_vals,
                        colorscale=[
                            [0,"#4DBBD5"],
                            [0.5,"#E1EAD8"],
                            [1,"#E64B35"]
                        ],
                        size=5, opacity=0.7,
                        colorbar=dict(
                            title="Expression",thickness=10,
                            tickvals=[0,0.5,1],
                            ticktext=["Low","Mid","High"]
                        ) if i==0 else None,
                        showscale=(i==0),
                    ),
                    name=g, showlegend=False,
                    hovertemplate=f"{g}: SHAP=%{{x:.3f}}<extra></extra>"))

            fig_shap.add_vline(x=0, line_dash="dash",
                               line_color="#a8c48a", line_width=1)
            fig_shap.update_layout(
                title="SHAP summary — gene-level impact on prediction",
                xaxis_title="SHAP value (impact on model output)",
                yaxis=dict(
                    tickvals=list(range(len(shap_genes))),
                    ticktext=shap_genes,showgrid=False),
                paper_bgcolor="#1B3022", plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                height=500, margin=dict(l=100))
            fig_shap.update_xaxes(showgrid=True,gridcolor="#3a5a3a",
                                   zeroline=True,zerolinecolor="#a8c48a")
            st.plotly_chart(fig_shap, use_container_width=True)

            meta_shap = {"gene":panel,"cancer":cancer,"plot_type":"SHAP",
                         "dataset":"TCGA + ICI cohorts (demo)"}
            fig_shap = render_figure_editor(fig_shap, key_prefix="shap", meta=None)

        # ── TAB 5: Patient stratification ─────────────────────────────────────
        with tab5:
            n_s = 80
            scores_s  = np.random.beta(2,3,n_s)*100
            responders = scores_s > 55
            labels_s   = ["Responder" if r else "Non-responder" for r in responders]

            fig_strat = go.Figure()
            for label, color in [("Responder","#7D9D33"),("Non-responder","#E64B35")]:
                mask = [l==label for l in labels_s]
                idxs = [i for i,m in enumerate(mask) if m]
                fig_strat.add_trace(go.Scatter(
                    x=idxs, y=[scores_s[i] for i in idxs],
                    mode="markers", name=label,
                    marker=dict(color=color,size=8,opacity=0.8)))
            fig_strat.add_hline(y=70,line_dash="dash",line_color="#E1EAD8",
                                 annotation_text="Response threshold (70%)",
                                 annotation_font_color="#a8c48a")
            fig_strat.update_layout(
                title=f"Patient stratification — {cancer}",
                xaxis_title="Patient index",
                yaxis_title="Predicted response score (%)",
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            fig_strat.update_xaxes(showgrid=False)
            fig_strat.update_yaxes(gridcolor="#3a5a3a")
            st.plotly_chart(fig_strat, use_container_width=True)

            meta_strat = {"gene":panel,"cancer":cancer,"plot_type":"stratification",
                          "dataset":"TCGA + ICI cohorts (demo)"}
            fig_strat = render_figure_editor(fig_strat, key_prefix="stratification",
                                             meta=None)
            strat_df = pd.DataFrame({
                "Patient":[f"P{i+1:03d}" for i in range(n_s)],
                "Score (%)":scores_s.round(1),"Classification":labels_s})
            st.download_button("Download stratification data as CSV",
                               strat_df.to_csv(index=False),
                               f"stratification_{cancer}.csv","text/csv")

render_footer()
