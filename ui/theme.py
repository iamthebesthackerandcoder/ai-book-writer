"""
Theme setup and global styles for the Streamlit UI.

Keep this module small and focused. All functions are pure helpers that can
be re-used by pages. Files are intentionally short (<250 lines).
"""
from __future__ import annotations

import streamlit as st


def set_page(title: str = "AI Book Writer") -> None:
    """Set page configuration and apply global CSS theme."""
    st.set_page_config(page_title=title, page_icon="📚", layout="wide")
    _inject_global_css()


def _inject_global_css() -> None:
    css = r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root { color-scheme: dark; }

    .stApp {
        background: radial-gradient(1200px 600px at 10% 0%, rgba(99,102,241,.12), transparent),
                    radial-gradient(900px 500px at 85% 10%, rgba(236,72,153,.10), transparent),
                    #0c1220;
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    .main .block-container {
        max-width: 1100px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 { color: #e5e9f0; letter-spacing: -0.01em; }
    p, label, span, li { color: #cdd6f4; }

    /* Cards */
    .ui-card { background: rgba(13,18,33,.72); border: 1px solid rgba(148,163,184,.18);
               border-radius: 18px; padding: 1.25rem 1.4rem; box-shadow: 0 14px 40px rgba(2,8,23,.35); }
    .ui-card h3 { margin: 0 0 .35rem 0; color: #e5e9f0; font-size: 1.1rem; }

    /* Buttons */
    .stButton button, .stDownloadButton button {
        border-radius: 999px; padding: .6rem 1.25rem; font-weight: 600;
        border: 1px solid rgba(99,102,241,.4); background: rgba(99,102,241,.15);
        color: #e7e9ff; transition: all .2s ease; backdrop-filter: blur(6px);
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background: linear-gradient(135deg, #6366f1, #22d3ee); color: #0b1020; border-color: transparent;
        box-shadow: 0 12px 30px rgba(99,102,241,.35);
    }

    /* Forms */
    div[data-testid="stForm"] { background: rgba(13,18,33,.72); border-radius: 18px; padding: 1.25rem 1.4rem;
        border: 1px solid rgba(148,163,184,.18); box-shadow: 0 12px 32px rgba(2,8,23,.28); }
    textarea, input, select { border-radius: 12px !important; }
    div[data-baseweb="toggle"] { margin-top: .25rem; }

    /* Expander */
    div[data-testid="stExpander"] { border: 1px solid rgba(148,163,184,.18); border-radius: 14px;
        background: rgba(13,18,33,.64); padding: .25rem .6rem; }
    div[data-testid="stExpander"] summary { font-weight: 600; }

    /* Layout helpers */
    .grid { display: grid; gap: 1rem; grid-template-columns: repeat(12, 1fr); }
    .hero { background: linear-gradient(135deg, rgba(99,102,241,.22), rgba(236,72,153,.14));
            border: 1px solid rgba(148,163,184,.22); border-radius: 22px; padding: 2rem; }
    .pill { display: inline-flex; align-items: center; gap: .4rem; margin: .25rem .35rem .25rem 0;
            padding: .4rem .75rem; border-radius: 999px; border: 1px solid rgba(148,163,184,.28);
            background: rgba(2,6,23,.55); color: #e5e9f0; font-size: .85rem; }

    /* Alerts */
    .stAlert { border-radius: 14px; border: 1px solid rgba(148,163,184,.25); }

    @media (max-width: 768px) {
        .main .block-container { padding-top: 1.4rem; }
        .hero { padding: 1.25rem; }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


__all__ = ["set_page"]

