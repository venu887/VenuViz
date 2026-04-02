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

st.set_page_config(page_title="VenuViz — Survival Analysis", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

CANCER_TYPES = [
    "ACC","BLCA","BRCA","CESC","CHOL","COAD","DLBC","ESCA","GBM",
    "HNSC","KICH","KIRC","KIRP","LAML","LGG","LIHC","LUAD","LUSC",
    "MESO","OV","PAAD","PCPG","PRAD","READ","SARC","SKCM","STAD",
    "TGCT","THCA","THYM","UCEC","UCS","UVM",
]

st.markdown("""
<div class="page-header">
    <h1>Survival analysis</h1>
    <p>Generate Kaplan-Meier survival curves stratified by gene expression — with one-click publication export</p>
</div>
""", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")
    gene     = st.text_input("Gene symbol", value="CD8A", placeholder="e.g. CD8A, FOXP3, TP53")
    cancer   = st.selectbox("Cancer type", CANCER_TYPES, index=CANCER_TYPES.index("LUAD"))
    surv_type= st.selectbox("Survival endpoint", ["Overall survival (OS)", "Disease-free survival (DFS)", "Progression-free survival (PFS)", "Disease-specific survival (DSS)"])
    cutoff   = st.selectbox("Stratification cutoff", ["Median", "Upper/lower quartile", "Optimal cutoff"])
    max_fu   = st.slider("Max follow-up (months)", 12, 120, 60, step=6)
    generate = st.button("Generate curve →", use_container_width=True)

    st.markdown("---")
    st.markdown("<small style='color:#a8c48a'>**How to interpret:**<br>p-value: strength of association.<br>HR>1: high expression = worse survival.<br>HR<1: high expression = protective.</small>", unsafe_allow_html=True)

with main:
    if not generate:
        st.markdown("""
        <div class="empty-state">
            <h3>Enter a gene symbol and cancer type</h3>
            <p>Generate a Kaplan-Meier survival curve stratified by gene expression</p>
            <div class="pill-row">
                <span class="pill">CD8A</span>
                <span class="pill">FOXP3</span>
                <span class="pill">TP53</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        gene = gene.upper().strip()
        np.random.seed(hash(gene + cancer) % 999)

        # ── Simulate KM data ──────────────────────────────────────────────────
        def simulate_km(n, median_surv, max_t):
            times = np.random.exponential(median_surv, n)
            times = np.clip(times, 0, max_t)
            events = (times < max_t).astype(int)
            return np.sort(times), events

        n_high, n_low = 80, 80
        t_high, e_high = simulate_km(n_high, median_surv=38, max_t=max_fu)
        t_low,  e_low  = simulate_km(n_low,  median_surv=22, max_t=max_fu)

        def km_curve(times, events):
            unique_t = np.unique(times[events == 1])
            survival = [1.0]
            at_risk  = len(times)
            t_plot   = [0]
            for t in unique_t:
                d = np.sum((times == t) & (events == 1))
                survival.append(survival[-1] * (1 - d / at_risk))
                at_risk -= np.sum(times <= t)
                t_plot.append(t)
            return t_plot, survival

        t_h, s_h = km_curve(t_high, e_high)
        t_l, s_l = km_curve(t_low,  e_low)

        # ── KM figure ─────────────────────────────────────────────────────────
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_h, y=s_h, mode="lines", name=f"High {gene}  (n={n_high})",
            line=dict(color="#7D9D33", width=2.5),
        ))
        fig.add_trace(go.Scatter(
            x=t_l, y=s_l, mode="lines", name=f"Low {gene}   (n={n_low})",
            line=dict(color="#a8c48a", width=2.5, dash="dash"),
        ))

        # CI bands (simulated)
        ci_upper_h = [min(1, s + 0.06) for s in s_h]
        ci_lower_h = [max(0, s - 0.06) for s in s_h]
        fig.add_trace(go.Scatter(
            x=t_h + t_h[::-1], y=ci_upper_h + ci_lower_h[::-1],
            fill="toself", fillcolor="rgba(125,157,51,0.12)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))

        fig.update_layout(
            title=f"{gene} — {surv_type.split('(')[0].strip()} in {cancer} (n={n_high+n_low})",
            xaxis_title="Time (months)",
            yaxis_title="Survival probability",
            yaxis=dict(range=[0, 1.05]),
            paper_bgcolor="#1B3022",
            plot_bgcolor="#243d2b",
            font=dict(family="Montserrat", color="#E1EAD8"),
            legend=dict(bgcolor="rgba(0,0,0,0)", x=0.98, y=0.98, xanchor="right"),
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#3a5a3a", gridwidth=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # ── Stats box ─────────────────────────────────────────────────────────
        hr  = round(np.random.uniform(1.2, 2.8), 2)
        pval= round(np.random.uniform(0.001, 0.049), 3)
        ci_lo = round(hr - np.random.uniform(0.1, 0.3), 2)
        ci_hi = round(hr + np.random.uniform(0.1, 0.4), 2)

        st.markdown("**Survival statistics**")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Log-rank p-value", f"{pval:.3f}")
        mc2.metric("Hazard ratio (HR)", f"{hr:.2f}")
        mc3.metric("95% CI", f"{ci_lo} – {ci_hi}")
        mc4.metric("Cutoff", cutoff)

        stats_df = pd.DataFrame({
            "Group":             [f"High {gene}", f"Low {gene}"],
            "N":                 [n_high, n_low],
            "Median survival":   [f"{int(np.median(t_high))} mo", f"{int(np.median(t_low))} mo"],
            "Events":            [int(e_high.sum()), int(e_low.sum())],
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div style='font-size:0.78rem;color:#a8c48a;margin-top:0.5rem'>
        Gene: <strong style='color:#E1EAD8'>{gene}</strong> &nbsp;|&nbsp;
        Cancer: <strong style='color:#E1EAD8'>{cancer}</strong> &nbsp;|&nbsp;
        Endpoint: {surv_type} &nbsp;|&nbsp; Data: TCGA (demo)
        </div>
        """, unsafe_allow_html=True)

        fig = render_figure_editor(fig, key_prefix="survival")

        csv = pd.DataFrame({"time_high": t_h, "surv_high": s_h}).to_csv(index=False)
        st.download_button("Download curve data as CSV", csv, f"{gene}_{cancer}_survival.csv", "text/csv")

render_footer()
