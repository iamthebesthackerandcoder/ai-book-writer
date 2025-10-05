"""
Reusable UI components for the app. Keep this under 250 lines.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Iterable, Mapping, Optional

import streamlit as st


def hero(title: str, subtitle: str, pills: Optional[Iterable[str]] = None) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1 style="margin:0 0 .4rem 0">{escape(title)}</h1>
            <p style="margin:.25rem 0 1rem 0; color: rgba(226,232,240,.92);">
                {escape(subtitle)}
            </p>
            <div>
                {''.join(f'<span class="pill">{escape(p)}</span>' for p in (pills or []))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: Optional[str] = None):  # context manager style
    class _Card:
        def __enter__(self, *_) -> None:
            st.markdown('<div class="ui-card">' + (f"<h3>{escape(title)}</h3>" if title else ""), unsafe_allow_html=True)

        def __exit__(self, *_):
            st.markdown("</div>", unsafe_allow_html=True)

    return _Card()


def progress_log(log_lines: Iterable[str]) -> str:
    lines = list(log_lines)
    if not lines:
        return ""
    entries = "".join(
        f"<div style='display:flex;gap:.6rem;align-items:center;padding:.45rem 0;border-bottom:1px solid rgba(148,163,184,.12)'>"
        f"<span style='width:8px;height:8px;border-radius:999px;background:linear-gradient(135deg,#38bdf8,#a855f7);box-shadow:0 0 0 4px rgba(99,102,241,.18);'></span>"
        f"<span style='flex:1'>{escape(line)}</span>"
        f"</div>"
        for line in lines
    )
    return f"<div class='ui-card'><h3>Activity</h3>{entries}</div>"


def request_summary(meta: Optional[Mapping[str, object]]) -> str:
    if not meta:
        return ""
    mode = "Full chapter drafts" if meta.get("generate_book") else "Detailed outline"
    chapters = f"{meta.get('chapters', 0)} chapters"
    provider = str(meta.get("provider", "–"))
    model = str(meta.get("model", "Automatic"))
    stat = (
        "<div style='display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));'>"
        + _stat("Mode", mode)
        + _stat("Chapters", chapters)
        + _stat("Provider", provider)
        + _stat("Model", model)
        + "</div>"
    )
    return stat


def _stat(label: str, value: str) -> str:
    return (
        "<div class='ui-card' style='padding:1rem 1.1rem'>"
        f"<div style='font-size:.82rem;color:rgba(148,163,184,.9);text-transform:uppercase;letter-spacing:.08em'>{escape(label)}</div>"
        f"<div style='font-size:1.15rem;font-weight:600;color:#eef2ff'>{escape(value)}</div>"
        "</div>"
    )


def downloadable_text(file_path: Path) -> None:
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()
        st.download_button(
            f"Download {file_path.name}",
            data=content,
            file_name=file_path.name,
            mime="text/plain",
        )
    except OSError:
        st.warning(f"Could not read {file_path}.")


__all__ = [
    "hero",
    "card",
    "progress_log",
    "request_summary",
    "downloadable_text",
]

