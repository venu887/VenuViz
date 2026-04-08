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

PALETTES = {
    "VenuViz default":    ["#7D9D33","#E1EAD8","#a8c48a","#3a5a3a","#243d2b"],
    "Nature (red/blue)":  ["#E64B35","#4DBBD5","#00A087","#3C5488","#F39B7F"],
    "Cell (blue/orange)": ["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD"],
    "Colorblind safe":    ["#0072B2","#E69F00","#56B4E9","#009E73","#F0E442"],
    "Grayscale":          ["#111111","#444444","#777777","#AAAAAA","#DDDDDD"],
}

def _key(prefix, suffix):
    return f"{prefix}_{suffix}"

def _init(prefix):
    defaults = {
        "font_family":    "Arial",
        "font_size_title": 12,
        "font_size_axis":  10,
        "font_size_tick":  9,
        "bold_title":      False,
        "italic_title":    False,
        "bold_axis":       False,
        "fig_w":           800,
        "fig_h":           500,
        "bg":              "white",
        "show_grid":       False,
        "legend_pos":      "Inside top-right",
        "export_fmt":      "PNG",
        "dpi":             300,
        "palette":         "VenuViz default",
        "color_g1":        "#7D9D33",
        "color_g2":        "#E1EAD8",
        "color_g3":        "#a8c48a",
        "color_g4":        "#3a5a3a",
        "color_bg":        "#ffffff",
        "opacity":         0.85,
        "line_width":      2,
        "marker_size":     6,
        "show_grid":       False,
        "grid_style":      "solid",
    }
    for k, v in defaults.items():
        sk = _key(prefix, k)
        if sk not in st.session_state:
            st.session_state[sk] = v

def render_figure_editor(fig: go.Figure, key_prefix: str = "fig",
                         meta: dict = None) -> go.Figure:
    """
    meta = {gene, cancer, plot_type, test, n_tumor, n_normal,
            pvalue, hr, dataset, cutoff}  — used for ZIP package
    """
    _init(key_prefix)

    with st.expander("◈  Customize figure for publication", expanded=False):

        # ── Journal Presets ───────────────────────────────────────────────────
        st.markdown("<p style='font-size:0.78rem;font-weight:700;color:#7D9D33;"
                    "letter-spacing:.06em;text-transform:uppercase;margin-bottom:.6rem'>"
                    "Journal presets</p>", unsafe_allow_html=True)
        cols = st.columns(len(JOURNAL_PRESETS))
        for i, (name, settings) in enumerate(JOURNAL_PRESETS.items()):
            with cols[i]:
                if st.button(name, key=f"{key_prefix}_preset_{i}"):
                    for k, v in settings.items():
                        st.session_state[_key(key_prefix, k)] = v
                    st.rerun()

        st.divider()

        # ── Controls ──────────────────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("**Typography**")
            st.session_state[_key(key_prefix,"font_family")] = st.selectbox(
                "Font", ["Arial","Times New Roman","Helvetica","Calibri","Courier New"],
                index=["Arial","Times New Roman","Helvetica","Calibri","Courier New"]
                      .index(st.session_state[_key(key_prefix,"font_family")]),
                key=f"{key_prefix}_ff")

            st.session_state[_key(key_prefix,"font_size_title")] = st.slider(
                "Title size (pt)", 6, 24,
                st.session_state[_key(key_prefix,"font_size_title")],
                key=f"{key_prefix}_fst")

            st.session_state[_key(key_prefix,"font_size_axis")] = st.slider(
                "Axis label size (pt)", 6, 20,
                st.session_state[_key(key_prefix,"font_size_axis")],
                key=f"{key_prefix}_fsa")

            st.session_state[_key(key_prefix,"font_size_tick")] = st.slider(
                "Tick label size (pt)", 5, 16,
                st.session_state[_key(key_prefix,"font_size_tick")],
                key=f"{key_prefix}_fstic")

            tb_col, ib_col = st.columns(2)
            with tb_col:
                st.session_state[_key(key_prefix,"bold_title")] = st.toggle(
                    "Bold title", st.session_state[_key(key_prefix,"bold_title")],
                    key=f"{key_prefix}_bt")
            with ib_col:
                st.session_state[_key(key_prefix,"italic_title")] = st.toggle(
                    "Italic title", st.session_state[_key(key_prefix,"italic_title")],
                    key=f"{key_prefix}_it")

        with c2:
            st.markdown("**Colors**")
            st.session_state[_key(key_prefix,"color_g1")] = st.color_picker(
                "Group 1 color", st.session_state[_key(key_prefix,"color_g1")],
                key=f"{key_prefix}_c1")
            st.session_state[_key(key_prefix,"color_g2")] = st.color_picker(
                "Group 2 color", st.session_state[_key(key_prefix,"color_g2")],
                key=f"{key_prefix}_c2")
            st.session_state[_key(key_prefix,"color_g3")] = st.color_picker(
                "Group 3 color", st.session_state[_key(key_prefix,"color_g3")],
                key=f"{key_prefix}_c3")
            st.session_state[_key(key_prefix,"color_bg")] = st.color_picker(
                "Background", st.session_state[_key(key_prefix,"color_bg")],
                key=f"{key_prefix}_cbg")
            st.session_state[_key(key_prefix,"opacity")] = st.slider(
                "Opacity", 0.3, 1.0,
                float(st.session_state[_key(key_prefix,"opacity")]),
                step=0.05, key=f"{key_prefix}_op")

        with c3:
            st.markdown("**Layout & Export**")
            st.session_state[_key(key_prefix,"fig_w")] = st.number_input(
                "Width (px)", 400, 1600,
                int(st.session_state[_key(key_prefix,"fig_w")]),
                step=50, key=f"{key_prefix}_fw")
            st.session_state[_key(key_prefix,"fig_h")] = st.number_input(
                "Height (px)", 300, 1200,
                int(st.session_state[_key(key_prefix,"fig_h")]),
                step=50, key=f"{key_prefix}_fh")
            st.session_state[_key(key_prefix,"show_grid")] = st.toggle(
                "Show gridlines",
                st.session_state[_key(key_prefix,"show_grid")],
                key=f"{key_prefix}_sg")
            st.session_state[_key(key_prefix,"legend_pos")] = st.selectbox(
                "Legend", ["Inside top-right","Inside top-left","Outside right","Hidden"],
                key=f"{key_prefix}_lp")
            st.session_state[_key(key_prefix,"export_fmt")] = st.selectbox(
                "Format", ["PNG","SVG"], key=f"{key_prefix}_ef")
            st.session_state[_key(key_prefix,"dpi")] = st.selectbox(
                "DPI", [150,300,600], index=1, key=f"{key_prefix}_dpi")
            st.session_state[_key(key_prefix,"line_width")] = st.slider(
                "Line width", 0.5, 4.0,
                float(st.session_state[_key(key_prefix,"line_width")]),
                step=0.5, key=f"{key_prefix}_lw")
            st.session_state[_key(key_prefix,"marker_size")] = st.slider(
                "Marker size", 2, 16,
                int(st.session_state[_key(key_prefix,"marker_size")]),
                key=f"{key_prefix}_ms")

        # ── Apply settings to figure ──────────────────────────────────────────
        bg        = st.session_state[_key(key_prefix,"color_bg")]
        font_color = "#000000" if bg in ["#ffffff","white"] else "#E1EAD8"
        grid_color = "#dddddd" if bg in ["#ffffff","white"] else "#3a5a3a"
        ff        = st.session_state[_key(key_prefix,"font_family")]
        bold_t    = st.session_state[_key(key_prefix,"bold_title")]
        fst       = st.session_state[_key(key_prefix,"font_size_title")]
        fsa       = st.session_state[_key(key_prefix,"font_size_axis")]
        fsti      = st.session_state[_key(key_prefix,"font_size_tick")]
        show_grid = st.session_state[_key(key_prefix,"show_grid")]

        title_weight = "bold" if bold_t else "normal"

        fig.update_layout(
            width  = int(st.session_state[_key(key_prefix,"fig_w")]),
            height = int(st.session_state[_key(key_prefix,"fig_h")]),
            paper_bgcolor = bg,
            plot_bgcolor  = bg,
            font = dict(family=ff, size=fst, color=font_color),
            title_font = dict(family=ff, size=fst, color=font_color),
            xaxis = dict(
                showgrid=show_grid, gridcolor=grid_color,
                title_font=dict(size=fsa, family=ff),
                tickfont=dict(size=fsti, family=ff),
            ),
            yaxis = dict(
                showgrid=show_grid, gridcolor=grid_color,
                title_font=dict(size=fsa, family=ff),
                tickfont=dict(size=fsti, family=ff),
            ),
        )

        legend_map = {
            "Inside top-right": dict(showlegend=True, legend=dict(x=0.98,y=0.98,xanchor="right",yanchor="top")),
            "Inside top-left":  dict(showlegend=True, legend=dict(x=0.02,y=0.98,xanchor="left", yanchor="top")),
            "Outside right":    dict(showlegend=True, legend=dict(x=1.02,y=0.5, xanchor="left", yanchor="middle")),
            "Hidden":           dict(showlegend=False),
        }
        lp = st.session_state[_key(key_prefix,"legend_pos")]
        fig.update_layout(**legend_map.get(lp, {}))

        # ── Download buttons ──────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        dl1, dl2, dl3 = st.columns(3)

        fmt = st.session_state[_key(key_prefix,"export_fmt")]
        dpi = int(st.session_state[_key(key_prefix,"dpi")])

        with dl1:
            try:
                img_bytes = fig.to_image(format=fmt.lower(), scale=dpi/96)
                st.download_button(
                    f"Download {fmt} ({dpi} DPI)",
                    data=img_bytes,
                    file_name=f"venuviz_figure.{fmt.lower()}",
                    mime=f"image/{fmt.lower()}",
                    key=f"{key_prefix}_dl_single",
                )
            except Exception:
                # Fallback: offer HTML download if kaleido missing
                html_str = fig.to_html(include_plotlyjs="cdn")
                st.download_button(
                    "Download interactive HTML",
                    data=html_str.encode(),
                    file_name="venuviz_figure.html",
                    mime="text/html",
                    key=f"{key_prefix}_dl_html",
                )
                st.caption("Install kaleido for PNG/SVG: add `kaleido` to requirements.txt")

        with dl2:
            if meta:
                zip_bytes = _build_zip(fig, fmt, dpi, meta)
                st.download_button(
                    "Download full package (ZIP)",
                    data=zip_bytes,
                    file_name="venuviz_package.zip",
                    mime="application/zip",
                    key=f"{key_prefix}_dl_zip",
                )

        with dl3:
            st.markdown(
                "<small style='color:#a8c48a'>If you use this figure, please "
                "<a href='/About' style='color:#7D9D33'>cite VenuViz →</a></small>",
                unsafe_allow_html=True)

    return fig


def _build_zip(fig, fmt, dpi, meta):
    """Build ZIP containing figure + SVG + params JSON + methods text + figure legend."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # PNG or SVG
        try:
            img = fig.to_image(format=fmt.lower(), scale=dpi/96)
            zf.writestr(f"figure.{fmt.lower()}", img)
            svg = fig.to_image(format="svg")
            zf.writestr("figure.svg", svg)
        except Exception:
            html_str = fig.to_html(include_plotlyjs="cdn")
            zf.writestr("figure.html", html_str.encode())

        # Parameters JSON
        params = {
            "generated_by": "VenuViz",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "url": "https://venuviz.streamlit.app",
            **meta,
        }
        zf.writestr("parameters.json", json.dumps(params, indent=2))

        # Methods text
        methods = _generate_methods(meta)
        zf.writestr("methods.txt", methods)

        # Figure legend
        legend = _generate_legend(meta)
        zf.writestr("figure_legend.txt", legend)

    buf.seek(0)
    return buf.read()


def _generate_methods(meta):
    gene    = meta.get("gene","[GENE]")
    cancer  = meta.get("cancer","[CANCER]")
    n_t     = meta.get("n_tumor","")
    n_n     = meta.get("n_normal","")
    test    = meta.get("test","Wilcoxon rank-sum")
    cutoff  = meta.get("cutoff","median")
    dataset = meta.get("dataset","TCGA")
    surv    = meta.get("survival_type","Overall survival")
    ptype   = meta.get("plot_type","expression")

    if ptype == "survival":
        return (
            f"Gene expression and clinical data for {gene} in {cancer} were obtained from {dataset}. "
            f"Patients were stratified into high and low {gene} expression groups using the {cutoff} "
            f"expression value as the cutoff. Survival analysis was performed using the Kaplan-Meier "
            f"method. {surv} differences between groups were assessed using the log-rank test. "
            f"Hazard ratios and 95% confidence intervals were calculated using Cox proportional "
            f"hazards regression. All analyses were performed using VenuViz (venuviz.streamlit.app)."
        )
    else:
        n_str = f"n={n_t} tumor" + (f", n={n_n} normal" if n_n else "")
        return (
            f"Gene expression data for {gene} in {cancer} ({n_str}) were obtained from {dataset}. "
            f"Expression values are reported as log2(TPM+1) normalized counts. "
            f"Differential expression between groups was assessed using the {test} test. "
            f"All analyses and visualizations were performed using VenuViz "
            f"(venuviz.streamlit.app; Mekala V, 2026)."
        )


def _generate_legend(meta):
    gene    = meta.get("gene","[GENE]")
    cancer  = meta.get("cancer","[CANCER]")
    n_t     = meta.get("n_tumor","")
    n_n     = meta.get("n_normal","")
    pval    = meta.get("pvalue","")
    hr      = meta.get("hr","")
    test    = meta.get("test","Wilcoxon rank-sum")
    dataset = meta.get("dataset","TCGA")
    ptype   = meta.get("plot_type","expression")

    pval_str = f" p={pval}," if pval else ""
    hr_str   = f" HR={hr}," if hr else ""

    if ptype == "survival":
        return (
            f"Figure. Kaplan-Meier survival curve for {gene} expression in {cancer}. "
            f"Patients stratified by {gene} expression (high vs low). "
            f"Data from {dataset} (n={n_t}).{pval_str}{hr_str} log-rank test. "
            f"Shaded areas represent 95% confidence intervals. "
            f"Generated with VenuViz (venuviz.streamlit.app)."
        )
    else:
        n_str = f"n={n_t} tumor" + (f", n={n_n} normal" if n_n else "")
        return (
            f"Figure. {gene} expression in {cancer}. "
            f"Log2(TPM+1) normalized expression values from {dataset} ({n_str}).{pval_str} "
            f"{test} test. Center line: median; box limits: interquartile range (IQR); "
            f"whiskers: 1.5×IQR. Generated with VenuViz (venuviz.streamlit.app)."
        )