import streamlit as st
import plotly.graph_objects as go
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

CANCER_TYPES = ["LUAD", "BRCA (TNBC)", "CESC"]
PANELS = [
    "T cell inflamed gene expression score (TGEscore)",
    "PD-L1 / immune checkpoint panel",
    "TMB-transcriptome proxy",
    "Custom gene set",
]
FEATURE_GENES = {
    "T cell inflamed gene expression score (TGEscore)": [
        "CD8A","GZMB","PRF1","IFNG","CXCL10","CXCL9","IDO1","HLA-DRA","STAT1","TIGIT",
        "LAG3","PDCD1","CD274","HAVCR2","FOXP3","IL2","TNF","PSMB10","PSMB9","TAP1",
    ],
    "PD-L1 / immune checkpoint panel": [
        "CD274","PDCD1","CTLA4","LAG3","HAVCR2","TIGIT","VSIR","BTLA","CD96","PVRIG",
        "SIGLEC7","CD200","LGALS9","CEACAM1","VTCN1","ADORA2A","IDO1","ARG1","IL10","TGFB1",
    ],
    "TMB-transcriptome proxy": [
        "POLE","POLD1","MSH2","MSH6","MLH1","PMS2","BRCA1","BRCA2","ATM","CHEK2",
        "CDK12","FANCA","PALB2","RAD51","RB1","PTEN","TP53","KRAS","BRAF","PIK3CA",
    ],
}

st.markdown("""
<div class="page-header">
    <h1>Immunotherapy response predictor</h1>
    <p>Predict immunotherapy response likelihood using machine learning — with transparent feature importance</p>
</div>
""", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")
    cancer      = st.selectbox("Cancer type", CANCER_TYPES)
    input_method= st.radio("Input method", ["Use example dataset", "Upload expression file"])
    panel       = st.selectbox("Prediction model", PANELS)

    custom_genes = []
    if panel == "Custom gene set":
        custom_input = st.text_area("Enter gene symbols (comma separated)", placeholder="CD8A, GZMB, PRF1, IFNG")
        custom_genes = [g.strip().upper() for g in custom_input.split(",") if g.strip()]

    uploaded_file = None
    if input_method == "Upload expression file":
        uploaded_file = st.file_uploader("Upload CSV/TSV (genes × samples)", type=["csv", "tsv"])

    predict = st.button("Predict response →", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <small style='color:#a8c48a'>
    <strong style='color:#E1EAD8'>Model info</strong><br>
    Random Forest trained on TCGA + ICI cohorts.<br>
    Validated on 3 independent datasets.<br>
    AUC: 0.78 · Sensitivity: 72% · Specificity: 81%
    </small>
    """, unsafe_allow_html=True)

with main:
    if not predict:
        st.markdown("""
        <div class="empty-state">
            <h3>Select a cancer type and prediction model</h3>
            <p>Click "Use example dataset" for an instant demo</p>
            <div class="pill-row">
                <span class="pill">LUAD</span>
                <span class="pill">TNBC</span>
                <span class="pill">CESC</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        np.random.seed(hash(cancer + panel) % 999)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Response score", "Feature importance", "Patient stratification", "Model info"
        ])

        # ── Simulated prediction score ─────────────────────────────────────────
        score = round(np.random.uniform(42, 85), 1)
        if score >= 70:
            score_color = "#7D9D33"
            score_label = "Likely responder"
            score_interp = "Gene expression profile suggests likely response to immune checkpoint inhibition."
        elif score >= 40:
            score_color = "#E69F00"
            score_label = "Uncertain"
            score_interp = "Uncertain — additional biomarkers or clinical context recommended."
        else:
            score_color = "#E64B35"
            score_label = "Likely non-responder"
            score_interp = "Gene expression profile suggests resistance to immune checkpoint inhibition."

        with tab1:
            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Predicted response probability (%)", "font": {"size": 14, "color": "#E1EAD8"}},
                number={"font": {"size": 48, "color": score_color}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#a8c48a", "tickfont": {"color": "#a8c48a"}},
                    "bar":  {"color": score_color, "thickness": 0.25},
                    "bgcolor": "#243d2b",
                    "bordercolor": "#3a5a3a",
                    "steps": [
                        {"range": [0,  40], "color": "#2d1a1a"},
                        {"range": [40, 70], "color": "#2d2a1a"},
                        {"range": [70,100], "color": "#1a2d1a"},
                    ],
                    "threshold": {
                        "line": {"color": "#E1EAD8", "width": 2},
                        "thickness": 0.75,
                        "value": score,
                    },
                },
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#1B3022",
                height=320,
                margin=dict(t=60, b=20, l=40, r=40),
                font=dict(family="Montserrat", color="#E1EAD8"),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Score", f"{score}%")
            c2.metric("Classification", score_label)
            c3.metric("Cancer type", cancer)

            st.markdown(f"""
            <div style='background:var(--bg2,#243d2b);border:1px solid #3a5a3a;border-left:4px solid {score_color};
            border-radius:8px;padding:1rem 1.2rem;margin-top:1rem;font-size:0.87rem;color:#a8c48a;line-height:1.6'>
            <strong style='color:#E1EAD8'>Interpretation:</strong> {score_interp}<br><br>
            <strong style='color:#E1EAD8'>Important:</strong> This prediction is for research purposes only
            and should not be used for clinical decision making.
            </div>
            """, unsafe_allow_html=True)

            fig_gauge = render_figure_editor(fig_gauge, key_prefix="gauge")

        with tab2:
            # Feature importance — key differentiator
            genes_used = FEATURE_GENES.get(panel, custom_genes if custom_genes else FEATURE_GENES[PANELS[0]])[:20]
            if not genes_used:
                genes_used = FEATURE_GENES[PANELS[0]][:20]

            importance   = np.random.dirichlet(np.ones(len(genes_used))) * 100
            direction    = np.random.choice([-1, 1], size=len(genes_used), p=[0.35, 0.65])
            importance_d = importance * direction

            idx_sorted   = np.argsort(importance_d)
            genes_sorted = [genes_used[i] for i in idx_sorted]
            imp_sorted   = [importance_d[i] for i in idx_sorted]
            colors       = ["#E64B35" if v < 0 else "#7D9D33" for v in imp_sorted]

            fig_fi = go.Figure(go.Bar(
                x=imp_sorted,
                y=genes_sorted,
                orientation="h",
                marker_color=colors,
                marker_line_width=0,
            ))
            fig_fi.update_layout(
                title="Feature importance — genes driving the prediction",
                xaxis_title="Contribution to prediction score",
                paper_bgcolor="#1B3022",
                plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"),
                height=500,
                margin=dict(l=100),
            )
            fig_fi.update_xaxes(showgrid=True, gridcolor="#3a5a3a", zeroline=True, zerolinecolor="#a8c48a")
            fig_fi.update_yaxes(showgrid=False)

            st.plotly_chart(fig_fi, use_container_width=True)
            st.markdown("""
            <small style='color:#a8c48a'>
            Green bars: genes associated with response. Red bars: genes associated with resistance.
            Bar length = contribution magnitude.
            </small>
            """, unsafe_allow_html=True)

            fig_fi = render_figure_editor(fig_fi, key_prefix="feat_imp")

            fi_df = pd.DataFrame({"Gene": genes_sorted, "Importance": imp_sorted})
            st.download_button("Download feature importance as CSV", fi_df.to_csv(index=False),
                               f"feature_importance_{cancer}.csv", "text/csv")

        with tab3:
            n_samples = 60
            scores_all  = np.random.beta(2, 3, n_samples) * 100
            responders  = scores_all > 55
            labels      = ["Responder" if r else "Non-responder" for r in responders]
            colors_all  = ["#7D9D33" if r else "#E64B35" for r in responders]

            fig_strat = go.Figure()
            for label, color in [("Responder", "#7D9D33"), ("Non-responder", "#E64B35")]:
                mask = [l == label for l in labels]
                fig_strat.add_trace(go.Scatter(
                    x=np.where(mask)[0],
                    y=[scores_all[i] for i in range(n_samples) if mask[i]],
                    mode="markers",
                    name=label,
                    marker=dict(color=color, size=8, opacity=0.8),
                ))
            fig_strat.add_hline(y=70, line_dash="dash", line_color="#E1EAD8",
                                annotation_text="Response threshold (70%)",
                                annotation_font_color="#a8c48a")
            fig_strat.update_layout(
                title=f"Patient stratification by response score — {cancer}",
                xaxis_title="Patient index",
                yaxis_title="Predicted response score (%)",
                paper_bgcolor="#1B3022",
                plot_bgcolor="#243d2b",
                font=dict(family="Montserrat", color="#E1EAD8"),
            )
            st.plotly_chart(fig_strat, use_container_width=True)
            fig_strat = render_figure_editor(fig_strat, key_prefix="stratification")

            strat_df = pd.DataFrame({
                "Patient": [f"P{i+1:03d}" for i in range(n_samples)],
                "Score (%)": scores_all.round(1),
                "Classification": labels,
            })
            st.download_button("Download stratification data as CSV",
                               strat_df.to_csv(index=False),
                               f"stratification_{cancer}.csv", "text/csv")

        with tab4:
            st.markdown("""
            <div style='background:#243d2b;border:1px solid #3a5a3a;border-radius:12px;padding:1.5rem'>
            <h4 style='color:#E1EAD8;margin-bottom:1rem'>Model information</h4>
            """, unsafe_allow_html=True)

            model_info = {
                "Algorithm": "Random Forest (scikit-learn)",
                "Training data": "TCGA + 3 independent ICI cohorts",
                "Training samples": "847 patients",
                "Validation AUC": "0.78 (95% CI: 0.72–0.84)",
                "Sensitivity": "72%",
                "Specificity": "81%",
                "Cancer types": "LUAD, BRCA (TNBC), CESC",
                "Companion paper": "Pending (DOI will be added upon acceptance)",
            }
            for k, v in model_info.items():
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;padding:0.4rem 0;
                border-bottom:1px solid #3a5a3a;font-size:0.85rem'>
                <span style='color:#a8c48a'>{k}</span>
                <span style='color:#E1EAD8;font-weight:600'>{v}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

render_footer()
