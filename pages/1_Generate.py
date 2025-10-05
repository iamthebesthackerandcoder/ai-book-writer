from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import streamlit as st

from generation_service import run_generation
from model_presets import POPULAR_MODELS
from ui.theme import set_page


set_page("Generate | AI Book Writer")

st.title("Generate Your Book")

# Keep session state minimal
if "progress_log" not in st.session_state:
    st.session_state["progress_log"] = []
if "result" not in st.session_state:
    st.session_state["result"] = None


with st.form("generation_form"):
    prompt = st.text_area(
        "Your Story Idea",
        placeholder=(
            "Describe the world, characters, plot, genre, tone, and any specific "
            "requirements for your story..."
        ),
        height=200,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        num_chapters = st.slider("Number of Chapters", min_value=1, max_value=40, value=10)
    with col2:
        provider_choice = st.selectbox(
            "LLM Provider",
            ("Local endpoint", "OpenRouter"),
            index=1 if os.getenv("OPENROUTER_API_KEY") else 0,
        )
    with col3:
        generate_book = st.checkbox("Generate full chapter drafts", value=False)

    use_openrouter = provider_choice == "OpenRouter"

    if use_openrouter:
        if not os.getenv("OPENROUTER_API_KEY"):
            st.warning("OPENROUTER_API_KEY is not set. Set it to use OpenRouter.")
        model_options = ["Custom model..."] + list(POPULAR_MODELS.keys())
        selected = st.selectbox("Choose a model preset", options=model_options)
        if selected == "Custom model...":
            model_override = st.text_input(
                "Custom model ID",
                value=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                help="Use the full provider/model name, e.g. openai/gpt-4o-mini",
            ).strip()
        else:
            model_override = POPULAR_MODELS[selected]["id"]
        endpoint_input: Optional[str] = None
    else:
        endpoint_input = st.text_input(
            "Local LLM Endpoint",
            value=os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1"),
            help="URL of your local OpenAI-compatible server (e.g., LM Studio, Ollama)",
        ).strip()
        model_override = st.text_input(
            "Model ID",
            value=os.getenv("LOCAL_LLM_MODEL", "Mistral-Nemo-Instruct-2407"),
        ).strip()

    submitted = st.form_submit_button("Generate")

if submitted:
    st.session_state["progress_log"] = []
    log_area = st.empty()

    def update_progress(message: str) -> None:
        st.session_state["progress_log"].append(message)
        # Show last 10 messages
        lines = st.session_state["progress_log"][-10:]
        log_area.write("\n".join(lines))

    sanitized_endpoint = (endpoint_input or "").strip() or None

    try:
        with st.spinner("Working... This may take a few minutes"):
            st.session_state["result"] = run_generation(
                initial_prompt=prompt,
                num_chapters=num_chapters,
                local_url=sanitized_endpoint,
                use_openrouter=use_openrouter,
                model=model_override or None,
                generate_book=generate_book,
                progress_callback=update_progress,
            )
        st.success("Generation complete.")
    except Exception as exc:
        st.session_state["result"] = None
        st.error(f"Generation failed: {exc}")


result = st.session_state.get("result")
if result:
    st.subheader("Outline")
    outline = result.get("outline", [])
    st.caption(f"Chapters: {len(outline)}")
    for chapter in outline:
        st.markdown(f"**Chapter {chapter['chapter_number']}: {chapter['title']}**")
        st.write(chapter["prompt"])  # summary

    outline_path = result.get("outline_path")
    if outline_path:
        try:
            p = Path(outline_path)
            with p.open("r", encoding="utf-8") as fh:
                content = fh.read()
            st.download_button("Download Outline", data=content, file_name=p.name, mime="text/plain")
            st.caption(f"Saved to: {p}")
        except OSError:
            st.warning("Outline file could not be read.")

    chapters = result.get("chapters", [])
    if chapters:
        st.subheader("Chapters")
        for chapter_file in chapters:
            p = Path(chapter_file)
            try:
                with p.open("r", encoding="utf-8") as fh:
                    content = fh.read()
                st.write(p.stem.replace("_", " ").title())
                st.download_button("Download", data=content, file_name=p.name, mime="text/plain")
            except OSError:
                st.warning(f"Could not read {p}.")
