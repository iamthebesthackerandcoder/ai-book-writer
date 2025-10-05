from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import streamlit as st

from generation_service import run_generation
from model_presets import POPULAR_MODELS
from ui.theme import set_page
from ui.components import hero, card, progress_log, request_summary, downloadable_text


set_page("Generate • AI Book Writer")

hero(
    title="Generate a Book",
    subtitle="Plan outlines, orchestrate agents, and draft chapters with your chosen model stack.",
    pills=["Outline planning", "Chapter drafts", "Local or OpenRouter"],
)


# Session state
for key, default in ("result", None), ("progress_log", []), ("last_request", None):
    if key not in st.session_state:
        st.session_state[key] = default


with card("Story setup"):
    with st.form("generation_form"):
        prompt = st.text_area(
            "Story prompt",
            placeholder="Describe the world, characters, and the kind of story you want...",
            height=200,
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            num_chapters = st.slider("Chapters", 1, 40, 10)

        provider_options = ("Local endpoint", "OpenRouter")
        default_provider = 1 if os.getenv("OPENROUTER_API_KEY") else 0
        with col2:
            provider_choice = st.selectbox("LLM provider", provider_options, index=default_provider)
        with col3:
            generate_book = st.toggle(
                "Full chapter drafts",
                value=False,
                help="Enable to generate full chapter drafts; otherwise, only outline planning runs.",
            )

        use_openrouter = provider_choice == "OpenRouter"

        st.markdown("---")
        st.subheader("Model settings")

        if not use_openrouter:
            endpoint_input = st.text_input(
                "LLM endpoint",
                value=os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1"),
                help="Autogen-compatible base URL (e.g., LM Studio or another local server).",
            )
            model_name = st.text_input(
                "Model id",
                value=os.getenv("LOCAL_LLM_MODEL", "Mistral-Nemo-Instruct-2407"),
            )
        else:
            endpoint_input = None
            st.caption("Set the OPENROUTER_API_KEY environment variable before launching this app.")
            if not os.getenv("OPENROUTER_API_KEY"):
                st.warning("OPENROUTER_API_KEY is not set; requests will fail until you add it to the environment.")

            model_options = ["Custom model..."]
            model_map = {}
            for preset_key, info in POPULAR_MODELS.items():
                display = f"{preset_key} ({info['description']})"
                model_options.append(display)
                model_map[display] = info["id"]

            current = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
            selected = st.selectbox("Choose a model preset", options=model_options)

            if selected == "Custom model...":
                model_name = st.text_input(
                    "Enter custom model ID",
                    value=current,
                    help="Full OpenRouter model ID, e.g. openai/gpt-4o-mini, anthropic/claude-3-haiku",
                )
            else:
                model_name = st.text_input("Model id", value=model_map.get(selected, current))

        submitted = st.form_submit_button("Run agents", type="primary")


log_placeholder = st.empty()

if 'submitted' in locals() and submitted:
    sanitized_endpoint: Optional[str] = endpoint_input.strip() if endpoint_input else None
    model_override = model_name.strip() if model_name else ""

    st.session_state["last_request"] = {
        "provider": provider_choice,
        "chapters": num_chapters,
        "generate_book": generate_book,
        "model": model_override or ("Automatic selection" if use_openrouter else "Server default"),
    }

    st.session_state["progress_log"] = []
    log_placeholder.empty()

    def update_progress(message: str) -> None:
        st.session_state["progress_log"].append(message)
        markup = progress_log(st.session_state["progress_log"])
        if markup:
            log_placeholder.markdown(markup, unsafe_allow_html=True)

    try:
        with st.spinner("Coordinating agents..."):
            st.session_state["result"] = run_generation(
                initial_prompt=prompt,
                num_chapters=num_chapters,
                local_url=sanitized_endpoint,
                use_openrouter=use_openrouter,
                model=model_override or None,
                generate_book=generate_book,
                progress_callback=update_progress,
            )
        st.success("Generation finished. Scroll down to review the results.")
    except Exception as exc:
        st.session_state["result"] = None
        st.error(f"Generation failed: {exc}")


if st.session_state.get("progress_log"):
    markup = progress_log(st.session_state["progress_log"])
    if markup:
        log_placeholder.markdown(markup, unsafe_allow_html=True)


result = st.session_state.get("result")
if result:
    summary = request_summary(st.session_state.get("last_request"))
    if summary:
        st.markdown(summary, unsafe_allow_html=True)

    outline_tab, chapters_tab = st.tabs(["Outline", "Chapters"])

    with outline_tab:
        st.markdown("### Outline")
        for chapter in result["outline"]:
            title = f"Chapter {chapter['chapter_number']}: {chapter['title']}"
            with st.expander(title, expanded=False):
                st.markdown(chapter["prompt"]) 

        outline_path = result.get("outline_path")
        if outline_path:
            try:
                outline_file = Path(outline_path)
                with outline_file.open("r", encoding="utf-8") as handle:
                    outline_content = handle.read()
                st.download_button(
                    "Download outline",
                    data=outline_content,
                    file_name=outline_file.name,
                    mime="text/plain",
                )
            except OSError:
                st.warning("Outline file is not accessible.")

    with chapters_tab:
        st.markdown("### Chapters")
        chapters = result.get("chapters", [])
        if chapters:
            col_count = 2 if len(chapters) > 1 else 1
            columns = st.columns(col_count)
            for idx, chapter_path in enumerate(chapters):
                column = columns[idx % col_count]
                with column:
                    file_path = Path(chapter_path)
                    try:
                        with file_path.open("r", encoding="utf-8") as f:
                            content = f.read()
                        st.markdown(f"**{file_path.stem.replace('_', ' ').title()}**")
                        st.download_button(
                            f"Download {file_path.name}",
                            data=content,
                            file_name=file_path.name,
                            mime="text/plain",
                        )
                    except OSError:
                        st.warning(f"Could not read {file_path}.")
        else:
            st.info("No chapters generated yet. Enable \"Full chapter drafts\" to produce full drafts.")

