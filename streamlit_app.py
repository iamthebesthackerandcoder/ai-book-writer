from __future__ import annotations

import streamlit as st

from ui.theme import set_page


set_page("AI Book Writer")

st.title("AI Book Writer")
st.write("Generate structured outlines and chapters from a single idea.")

# Prefer a direct link to the Generate page; fall back to instructions.
page_link = getattr(st, "page_link", None)
if callable(page_link):
    st.page_link("pages/1_Generate.py", label="Start Generating", icon="📝")
else:
    st.info("Open the '1_Generate' page from the sidebar to start.")

