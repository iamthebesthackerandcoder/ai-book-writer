from pathlib import Path
import os

import streamlit as st
from generation_service import run_generation

st.set_page_config(page_title="AI Book Writer", page_icon=":books:", layout="wide")
st.title("AI Book Writer")
st.caption("Generate structured outlines and full-length chapters with collaborative AI agents.")

if "result" not in st.session_state:
    st.session_state["result"] = None
if "progress_log" not in st.session_state:
    st.session_state["progress_log"] = []

st.markdown(
    """
    Configure your story premise, pick the chapter count, and let the agents plan the outline or draft full chapters.
    Toggle *Generate full chapters* only when you are ready for a long-running job; each chapter is written in depth.
    """
)

with st.form("generation_form"):
    prompt = st.text_area(
        "Story prompt",
        placeholder="Describe the world, characters, and the kind of story you want...",
        height=220,
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        num_chapters = st.slider("Chapters", min_value=1, max_value=40, value=10)
    provider_options = ("Local endpoint", "OpenRouter")
    default_provider = 1 if os.getenv("OPENROUTER_API_KEY") else 0
    with col2:
        provider_choice = st.selectbox("LLM provider", provider_options, index=default_provider)
    with col3:
        generate_book = st.toggle("Generate full chapters", value=False)

    model_name = ""
    endpoint_input = None
    if provider_choice == "Local endpoint":
        endpoint_input = st.text_input(
            "LLM endpoint",
            value=os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1"),
            help="Autogen-compatible base URL, e.g. LM Studio or other local server.",
        )
        model_name = st.text_input(
            "Model id",
            value=os.getenv("LOCAL_LLM_MODEL", "Mistral-Nemo-Instruct-2407"),
        )
        use_openrouter = False
    else:
        st.caption("Set the OPENROUTER_API_KEY environment variable before launching this app.")
        if not os.getenv("OPENROUTER_API_KEY"):
            st.warning("OPENROUTER_API_KEY is not set; requests will fail until you add it to the environment.")
        model_name = st.text_input(
            "OpenRouter model id",
            value=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            help="Use the OpenRouter model list endpoint to explore available models.",
        )
        use_openrouter = True
        endpoint_input = None

    submitted = st.form_submit_button("Generate", type="primary")

log_placeholder = st.empty()

if submitted:
    st.session_state["progress_log"] = []

    def update_progress(message: str) -> None:
        st.session_state["progress_log"].append(message)
        log_placeholder.markdown("\n".join(f"- {line}" for line in st.session_state["progress_log"]))

    try:
        sanitized_endpoint = endpoint_input.strip() if endpoint_input else None
        model_override = model_name.strip() or None

        with st.spinner("Coordinating agents..."):
            st.session_state["result"] = run_generation(
                initial_prompt=prompt,
                num_chapters=num_chapters,
                local_url=sanitized_endpoint,
                use_openrouter=use_openrouter,
                model=model_override,
                generate_book=generate_book,
                progress_callback=update_progress,
            )
        st.success("Generation finished. Scroll down to review the results.")
    except Exception as exc:
        st.session_state["result"] = None
        st.error(f"Generation failed: {exc}")

if st.session_state["progress_log"]:
    st.subheader("Activity Log")
    st.markdown("\n".join(f"- {line}" for line in st.session_state["progress_log"]))

result = st.session_state["result"]

if result:
    st.subheader("Outline")
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

    chapters = result.get("chapters", [])
    if chapters:
        st.subheader("Chapters")
        for chapter_path in chapters:
            file_path = Path(chapter_path)
            try:
                with file_path.open("r", encoding="utf-8") as chapter_file:
                    chapter_content = chapter_file.read()
                st.download_button(
                    f"Download {file_path.name}",
                    data=chapter_content,
                    file_name=file_path.name,
                    mime="text/plain",
                )
            except OSError:
                st.warning(f"Could not read {file_path}.")
    else:
        st.info("No chapters generated yet. Enable \"Generate full chapters\" to produce full drafts.")
