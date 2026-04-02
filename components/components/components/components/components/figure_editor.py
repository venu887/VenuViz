import streamlit as st
import plotly.graph_objects as go
import io

JOURNAL_PRESETS = {
    "Nature / Cell":         {"font_family": "Arial",           "font_size": 8,  "dpi": 300, "show_grid": False},
    "PNAS":                  {"font_family": "Helvetica",       "font_size": 9,  "dpi": 600, "show_grid": False},
    "Bioinformatics (OUP)":  {"font_family": "Times New Roman", "font_size": 10, "dpi": 300, "show_grid": True},
    "Generic publication":   {"font_family": "Arial",           "font_size": 10, "dpi": 300, "show_grid": False},
    "Presentation / Poster": {"font_family": "Arial",           "font_size": 14, "dpi": 150, "show_grid": True},
}

PALETTES = {
    "VenuViz default":   ["#7D9D33", "#E1EAD8", "#a8c48a", "#3a5a3a", "#243d2b"],
    "Nature (red/blue)": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F"],
    "Cell (blue/orange)":["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD"],
    "Colorblind safe":   ["#0072B2", "#E69F00", "#56B4E9", "#009E73", "#F0E442"],
    "Grayscale":         ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
}

def render_figure_editor(fig: go.Figure, key_prefix: str = "fig") -> go.Figure:
    with st.expander("◈  Customize figure for publication", expanded=False):

        st.markdown("<p class='fig-editor-title'>Journal presets — one click to apply journal specifications</p>", unsafe_allow_html=True)
        preset_cols = st.columns(len(JOURNAL_PRESETS))
        for i, (name, settings) in enumerate(JOURNAL_PRESETS.items()):
            with preset_cols[i]:
                if st.button(name, key=f"{key_prefix}_preset_{i}"):
                    for k, v in settings.items():
                        st.session_state[f"{key_prefix}_{k}"] = v

        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            font_family = st.selectbox("Font family", ["Arial", "Times New Roman", "Helvetica", "Calibri"], key=f"{key_prefix}_font_family")
            font_size   = st.slider("Font size (pt)", 6, 18, st.session_state.get(f"{key_prefix}_font_size", 10), key=f"{key_prefix}_font_size_slider")
            palette_name= st.selectbox("Color palette", list(PALETTES.keys()), key=f"{key_prefix}_palette")

        with c2:
            fig_w = st.number_input("Width (px)",  400, 1600, 800,  step=50, key=f"{key_prefix}_width")
            fig_h = st.number_input("Height (px)", 300, 1200, 500,  step=50, key=f"{key_prefix}_height")
            bg    = st.selectbox("Background", ["white", "transparent", "#1B3022"], key=f"{key_prefix}_bg")

        with c3:
            show_grid   = st.toggle("Gridlines", value=st.session_state.get(f"{key_prefix}_show_grid", False), key=f"{key_prefix}_grid_toggle")
            legend_pos  = st.selectbox("Legend", ["Inside top-right", "Inside top-left", "Outside right", "Hidden"], key=f"{key_prefix}_legend")
            export_fmt  = st.selectbox("Format", ["PNG", "SVG"], key=f"{key_prefix}_format")
            dpi         = st.selectbox("DPI", [150, 300, 600], index=1, key=f"{key_prefix}_dpi_sel")

        # Apply to figure
        font_color = "#000000" if bg == "white" else "#E1EAD8"
        grid_color = "#dddddd" if bg == "white" else "#3a5a3a"

        fig.update_layout(
            width=fig_w, height=fig_h,
            paper_bgcolor=bg, plot_bgcolor=bg,
            font=dict(family=font_family, size=font_size, color=font_color),
            xaxis=dict(showgrid=show_grid, gridcolor=grid_color, linecolor=grid_color),
            yaxis=dict(showgrid=show_grid, gridcolor=grid_color, linecolor=grid_color),
        )

        legend_map = {
            "Inside top-right":  dict(showlegend=True,  legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top")),
            "Inside top-left":   dict(showlegend=True,  legend=dict(x=0.02, y=0.98, xanchor="left",  yanchor="top")),
            "Outside right":     dict(showlegend=True,  legend=dict(x=1.02, y=0.5,  xanchor="left",  yanchor="middle")),
            "Hidden":            dict(showlegend=False),
        }
        fig.update_layout(**legend_map.get(legend_pos, {}))

        st.markdown("<br>", unsafe_allow_html=True)
        dl1, dl2 = st.columns([2, 3])
        with dl1:
            try:
                img_bytes = fig.to_image(format=export_fmt.lower(), scale=dpi/96)
                st.download_button(
                    f"Download figure ({export_fmt}, {dpi} DPI)",
                    data=img_bytes,
                    file_name=f"venuviz_figure.{export_fmt.lower()}",
                    mime=f"image/{export_fmt.lower()}",
                    key=f"{key_prefix}_dl_btn",
                )
            except Exception:
                st.info("Install kaleido for image export: pip install kaleido")
        with dl2:
            st.markdown(
                "<small style='color:#a8c48a'>If you use this figure, please <a href='/About' style='color:#7D9D33'>cite VenuViz →</a></small>",
                unsafe_allow_html=True,
            )

    return fig
