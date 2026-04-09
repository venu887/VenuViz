import streamlit as st
import plotly.graph_objects as go
import zipfile, io, json
from datetime import datetime

JOURNAL_PRESETS = {
    "Nature / Cell":         {"font_family":"Arial",           "font_size_title":8,  "font_size_axis":7,  "font_size_tick":6,  "dpi":300, "show_grid":False},
    "PNAS":                  {"font_family":"Helvetica",       "font_size_title":9,  "font_size_axis":8,  "font_size_tick":7,  "dpi":600, "show_grid":False},
    "Bioinformatics (OUP)":  {"font_family":"Times New Roman", "font_size_title":10, "font_size_axis":9,  "font_size_tick":8,  "dpi":300, "show_grid":True},
    "Generic publication":   {"font_family":"Arial",           "font_size_title":11, "font_size_axis":10, "font_size_tick":9,  "dpi":300, "show_grid":False},
    "Presentation / Poster": {"font_family":"Arial",           "font_size_title":16, "font_size_axis":14, "font_size_tick":12, "dpi":150, "show_grid":True},
}

def _sk(prefix, suffix):
    """Build a session state key that is NOT used as a widget key."""
    return f"__fe_{prefix}_{suffix}__"

def _init_defaults(prefix):
    defaults = {
        "font_family":     "Arial",
        "font_size_title": 12,
        "font_size_axis":  10,
        "font_size_tick":  9,
        "bold_title":      False,
        "fig_w":           800,
        "fig_h":           500,
        "bg":              "#ffffff",
        "show_grid":       False,
        "legend_pos":      "Inside top-right",
        "export_fmt":      "PNG",
        "dpi":             300,
        "color_g1":        "#7D9D33",
        "color_g2":        "#E1EAD8",
        "color_g3":        "#a8c48a",
        "opacity":         0.85,
        "line_width":      2.0,
        "marker_size":     6,
    }
    for k, v in defaults.items():
        sk = _sk(prefix, k)
        if sk not in st.session_state:
            st.session_state[sk] = v


def render_figure_editor(fig: go.Figure,
                         key_prefix: str = "fig",
                         meta: dict = None) -> go.Figure:
    """
    Renders the publication figure editor inside a st.form so that
    NO widget interaction triggers a page rerun until the user
    explicitly clicks 'Apply changes'.
    """
    _init_defaults(key_prefix)

    with st.expander("◈  Customize figure for publication", expanded=False):

        # ── Journal preset buttons (outside form — instant apply) ─────────────
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:700;color:#7D9D33;"
            "letter-spacing:.06em;text-transform:uppercase;margin-bottom:.5rem'>"
            "Journal presets — one click applies all specs</p>",
            unsafe_allow_html=True)

        preset_cols = st.columns(len(JOURNAL_PRESETS))
        for i, (name, settings) in enumerate(JOURNAL_PRESETS.items()):
            with preset_cols[i]:
                if st.button(name, key=f"_preset_{key_prefix}_{i}"):
                    for k, v in settings.items():
                        st.session_state[_sk(prefix=key_prefix, suffix=k)] = v
                    # No st.rerun() — form will pick up new defaults on next submit

        st.divider()

        # ── Main controls inside a form — nothing reruns until submit ─────────
        with st.form(key=f"_fe_form_{key_prefix}"):
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown("**Typography**")
                font_family = st.selectbox(
                    "Font family",
                    ["Arial", "Times New Roman", "Helvetica", "Calibri", "Courier New"],
                    index=["Arial","Times New Roman","Helvetica","Calibri","Courier New"]
                          .index(st.session_state[_sk(key_prefix,"font_family")]),
                    key=f"_w_ff_{key_prefix}")

                font_size_title = st.slider(
                    "Title size (pt)", 6, 24,
                    int(st.session_state[_sk(key_prefix,"font_size_title")]),
                    key=f"_w_fst_{key_prefix}")

                font_size_axis = st.slider(
                    "Axis label size (pt)", 6, 20,
                    int(st.session_state[_sk(key_prefix,"font_size_axis")]),
                    key=f"_w_fsa_{key_prefix}")

                font_size_tick = st.slider(
                    "Tick label size (pt)", 5, 16,
                    int(st.session_state[_sk(key_prefix,"font_size_tick")]),
                    key=f"_w_fstic_{key_prefix}")

                bold_title = st.checkbox(
                    "Bold title",
                    value=bool(st.session_state[_sk(key_prefix,"bold_title")]),
                    key=f"_w_bt_{key_prefix}")

            with c2:
                st.markdown("**Colors**")
                color_g1 = st.color_picker(
                    "Group 1 color",
                    st.session_state[_sk(key_prefix,"color_g1")],
                    key=f"_w_c1_{key_prefix}")

                color_g2 = st.color_picker(
                    "Group 2 color",
                    st.session_state[_sk(key_prefix,"color_g2")],
                    key=f"_w_c2_{key_prefix}")

                color_g3 = st.color_picker(
                    "Group 3 color",
                    st.session_state[_sk(key_prefix,"color_g3")],
                    key=f"_w_c3_{key_prefix}")

                color_bg = st.color_picker(
                    "Background",
                    st.session_state[_sk(key_prefix,"bg")],
                    key=f"_w_bg_{key_prefix}")

                opacity = st.slider(
                    "Opacity", 0.3, 1.0,
                    float(st.session_state[_sk(key_prefix,"opacity")]),
                    step=0.05, key=f"_w_op_{key_prefix}")

            with c3:
                st.markdown("**Layout & Export**")
                fig_w = st.number_input(
                    "Width (px)", 400, 1600,
                    int(st.session_state[_sk(key_prefix,"fig_w")]),
                    step=50, key=f"_w_fw_{key_prefix}")

                fig_h = st.number_input(
                    "Height (px)", 300, 1200,
                    int(st.session_state[_sk(key_prefix,"fig_h")]),
                    step=50, key=f"_w_fh_{key_prefix}")

                show_grid = st.checkbox(
                    "Show gridlines",
                    value=bool(st.session_state[_sk(key_prefix,"show_grid")]),
                    key=f"_w_sg_{key_prefix}")

                legend_pos = st.selectbox(
                    "Legend position",
                    ["Inside top-right","Inside top-left","Outside right","Hidden"],
                    index=["Inside top-right","Inside top-left","Outside right","Hidden"]
                          .index(st.session_state[_sk(key_prefix,"legend_pos")]),
                    key=f"_w_lp_{key_prefix}")

                export_fmt = st.selectbox(
                    "Export format", ["PNG", "SVG"],
                    index=["PNG","SVG"].index(st.session_state[_sk(key_prefix,"export_fmt")]),
                    key=f"_w_ef_{key_prefix}")

                dpi = st.selectbox(
                    "Resolution (DPI)", [150, 300, 600],
                    index=[150,300,600].index(int(st.session_state[_sk(key_prefix,"dpi")])),
                    key=f"_w_dpi_{key_prefix}")

                line_width = st.slider(
                    "Line width", 0.5, 4.0,
                    float(st.session_state[_sk(key_prefix,"line_width")]),
                    step=0.5, key=f"_w_lw_{key_prefix}")

                marker_size = st.slider(
                    "Marker size", 2, 16,
                    int(st.session_state[_sk(key_prefix,"marker_size")]),
                    key=f"_w_ms_{key_prefix}")

            # ── Submit button — ONLY this triggers rerun ──────────────────────
            submitted = st.form_submit_button(
                "Apply changes →",
                use_container_width=True,
                type="primary")

        # ── On submit: save widget values to session state ────────────────────
        if submitted:
            st.session_state[_sk(key_prefix,"font_family")]     = font_family
            st.session_state[_sk(key_prefix,"font_size_title")] = font_size_title
            st.session_state[_sk(key_prefix,"font_size_axis")]  = font_size_axis
            st.session_state[_sk(key_prefix,"font_size_tick")]  = font_size_tick
            st.session_state[_sk(key_prefix,"bold_title")]      = bold_title
            st.session_state[_sk(key_prefix,"color_g1")]        = color_g1
            st.session_state[_sk(key_prefix,"color_g2")]        = color_g2
            st.session_state[_sk(key_prefix,"color_g3")]        = color_g3
            st.session_state[_sk(key_prefix,"bg")]              = color_bg
            st.session_state[_sk(key_prefix,"opacity")]         = opacity
            st.session_state[_sk(key_prefix,"fig_w")]           = fig_w
            st.session_state[_sk(key_prefix,"fig_h")]           = fig_h
            st.session_state[_sk(key_prefix,"show_grid")]       = show_grid
            st.session_state[_sk(key_prefix,"legend_pos")]      = legend_pos
            st.session_state[_sk(key_prefix,"export_fmt")]      = export_fmt
            st.session_state[_sk(key_prefix,"dpi")]             = dpi
            st.session_state[_sk(key_prefix,"line_width")]      = line_width
            st.session_state[_sk(key_prefix,"marker_size")]     = marker_size

        # ── Apply stored values to figure ─────────────────────────────────────
        bg         = st.session_state[_sk(key_prefix,"bg")]
        font_color = "#000000" if bg in ["#ffffff","white"] else "#E1EAD8"
        grid_color = "#dddddd" if bg in ["#ffffff","white"] else "#3a5a3a"
        ff         = st.session_state[_sk(key_prefix,"font_family")]
        fst        = int(st.session_state[_sk(key_prefix,"font_size_title")])
        fsa        = int(st.session_state[_sk(key_prefix,"font_size_axis")])
        fsti       = int(st.session_state[_sk(key_prefix,"font_size_tick")])
        sg         = bool(st.session_state[_sk(key_prefix,"show_grid")])
        lp         = st.session_state[_sk(key_prefix,"legend_pos")]
        fmt        = st.session_state[_sk(key_prefix,"export_fmt")]
        dpi_val    = int(st.session_state[_sk(key_prefix,"dpi")])

        fig.update_layout(
            width=int(st.session_state[_sk(key_prefix,"fig_w")]),
            height=int(st.session_state[_sk(key_prefix,"fig_h")]),
            paper_bgcolor=bg,
            plot_bgcolor=bg,
            font=dict(family=ff, size=fst, color=font_color),
            title_font=dict(family=ff, size=fst, color=font_color),
            xaxis=dict(
                showgrid=sg, gridcolor=grid_color,
                title_font=dict(size=fsa, family=ff),
                tickfont=dict(size=fsti, family=ff)),
            yaxis=dict(
                showgrid=sg, gridcolor=grid_color,
                title_font=dict(size=fsa, family=ff),
                tickfont=dict(size=fsti, family=ff)),
        )

        legend_map = {
            "Inside top-right": dict(showlegend=True,  legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top")),
            "Inside top-left":  dict(showlegend=True,  legend=dict(x=0.02, y=0.98, xanchor="left",  yanchor="top")),
            "Outside right":    dict(showlegend=True,  legend=dict(x=1.02, y=0.5,  xanchor="left",  yanchor="middle")),
            "Hidden":           dict(showlegend=False),
        }
        fig.update_layout(**legend_map.get(lp, {}))

        # ── Download buttons ──────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        dl1, dl2, dl3 = st.columns(3)

        with dl1:
            try:
                img_bytes = fig.to_image(format=fmt.lower(), scale=dpi_val/96)
                st.download_button(
                    f"Download {fmt} ({dpi_val} DPI)",
                    data=img_bytes,
                    file_name=f"venuviz_figure.{fmt.lower()}",
                    mime=f"image/{fmt.lower()}",
                    key=f"_dl_single_{key_prefix}")
            except Exception:
                html_bytes = fig.to_html(include_plotlyjs="cdn").encode()
                st.download_button(
                    "Download interactive HTML",
                    data=html_bytes,
                    file_name="venuviz_figure.html",
                    mime="text/html",
                    key=f"_dl_html_{key_prefix}")
                st.caption("Add `kaleido` to requirements.txt for PNG/SVG export")

        with dl2:
            if meta:
                try:
                    zip_bytes = _build_zip(fig, fmt, dpi_val, meta)
                    st.download_button(
                        "Download full package (ZIP)",
                        data=zip_bytes,
                        file_name="venuviz_package.zip",
                        mime="application/zip",
                        key=f"_dl_zip_{key_prefix}")
                except Exception:
                    st.caption("ZIP download requires kaleido")

        with dl3:
            st.markdown(
                "<small style='color:#a8c48a'>If you use this figure, please "
                "<a href='/About' style='color:#7D9D33'>cite VenuViz →</a></small>",
                unsafe_allow_html=True)

    return fig


# ── ZIP builder ───────────────────────────────────────────────────────────────

def _build_zip(fig, fmt, dpi, meta):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        try:
            img = fig.to_image(format=fmt.lower(), scale=dpi/96)
            zf.writestr(f"figure.{fmt.lower()}", img)
            zf.writestr("figure.svg", fig.to_image(format="svg"))
        except Exception:
            zf.writestr("figure.html",
                        fig.to_html(include_plotlyjs="cdn").encode())

        params = {"generated_by":"VenuViz","date":datetime.now().strftime("%Y-%m-%d"),
                  "url":"https://venuviz.streamlit.app", **meta}
        zf.writestr("parameters.json", json.dumps(params, indent=2))
        zf.writestr("methods.txt",      _methods(meta))
        zf.writestr("figure_legend.txt",_legend(meta))
    buf.seek(0)
    return buf.read()


def _methods(meta):
    gene  = meta.get("gene","[GENE]")
    cancer= meta.get("cancer","[CANCER]")
    n_t   = meta.get("n_tumor","")
    n_n   = meta.get("n_normal","")
    test  = meta.get("test","Wilcoxon rank-sum")
    cutoff= meta.get("cutoff","median")
    ds    = meta.get("dataset","TCGA")
    surv  = meta.get("survival_type","Overall survival")
    pt    = meta.get("plot_type","expression")

    if pt == "survival":
        return (f"Gene expression and clinical data for {gene} in {cancer} were obtained from {ds}. "
                f"Patients were stratified into high/low {gene} expression groups using the {cutoff} "
                f"expression value as the cutoff. Survival analysis was performed using the Kaplan-Meier "
                f"method. {surv} differences were assessed using the log-rank test. Hazard ratios and "
                f"95% confidence intervals were calculated using Cox proportional hazards regression. "
                f"All analyses were performed using VenuViz (venuviz.streamlit.app).")
    else:
        n_str = f"n={n_t} tumor" + (f", n={n_n} normal" if n_n else "")
        return (f"Gene expression data for {gene} in {cancer} ({n_str}) were obtained from {ds}. "
                f"Expression values are reported as log2(TPM+1) normalized counts. "
                f"Differential expression between groups was assessed using the {test} test. "
                f"All analyses were performed using VenuViz (venuviz.streamlit.app; Mekala V, 2026).")


def _legend(meta):
    gene  = meta.get("gene","[GENE]")
    cancer= meta.get("cancer","[CANCER]")
    n_t   = meta.get("n_tumor","")
    n_n   = meta.get("n_normal","")
    pval  = meta.get("pvalue","")
    hr    = meta.get("hr","")
    test  = meta.get("test","Wilcoxon rank-sum")
    ds    = meta.get("dataset","TCGA")
    pt    = meta.get("plot_type","expression")

    pv_str = f" p={pval}," if pval else ""
    hr_str = f" HR={hr}," if hr else ""

    if pt == "survival":
        return (f"Figure. Kaplan-Meier survival curve for {gene} in {cancer}. "
                f"Patients stratified by {gene} expression (high vs low, n={n_t}). "
                f"Data: {ds}.{pv_str}{hr_str} log-rank test. "
                f"Shaded areas: 95% CI. Generated with VenuViz (venuviz.streamlit.app).")
    else:
        n_str = f"n={n_t} tumor" + (f", n={n_n} normal" if n_n else "")
        return (f"Figure. {gene} expression in {cancer}. "
                f"Log2(TPM+1) values from {ds} ({n_str}).{pv_str} "
                f"{test} test. Center line: median; box: IQR; whiskers: 1.5×IQR. "
                f"Generated with VenuViz (venuviz.streamlit.app).")
