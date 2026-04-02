# VenuViz — Precision Cancer Genomics

**An integrated cancer genomics visualization platform with publication-ready figure export.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io)

---

## What is VenuViz?

VenuViz combines four cancer genomics analyses in one platform:

1. **Gene Explorer** — Expression across tumor stages, subtypes, and normal tissue
2. **Survival Analysis** — Kaplan-Meier curves with p-value and hazard ratio
3. **Immune TME** — Single-cell immune sub-population maps linked to survival
4. **Biomarker Predictor** — ML-based immunotherapy response prediction

**Key differentiator:** Built-in publication figure editor — customize colors, fonts, resolution, and journal presets before downloading.

---

## Quick Start

```bash
git clone https://github.com/yourusername/Cancer-Portal-2026.git
cd Cancer-Portal-2026
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
venuviz/
├── app.py                    # Home page
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Theme config
├── components/
│   ├── styles.py             # Global CSS
│   ├── navbar.py             # Navigation bar
│   ├── footer.py             # Footer
│   └── figure_editor.py      # Publication figure editor
└── pages/
    ├── 1_Explorer.py         # Gene expression explorer
    ├── 2_Survival.py         # Survival analysis
    ├── 3_Immune_TME.py       # Tumor immune microenvironment
    ├── 4_Biomarker.py        # Immunotherapy predictor
    └── 5_About.py            # About + citation
```

---

## Data Sources

| Source | Description |
|--------|-------------|
| TCGA   | The Cancer Genome Atlas — 33 cancer types |
| TISCH2 | Tumor Immune Single Cell Hub — 190 scRNA-seq datasets |
| GEO    | Gene Expression Omnibus |
| CCLE   | Cancer Cell Line Encyclopedia |

---

## How to Cite

```
Mekala, V. (2026). VenuViz: An integrated cancer genomics visualization platform
with publication-ready figure export. Bioinformatics. DOI: pending
```

---

## License

MIT License — free to use, modify, and distribute.

---

## Developer

**Venugopal Mekala** — Postdoctoral Scholar, Computational Cancer Biology

For bug reports or feature requests, please open a GitHub Issue.
