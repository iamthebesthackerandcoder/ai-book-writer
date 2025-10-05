from __future__ import annotations

import streamlit as st


def set_page(title: str = "AI Book Writer") -> None:
    """Set minimal page configuration with no extra styling."""
    st.set_page_config(
        page_title=title,
        layout="wide",
    )

