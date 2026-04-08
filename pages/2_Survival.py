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

st.set_page_config(page_title="VenuViz — Survival Analysis", page_icon="🧬", layout="wide")
inject_styles()
render_navbar()

CANCER_TYPES = [
    "ACC","BLCA","BRCA","CESC","CHOL","COAD","DLBC","ESCA","GBM",
    "HNSC","KICH","KIRC","KIRP","LAML","LGG","LIHC","LUAD","LUSC",
    "MESO","OV","PAAD","PCPG","PRAD","READ","SARC","SKCM","STAD",
    "TGCT","THCA","THYM","UCEC","UCS","UVM",
]
PLOT_TYPES = ["Kaplan-Meier curve","Forest plot (pan-cancer HR)","Competing risks","Landmark analysis","Multi-gene comparison"]

# ── Session state init ────────────────────────────────────────────────────────
_defaults = {
    "surv_gene":    "CD8A",
    "surv_cancer":  "LUAD",
    "surv_type":    "Overall survival (OS)",
    "surv_cutoff":  "Median",
    "surv_maxfu":   60,
    "surv_plot":    "Kaplan-Meier curve",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Restore from URL params ───────────────────────────────────────────────────
params = st.query_params
if "gene"   in params: st.session_state["surv_gene"]   = params["gene"]
if "cancer" in params: st.session_state["surv_cancer"] = params["cancer"]

st.markdown("""
<div class="page-header">
    <h1>Survival analysis</h1>
    <p>Generate Kaplan-Meier curves, forest plots, and competing risks analysis — with one-click publication export</p>
</div>""", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3])

with sidebar:
    st.markdown("### Input")

    gene = st.text_input("Gene symbol",
        value=st.session_state["surv_gene"],
        placeholder="e.g. CD8A, FOXP3, TP53",
        key="surv_gene_input")
    st.session_state["surv_gene"] = gene

    pa, pb, pc = st.columns(3)
    for col, eg in zip([pa,pb,pc], ["CD8A","FOXP3","TP53"]):
        with col:
            if st.button(eg, key=f"surv_pill_{eg}"):
                st.session_state["surv_gene"] = eg
                st.rerun()

    cancer = st.selectbox("Cancer type", CANCER_TYPES,
        index=CANCER_TYPES.index(st.session_state["surv_cancer"]),
        key="surv_cancer_sel")
    st.session_state["surv_cancer"] = cancer

    plot_type = st.selectbox("Analysis type", PLOT_TYPES,
        index=PLOT_TYPES.index(st.session_state["surv_plot"]),
        key="surv_plot_sel")
    st.session_state["surv_plot"] = plot_type

    surv_type = st.selectbox("Survival endpoint",
        ["Overall survival (OS)","Disease-free survival (DFS)",
         "Progression-free survival (PFS)","Disease-specific survival (DSS)"],
        index=["Overall survival (OS)","Disease-free survival (DFS)",
               "Progression-free survival (PFS)","Disease-specific survival (DSS)"]
              .index(st.session_state["surv_type"]),
        key="surv_type_sel")
    st.session_state["surv_type"] = surv_type

    cutoff = st.selectbox("Stratification cutoff",
        ["Median","Upper/lower quartile","Optimal cutoff"],
        index=["Median","Upper/lower quartile","Optimal cutoff"]
              .index(st.session_state["surv_cutoff"]),
        key="surv_cutoff_sel")
    st.session_state["surv_cutoff"] = cutoff

    if plot_type == "Kaplan-Meier curve":
        max_fu = st.slider("Max follow-up (months)", 12, 120,
            int(st.session_state["surv_maxfu"]), step=6, key="surv_fu_slider")
        st.session_state["surv_maxfu"] = max_fu

    generate = st.button("Generate →", use_container_width=True)

    # Shareable URL
    if gene:
        share_url = f"?gene={gene}&cancer={cancer}"
        st.markdown(f"<small style='color:#a8c48a'>🔗 <a href='{share_url}' style='color:#7D9D33'>Share this analysis</a></small>",
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<small style='color:#a8c48a'>
    <strong style='color:#E1EAD8'>Interpretation guide</strong><br>
    p &lt; 0.05: significant survival difference<br>
    HR &gt; 1: high expression = worse prognosis<br>
    HR &lt; 1: high expression = better prognosis
    </small>""", unsafe_allow_html=True)

# ── Helper: simulate KM data ──────────────────────────────────────────────────
def sim_km(n, med, max_t, seed=0):
    np.random.seed(seed)
    t = np.clip(np.random.exponential(med, n), 0, max_t)
    e = (t < max_t).astype(int)
    return np.sort(t), e

def km_curve(times, events):
    ut = np.unique(times[events==1])
    s=[1.0]; tp=[0]; ar=len(times)
    for t in ut:
        d = np.sum((times==t)&(events==1))
        s.append(s[-1]*(1-d/ar))
        ar -= np.sum(times<=t)
        tp.append(t)
    return tp, s

with main:
    if not generate and not params:
        st.markdown("""
        <div class="empty-state">
            <h3>Select analysis type and click Generate</h3>
            <p>KM curves · Forest plots · Competing risks · Landmark analysis</p>
            <div class="pill-row">
                <span class="pill">CD8A</span>
                <span class="pill">FOXP3</span>
                <span class="pill">TP53</span>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        gene      = st.session_state["surv_gene"].upper().strip()
        cancer    = st.session_state["surv_cancer"]
        plot_type = st.session_state["surv_plot"]
        max_fu    = int(st.session_state["surv_maxfu"])
        cutoff    = st.session_state["surv_cutoff"]
        surv_type = st.session_state["surv_type"]
        seed_base = hash(gene+cancer) % 999

        # ── KM CURVE ─────────────────────────────────────────────────────────
        if plot_type == "Kaplan-Meier curve":
            n=80
            t_hi,e_hi = sim_km(n, 38, max_fu, seed_base)
            t_lo,e_lo = sim_km(n, 22, max_fu, seed_base+1)
            th,sh = km_curve(t_hi,e_hi)
            tl,sl = km_curve(t_lo,e_lo)

            fig = go.Figure()
            # CI bands
            ci_hi_u = [min(1,s+0.06) for s in sh]
            ci_hi_l = [max(0,s-0.06) for s in sh]
            ci_lo_u = [min(1,s+0.06) for s in sl]
            ci_lo_l = [max(0,s-0.06) for s in sl]
            fig.add_trace(go.Scatter(x=th+th[::-1],y=ci_hi_u+ci_hi_l[::-1],
                fill="toself",fillcolor="rgba(125,157,51,0.12)",
                line=dict(color="rgba(0,0,0,0)"),showlegend=False,hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=tl+tl[::-1],y=ci_lo_u+ci_lo_l[::-1],
                fill="toself",fillcolor="rgba(168,196,138,0.12)",
                line=dict(color="rgba(0,0,0,0)"),showlegend=False,hoverinfo="skip"))
            # KM lines
            fig.add_trace(go.Scatter(x=th,y=sh,mode="lines",
                name=f"High {gene} (n={n})",
                line=dict(color="#7D9D33",width=2.5)))
            fig.add_trace(go.Scatter(x=tl,y=sl,mode="lines",
                name=f"Low {gene} (n={n})",
                line=dict(color="#a8c48a",width=2.5,dash="dash")))
            # Censoring ticks
            cens_hi = t_hi[e_hi==0]
            cens_lo = t_lo[e_lo==0]
            for ct,cs,c in [(cens_hi,th,sh),(cens_lo,tl,sl)]:
                interp_s = np.interp(ct, cs, cs)
                fig.add_trace(go.Scatter(x=ct,y=np.interp(ct,cs,cs),
                    mode="markers",marker=dict(symbol="line-ns",size=8,
                    color="#E1EAD8",line=dict(width=1.5,color="#E1EAD8")),
                    showlegend=False,hoverinfo="skip"))

            fig.update_layout(
                title=f"{gene} — {surv_type.split('(')[0].strip()} in {cancer} (n={n*2})",
                xaxis_title="Time (months)",yaxis_title="Survival probability",
                yaxis=dict(range=[0,1.05]),
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)",x=0.98,y=0.98,
                            xanchor="right",yanchor="top"))
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#3a5a3a",gridwidth=0.5)
            st.plotly_chart(fig, use_container_width=True)

            hr   = round(np.random.uniform(1.2,2.8),2)
            pval = round(np.random.uniform(0.001,0.049),3)
            ci_lo_v = round(hr-np.random.uniform(0.1,0.3),2)
            ci_hi_v = round(hr+np.random.uniform(0.1,0.4),2)

            mc1,mc2,mc3,mc4 = st.columns(4)
            mc1.metric("Log-rank p-value", f"{pval:.3f}")
            mc2.metric("Hazard ratio", f"{hr:.2f}")
            mc3.metric("95% CI", f"{ci_lo_v}–{ci_hi_v}")
            mc4.metric("Cutoff", cutoff)

            sdf = pd.DataFrame({"Group":[f"High {gene}",f"Low {gene}"],
                "N":[n,n],
                "Median survival":[f"{int(np.median(t_hi))} mo",f"{int(np.median(t_lo))} mo"],
                "Events":[int(e_hi.sum()),int(e_lo.sum())]})
            st.dataframe(sdf, use_container_width=True, hide_index=True)

            meta = {"gene":gene,"cancer":cancer,"plot_type":"survival",
                    "survival_type":surv_type,"cutoff":cutoff,
                    "n_tumor":n*2,"pvalue":pval,"hr":hr,"dataset":"TCGA (demo)"}
            fig = render_figure_editor(fig, key_prefix="km", meta=meta)

            csv = pd.DataFrame({"time_high":th,"surv_high":sh}).to_csv(index=False)
            st.download_button("Download curve data as CSV", csv,
                               f"{gene}_{cancer}_survival.csv","text/csv")

        # ── FOREST PLOT ───────────────────────────────────────────────────────
        elif plot_type == "Forest plot (pan-cancer HR)":
            cancers_sel = CANCER_TYPES[:20]
            np.random.seed(seed_base)
            hrs     = np.random.uniform(0.5, 3.0, len(cancers_sel))
            ci_lo_v = hrs - np.random.uniform(0.1,0.5,len(cancers_sel))
            ci_hi_v = hrs + np.random.uniform(0.1,0.5,len(cancers_sel))
            pvals   = np.random.uniform(0.001,0.3,len(cancers_sel))
            colors_f= ["#7D9D33" if p<0.05 else "#a8c48a" for p in pvals]

            fig = go.Figure()
            for i,(c,hr,lo,hi,p,col) in enumerate(zip(
                    cancers_sel,hrs,ci_lo_v,ci_hi_v,pvals,colors_f)):
                fig.add_trace(go.Scatter(
                    x=[lo,hi],y=[i,i],mode="lines",
                    line=dict(color=col,width=2),showlegend=False))
                fig.add_trace(go.Scatter(
                    x=[hr],y=[i],mode="markers",
                    marker=dict(color=col,size=10,
                                symbol="square" if p<0.05 else "circle"),
                    name=c,showlegend=False,
                    hovertemplate=f"{c}: HR={hr:.2f} (95%CI: {lo:.2f}–{hi:.2f}), p={p:.3f}<extra></extra>"))
                fig.add_annotation(x=hi+0.05,y=i,
                    text=f"<b>{c}</b>" if p<0.05 else c,
                    showarrow=False,xanchor="left",
                    font=dict(size=10,color="#E1EAD8" if p<0.05 else "#a8c48a"))

            fig.add_vline(x=1.0,line_dash="dash",line_color="#E1EAD8",
                          annotation_text="HR=1",annotation_font_color="#a8c48a")
            fig.update_layout(
                title=f"{gene} — Hazard Ratio across cancer types ({surv_type.split('(')[0].strip()})",
                xaxis_title="Hazard Ratio (95% CI)",
                yaxis=dict(tickvals=list(range(len(cancers_sel))),
                           ticktext=cancers_sel,showgrid=False),
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                height=600,margin=dict(l=60,r=200))
            fig.update_xaxes(showgrid=True,gridcolor="#3a5a3a",range=[0,4])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""<small style='color:#a8c48a'>
            Filled squares = p&lt;0.05 (significant). Circles = p≥0.05.
            Green = high expression associated with worse survival (HR&gt;1).
            </small>""", unsafe_allow_html=True)

            fdf = pd.DataFrame({"Cancer":cancers_sel,"HR":hrs.round(2),
                "CI_lower":ci_lo_v.round(2),"CI_upper":ci_hi_v.round(2),
                "p_value":pvals.round(3)})
            meta = {"gene":gene,"cancer":"Pan-cancer","plot_type":"forest",
                    "survival_type":surv_type,"dataset":"TCGA (demo)"}
            fig = render_figure_editor(fig, key_prefix="forest", meta=meta)
            st.download_button("Download forest plot data as CSV",
                               fdf.to_csv(index=False),
                               f"{gene}_pancancer_HR.csv","text/csv")

        # ── COMPETING RISKS ───────────────────────────────────────────────────
        elif plot_type == "Competing risks":
            n=150
            np.random.seed(seed_base)
            t   = np.sort(np.random.exponential(30, n))
            e1  = np.random.choice([0,1,2],n,p=[0.3,0.5,0.2])
            cif1,cif2,tp = [0],[0],[0]
            at_risk = n
            for ti in np.unique(t):
                d1 = np.sum((t==ti)&(e1==1))
                d2 = np.sum((t==ti)&(e1==2))
                cif1.append(cif1[-1] + d1/at_risk)
                cif2.append(cif2[-1] + d2/at_risk)
                at_risk -= np.sum(t<=ti)
                tp.append(ti)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tp,y=cif1,mode="lines",
                name="Event of interest (death)",
                line=dict(color="#7D9D33",width=2.5)))
            fig.add_trace(go.Scatter(x=tp,y=cif2,mode="lines",
                name="Competing event",
                line=dict(color="#E64B35",width=2.5,dash="dot")))
            fig.add_trace(go.Scatter(
                x=tp+tp[::-1],
                y=[c+0.03 for c in cif1]+[max(0,c-0.03) for c in cif1[::-1]],
                fill="toself",fillcolor="rgba(125,157,51,0.12)",
                line=dict(color="rgba(0,0,0,0)"),showlegend=False))
            fig.update_layout(
                title=f"{gene} — Competing risks analysis in {cancer}",
                xaxis_title="Time (months)",
                yaxis_title="Cumulative incidence",
                yaxis=dict(range=[0,1]),
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#3a5a3a",gridwidth=0.5)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""<small style='color:#a8c48a'>
            Competing risks analysis accounts for events that prevent the primary outcome.
            Unlike KM curves, cumulative incidence functions do not sum to 1.
            </small>""", unsafe_allow_html=True)
            meta = {"gene":gene,"cancer":cancer,"plot_type":"competing_risks",
                    "dataset":"TCGA (demo)"}
            fig = render_figure_editor(fig, key_prefix="comprisks", meta=meta)

        # ── LANDMARK ANALYSIS ─────────────────────────────────────────────────
        elif plot_type == "Landmark analysis":
            landmark_t = st.slider("Landmark time (months)", 6, 36, 12)
            n=60
            fig = make_subplots(rows=1,cols=2,
                subplot_titles=["All patients (from time 0)",
                                 f"Landmark at {landmark_t} months"],
                shared_yaxes=True)
            for col_i, seed_add in enumerate([0,10],1):
                t_hi,e_hi = sim_km(n,38,60,seed_base+seed_add)
                t_lo,e_lo = sim_km(n,22,60,seed_base+seed_add+1)
                th,sh = km_curve(t_hi,e_hi)
                tl,sl = km_curve(t_lo,e_lo)
                fig.add_trace(go.Scatter(x=th,y=sh,mode="lines",
                    name=f"High {gene}",line=dict(color="#7D9D33",width=2),
                    showlegend=(col_i==1)),row=1,col=col_i)
                fig.add_trace(go.Scatter(x=tl,y=sl,mode="lines",
                    name=f"Low {gene}",line=dict(color="#a8c48a",width=2,dash="dash"),
                    showlegend=(col_i==1)),row=1,col=col_i)
                if col_i==2:
                    fig.add_vline(x=landmark_t,line_dash="dot",
                                  line_color="#E1EAD8",row=1,col=col_i)
            fig.update_layout(
                title=f"{gene} — Landmark analysis at {landmark_t} months in {cancer}",
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"))
            fig.update_yaxes(title_text="Survival probability",range=[0,1.05])
            fig.update_xaxes(title_text="Time (months)",showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
            meta = {"gene":gene,"cancer":cancer,"plot_type":"landmark",
                    "dataset":"TCGA (demo)"}
            fig = render_figure_editor(fig, key_prefix="landmark", meta=meta)

        # ── MULTI-GENE COMPARISON ─────────────────────────────────────────────
        elif plot_type == "Multi-gene comparison":
            extra_genes = st.text_input(
                "Add more genes (comma separated)",
                placeholder="e.g. FOXP3, PD-L1, CTLA4",
                key="surv_extra_genes")
            genes_list = [gene] + [g.strip().upper() for g in extra_genes.split(",") if g.strip()]
            genes_list = genes_list[:5]
            colors_mg  = ["#7D9D33","#a8c48a","#4DBBD5","#E64B35","#F39B7F"]
            fig = go.Figure()
            for i,g in enumerate(genes_list):
                np.random.seed(hash(g+cancer)%999)
                t_hi,e_hi = sim_km(60, np.random.uniform(25,45), 60, hash(g)%999)
                th,sh = km_curve(t_hi,e_hi)
                fig.add_trace(go.Scatter(x=th,y=sh,mode="lines",name=f"High {g}",
                    line=dict(color=colors_mg[i],width=2.5)))
            fig.update_layout(
                title=f"Multi-gene survival comparison in {cancer}",
                xaxis_title="Time (months)",yaxis_title="Survival probability",
                yaxis=dict(range=[0,1.05]),
                paper_bgcolor="#1B3022",plot_bgcolor="#243d2b",
                font=dict(family="Montserrat",color="#E1EAD8"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#3a5a3a",gridwidth=0.5)
            st.plotly_chart(fig, use_container_width=True)
            meta = {"gene":", ".join(genes_list),"cancer":cancer,
                    "plot_type":"multi_gene_survival","dataset":"TCGA (demo)"}
            fig = render_figure_editor(fig, key_prefix="multigene", meta=meta)

render_footer()