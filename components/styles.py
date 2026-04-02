import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Source+Serif+4:ital,wght@0,300;1,300&display=swap');

    :root {
        --bg:       #1B3022;
        --bg2:      #243d2b;
        --bg3:      #122318;
        --green:    #7D9D33;
        --green-lt: #9ab84a;
        --accent:   #E1EAD8;
        --muted:    #a8c48a;
        --border:   #3a5a3a;
        --font:     'Montserrat', sans-serif;
    }

    html, body, [class*="css"] {
        font-family: var(--font) !important;
        background-color: var(--bg) !important;
        color: var(--accent) !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 2rem 4rem 2rem !important; max-width: 1200px !important; }

    /* Navbar */
    .vv-nav { background:var(--bg3); border-bottom:1px solid var(--border); padding:0.9rem 2rem; display:flex; align-items:center; justify-content:space-between; margin:0 -2rem 2rem -2rem; }
    .vv-logo { font-size:1.4rem; font-weight:800; color:var(--accent) !important; text-decoration:none !important; }
    .vv-logo span { color:var(--green); }
    .vv-tagline { font-size:0.62rem; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase; display:block; }
    .vv-nav-links { display:flex; gap:1.8rem; align-items:center; }
    .vv-nav-links a { color:var(--muted) !important; text-decoration:none !important; font-size:0.82rem; font-weight:500; }
    .vv-nav-links a:hover { color:var(--accent) !important; }
    .vv-nav-cta { background:var(--green) !important; color:#fff !important; padding:0.35rem 1rem !important; border-radius:6px !important; font-size:0.8rem !important; }

    /* Hero */
    .hero-section { text-align:center; padding:5rem 2rem 3rem; }
    .hero-badge { display:inline-block; background:var(--bg2); border:1px solid var(--border); color:var(--muted); font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; padding:0.3rem 1rem; border-radius:20px; margin-bottom:1.5rem; }
    .hero-title { font-size:clamp(2.2rem,5vw,3.6rem); font-weight:800; color:var(--accent); line-height:1.15; margin-bottom:1.2rem; letter-spacing:-1px; }
    .hero-sub { font-size:1rem; color:var(--muted); max-width:560px; margin:0 auto 2rem; line-height:1.7; font-weight:300; }
    .hero-buttons { display:flex; gap:1rem; justify-content:center; margin-bottom:1.5rem; }
    .btn-primary { background:var(--green) !important; color:#fff !important; padding:0.75rem 2rem !important; border-radius:8px !important; font-weight:700 !important; font-size:0.9rem !important; text-decoration:none !important; }
    .btn-secondary { background:transparent !important; color:var(--green) !important; border:1.5px solid var(--green) !important; padding:0.75rem 2rem !important; border-radius:8px !important; font-weight:600 !important; font-size:0.9rem !important; text-decoration:none !important; }
    .hero-trust { font-size:0.75rem; color:var(--muted); opacity:0.7; letter-spacing:0.04em; }

    /* Stats */
    .stat-card { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:1.5rem; text-align:center; }
    .stat-value { font-size:2rem; font-weight:800; color:var(--green); letter-spacing:-1px; }
    .stat-label { font-size:0.75rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; margin-top:0.3rem; }

    /* Sections */
    .section-divider { height:1px; background:var(--border); margin:3rem 0; opacity:0.5; }
    .section-title { font-size:1.5rem; font-weight:700; color:var(--accent); margin-bottom:1.5rem; letter-spacing:-0.3px; }

    /* Feature cards */
    .feature-card { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:1.5rem; transition:border-color 0.2s,transform 0.2s; }
    .feature-card:hover { border-color:var(--green); transform:translateY(-2px); }
    .feature-icon { font-size:1.4rem; color:var(--green); margin-bottom:0.8rem; }
    .feature-title { font-size:0.95rem; font-weight:700; color:var(--accent); margin-bottom:0.6rem; }
    .feature-desc { font-size:0.82rem; color:var(--muted); line-height:1.6; margin-bottom:1rem; }
    .feature-link { font-size:0.8rem; color:var(--green) !important; text-decoration:none !important; font-weight:600; }

    /* Diff cards */
    .diff-card { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:1.5rem; text-align:center; }
    .diff-card.highlight { border-color:var(--green); background:#1e3d24; }
    .diff-icon { font-size:1.6rem; color:var(--green); margin-bottom:0.8rem; }
    .diff-card h4 { font-size:0.9rem; font-weight:700; color:var(--accent); margin-bottom:0.5rem; }
    .diff-card p { font-size:0.8rem; color:var(--muted); line-height:1.6; }

    /* Steps */
    .step-card { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:2rem 1.5rem; text-align:center; }
    .step-num { font-size:2.5rem; font-weight:800; color:var(--green); opacity:0.4; line-height:1; margin-bottom:0.8rem; }
    .step-title { font-size:1rem; font-weight:700; color:var(--accent); margin-bottom:0.5rem; }
    .step-desc { font-size:0.82rem; color:var(--muted); line-height:1.6; }

    /* Citation */
    .cite-banner { background:var(--bg2); border:1px solid var(--border); border-left:4px solid var(--green); border-radius:12px; padding:2rem; }
    .cite-banner h3 { font-size:1.1rem; font-weight:700; color:var(--accent); margin-bottom:0.5rem; }
    .cite-banner p { font-size:0.85rem; color:var(--muted); margin-bottom:1rem; }
    .cite-box { background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:1rem 1.2rem; font-size:0.82rem; color:var(--accent); font-family:'Courier New',monospace; line-height:1.6; }

    /* Developer */
    .dev-section { text-align:center; }
    .dev-bio { font-size:0.9rem; color:var(--muted); max-width:600px; margin:0 auto 1.5rem; line-height:1.7; }
    .dev-bio strong { color:var(--accent); }
    .dev-links { display:flex; gap:1rem; justify-content:center; }
    .dev-link { background:var(--bg2) !important; border:1px solid var(--border) !important; color:var(--muted) !important; padding:0.4rem 1rem !important; border-radius:6px !important; font-size:0.8rem !important; text-decoration:none !important; }
    .dev-link:hover { border-color:var(--green) !important; color:var(--green) !important; }

    /* Footer */
    .vv-footer { background:var(--bg3); border-top:1px solid var(--border); margin:4rem -2rem -4rem -2rem; padding:2rem; text-align:center; }
    .footer-links { display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center; margin-bottom:1rem; }
    .footer-links a { color:var(--muted) !important; text-decoration:none !important; font-size:0.78rem; }
    .footer-links a:hover { color:var(--accent) !important; }
    .footer-copy { font-size:0.72rem; color:var(--muted); opacity:0.6; margin-bottom:0.5rem; }
    .footer-disclaimer { font-size:0.68rem; color:var(--muted); opacity:0.45; max-width:640px; margin:0 auto; }

    /* Sidebar */
    [data-testid="stSidebar"] { background:var(--bg2) !important; border-right:1px solid var(--border) !important; }
    [data-testid="stSidebar"] label { color:var(--muted) !important; font-size:0.78rem !important; font-weight:600 !important; letter-spacing:0.04em !important; text-transform:uppercase !important; }

    /* Streamlit widgets */
    .stButton>button { background:var(--green) !important; color:#fff !important; border:none !important; border-radius:8px !important; font-family:var(--font) !important; font-weight:700 !important; }
    .stButton>button:hover { background:var(--green-lt) !important; }
    .stSelectbox>div>div, .stTextInput>div>div>input { background:var(--bg3) !important; border:1px solid var(--border) !important; color:var(--accent) !important; border-radius:6px !important; }
    .stTabs [data-baseweb="tab-list"] { background:var(--bg2) !important; border-radius:8px !important; padding:0.2rem !important; }
    .stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--muted) !important; border-radius:6px !important; font-size:0.82rem !important; font-weight:600 !important; }
    .stTabs [aria-selected="true"] { background:var(--green) !important; color:#fff !important; }

    /* Page header */
    .page-header { padding:2rem 0 1.5rem; border-bottom:1px solid var(--border); margin-bottom:2rem; }
    .page-header h1 { font-size:1.8rem; font-weight:800; color:var(--accent); margin-bottom:0.3rem; }
    .page-header p { font-size:0.9rem; color:var(--muted); line-height:1.6; }

    /* Empty state */
    .empty-state { text-align:center; padding:4rem 2rem; }
    .empty-state h3 { font-size:1rem; font-weight:600; color:var(--accent); margin-bottom:0.5rem; }
    .empty-state p { font-size:0.85rem; color:var(--muted); margin-bottom:1.5rem; }
    .pill-row { display:flex; gap:0.5rem; justify-content:center; flex-wrap:wrap; }
    .pill { background:var(--bg3); border:1px solid var(--border); color:var(--green) !important; padding:0.3rem 0.9rem; border-radius:20px; font-size:0.8rem; font-weight:600; text-decoration:none !important; }

    /* Figure editor */
    .fig-editor { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:1.2rem 1.5rem; margin-top:1rem; }
    .fig-editor-title { font-size:0.78rem; font-weight:700; color:var(--green); letter-spacing:0.06em; text-transform:uppercase; margin-bottom:1rem; }
    </style>
    """, unsafe_allow_html=True)
