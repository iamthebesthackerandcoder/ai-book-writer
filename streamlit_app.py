from html import escape
from pathlib import Path
import os

import streamlit as st
from generation_service import run_generation

st.set_page_config(page_title="AI Book Writer", page_icon=":books:", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        color-scheme: dark;
    }

    .stApp {
        background: radial-gradient(circle at 20% 20%, rgba(79, 70, 229, 0.18), transparent 55%),
                    radial-gradient(circle at 80% 0%, rgba(236, 72, 153, 0.16), transparent 45%),
                    #0b1220;
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 3.5rem;
        padding-bottom: 4rem;
        max-width: 1100px;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }

    p, li, label, span {
        color: #cbd5f5;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(236, 72, 153, 0.12));
        padding: 2.75rem;
        border-radius: 28px;
        border: 1px solid rgba(148, 163, 184, 0.32);
        box-shadow: 0 25px 65px rgba(15, 23, 42, 0.35);
    }

    .hero-card h1 {
        font-size: 2.8rem;
        margin-bottom: 0.75rem;
        color: #f8fafc;
    }

    .hero-card p {
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        color: rgba(226, 232, 240, 0.9);
    }

    .hero-eyebrow {
        font-size: 0.85rem;
        letter-spacing: 0.25rem;
        text-transform: uppercase;
        color: rgba(148, 163, 184, 0.9);
        margin-bottom: 1.2rem;
        display: inline-block;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }

    .hero-pill {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(148, 163, 184, 0.35);
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        font-size: 0.85rem;
        color: #e2e8f0;
    }

    .hero-side {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1.5rem 1.75rem;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 24px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        backdrop-filter: blur(18px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .hero-side h3 {
        font-size: 1.1rem;
        margin: 0;
        color: #f1f5f9;
    }

    .hero-side ul {
        padding-left: 1.1rem;
        margin: 0;
        color: rgba(226, 232, 240, 0.85);
        font-size: 0.95rem;
    }

    .section-caption {
        margin: 2.5rem 0 1.5rem;
        font-size: 1.05rem;
        color: rgba(203, 213, 225, 0.92);
    }

    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.72);
        border-radius: 22px;
        padding: 2.25rem 2.5rem;
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.35);
    }

    div[data-testid="stForm"] label {
        font-weight: 600;
        color: #e2e8f0;
    }

    textarea, input, select {
        border-radius: 14px !important;
    }

    div[data-baseweb="toggle"] {
        margin-top: 0.35rem;
    }

    .stButton button, .stDownloadButton button {
        border-radius: 999px;
        padding: 0.65rem 1.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.28);
    }

    .stButton button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #7c3aed, #22d3ee);
    }

    .stDownloadButton button {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #cbd5f5;
    }

    .stDownloadButton button:hover {
        border-color: rgba(125, 211, 252, 0.7);
        color: white;
    }

    .progress-card {
        margin-top: 2.5rem;
        padding: 1.75rem 1.9rem;
        background: rgba(15, 23, 42, 0.7);
        border-radius: 22px;
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.35);
    }

    .progress-card h3 {
        margin-top: 0;
        color: #e2e8f0;
    }

    .log-entry {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.65rem 0;
        color: rgba(226, 232, 240, 0.95);
        font-size: 0.95rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }

    .log-entry:last-child {
        border-bottom: none;
    }

    .log-dot {
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #38bdf8, #a855f7);
        border-radius: 999px;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.18);
    }

    .log-text {
        flex: 1;
    }

    .tab-content {
        margin-top: 1.5rem;
    }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.63);
        padding: 0.4rem 0.8rem;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.25);
    }

    div[data-testid="stExpander"] details summary {
        font-size: 1.05rem;
        font-weight: 600;
        color: #e2e8f0;
    }

    div[data-testid="stExpander"] p {
        color: rgba(226, 232, 240, 0.84);
    }

    .stat-grid {
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }

    .stat-card {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        padding: 1.2rem 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
    }

    .stat-card .stat-label {
        color: rgba(148, 163, 184, 0.9);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .stat-card .stat-value {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 600;
    }

    .stAlert {
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.82);
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 2.2rem;
        }
        .hero-card {
            padding: 1.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "result" not in st.session_state:
    st.session_state["result"] = None
if "progress_log" not in st.session_state:
    st.session_state["progress_log"] = []
if "last_request" not in st.session_state:
    st.session_state["last_request"] = None

hero_left, hero_right = st.columns([1.8, 1])
with hero_left:
    st.markdown(
        """
        <div class="hero-card">
            <span class="hero-eyebrow">Multi-agent studio</span>
            <h1>Craft entire books with AI co-authors</h1>
            <p>Generate structured outlines and cinematic chapters with a coordinated team of autonomous agents.</p>
            <div class="hero-pills">
                <span class="hero-pill">Outline planning</span>
                <span class="hero-pill">Chapter drafting</span>
                <span class="hero-pill">Local endpoints</span>
                <span class="hero-pill">OpenRouter ready</span>
                <span class="hero-pill">Progress tracking</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown(
        """
        <div class="hero-side">
            <h3>What to expect</h3>
            <ul>
                <li>Clear outline scaffolds tailored to your premise</li>
                <li>Agents that collaborate through each chapter draft</li>
                <li>Instant downloads for outlines and finished chapters</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="section-caption">
        Configure your story premise, choose your preferred model stack, and run the agents when you're ready. The interface keeps things transparent so you can follow along as chapters take shape.
    </div>
    """,
    unsafe_allow_html=True,
)


def build_progress_markup(log_lines):
    if not log_lines:
        return ""
    entries = "".join(
        f"<div class='log-entry'><span class='log-dot'></span><span class='log-text'>{escape(line)}</span></div>"
        for line in log_lines
    )
    return f"<div class='progress-card'><h3>Activity log</h3>{entries}</div>"


def build_request_summary(request_meta):
    if not request_meta:
        return ""
    mode_text = "Full chapter drafts" if request_meta.get("generate_book") else "Detailed outline"
    chapters_text = f"{request_meta.get('chapters', 0)} chapters"
    provider_label = request_meta.get("provider", "—")
    model_label = request_meta.get("model") or "Automatic selection"
    summary = f"""
        <div class="stat-grid">
            <div class="stat-card">
                <span class="stat-label">Mode</span>
                <span class="stat-value">{escape(mode_text)}</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Chapters</span>
                <span class="stat-value">{escape(chapters_text)}</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Provider</span>
                <span class="stat-value">{escape(provider_label)}</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Model</span>
                <span class="stat-value">{escape(model_label)}</span>
            </div>
        </div>
    """
    return summary


with st.form("generation_form"):
    st.subheader("Story setup")
    prompt = st.text_area(
        "Story prompt",
        placeholder="Describe the world, characters, and the kind of story you want...",
        height=220,
    )

    st.subheader("Generation preferences")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        num_chapters = st.slider("Chapters", min_value=1, max_value=40, value=10)

    provider_options = ("Local endpoint", "OpenRouter")
    default_provider = 1 if os.getenv("OPENROUTER_API_KEY") else 0
    with col2:
        provider_choice = st.selectbox("LLM provider", provider_options, index=default_provider)
    with col3:
        generate_book = st.toggle(
            "Full chapter drafts",
            value=False,
            help="When enabled, each agent produces full chapters. Leave off for outline-only planning.",
        )

    use_openrouter = provider_choice == "OpenRouter"

    st.markdown("---")
    st.subheader("Model settings")

    if not use_openrouter:
        endpoint_input = st.text_input(
            "LLM endpoint",
            value=os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1"),
            help="Autogen-compatible base URL, e.g. LM Studio or other local server.",
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
        model_name = st.text_input(
            "OpenRouter model id",
            value=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            help="Use the OpenRouter model list endpoint to explore available models.",
        )

    submitted = st.form_submit_button("Run agents", type="primary")

log_placeholder = st.empty()

if submitted:
    sanitized_endpoint = endpoint_input.strip() if endpoint_input else None
    model_override = model_name.strip() if model_name else ""

    st.session_state["last_request"] = {
        "provider": provider_choice,
        "chapters": num_chapters,
        "generate_book": generate_book,
        "model": model_override or (
            "Automatic selection" if use_openrouter else "Server default"
        ),
    }

    st.session_state["progress_log"] = []
    log_placeholder.empty()

    def update_progress(message: str) -> None:
        st.session_state["progress_log"].append(message)
        log_markup = build_progress_markup(st.session_state["progress_log"])
        if log_markup:
            log_placeholder.markdown(log_markup, unsafe_allow_html=True)

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

if st.session_state["progress_log"]:
    log_markup = build_progress_markup(st.session_state["progress_log"])
    if log_markup:
        log_placeholder.markdown(log_markup, unsafe_allow_html=True)

result = st.session_state["result"]

if result:
    summary_markup = build_request_summary(st.session_state.get("last_request"))
    if summary_markup:
        st.markdown(summary_markup, unsafe_allow_html=True)

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
            column_count = 2 if len(chapters) > 1 else 1
            chapter_columns = st.columns(column_count)
            for index, chapter_path in enumerate(chapters):
                column = chapter_columns[index % column_count]
                with column:
                    file_path = Path(chapter_path)
                    try:
                        with file_path.open("r", encoding="utf-8") as chapter_file:
                            chapter_content = chapter_file.read()
                        st.markdown(f"**{file_path.stem.replace('_', ' ').title()}**")
                        st.download_button(
                            f"Download {file_path.name}",
                            data=chapter_content,
                            file_name=file_path.name,
                            mime="text/plain",
                        )
                    except OSError:
                        st.warning(f"Could not read {file_path}.")
        else:
            st.info("No chapters generated yet. Enable \"Full chapter drafts\" to produce full drafts.")
