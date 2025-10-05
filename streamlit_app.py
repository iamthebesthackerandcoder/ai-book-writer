from __future__ import annotations

import streamlit as st

from ui.theme import set_page
from ui.components import hero, card


set_page("AI Book Writer")

hero(
    title="Craft Books with AI Co‑Authors",
    subtitle=(
        "Generate structured outlines and cinematic chapters with a coordinated"
        " team of autonomous agents."
    ),
    pills=["Multi‑agent", "Modern UI", "Local + OpenRouter"],
)

col_left, col_right = st.columns([1.5, 1])
with col_left:
    with card("What you can do"):
        st.markdown("- Plan a detailed outline from a single premise")
        st.markdown("- Generate full chapter drafts with multi‑agent orchestration")
        st.markdown("- Use local endpoints or OpenRouter with popular presets")
        st.markdown("- Download outlines and chapters instantly")

with col_right:
    with card("Get started"):
        st.markdown(
            "Configure your story and run the agents from the Generate page."
        )
        page_link = getattr(st, "page_link", None)
        if callable(page_link):
            page_link("pages/1_Generate.py", label="Start generating →", icon="✨")
        else:
            st.markdown("Use the Pages sidebar to open ‘Generate’. ✨")

with card("Tips"):
    st.caption(
        "For OpenRouter, set the OPENROUTER_API_KEY environment variable before running the app."
    )

