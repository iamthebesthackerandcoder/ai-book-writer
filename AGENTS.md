# Repository Guidelines
## Project Structure & Module Organization
Core orchestration lives at the repo root: `agents.py` defines the collaborating roles, `book_generator.py` and `outline_generator.py` drive chapter creation, and `generation_service.py` wraps LLM calls. The Streamlit surface sits in `streamlit_app.py` with supporting layouts in `pages/` and `ui/`; reusable assets stay under `assets/`. Generated manuscripts land in the git-ignored `book_output/`. Configuration is centralized in `config.py` plus `.env` files. Tests reside alongside modules (see `test_model_selection.py`).

## Build, Test, and Development Commands
Create an isolated environment with `uv venv .venv` and install dependencies via `uv pip install -r requirements.txt`. Activate the shell with `.venv\Scripts\Activate.ps1` on Windows or `source .venv/bin/activate` elsewhere. Run the end-to-end CLI using `python main.py --prompt "Describe your hero"` or launch the UI with `streamlit run streamlit_app.py`. Use `pytest` for automated checks, adding `-k` or `-vv` when iterating. Format and lint before submitting: `uv pip run black .`, `uv pip run flake8`, and `uv pip run mypy`.

## Coding Style & Naming Conventions
Follow Black defaults: 4-space indentation, 88-character lines, trailing commas where practical. Keep imports grouped standard/third-party/local. Modules and packages use `snake_case`; classes use `PascalCase`; functions, variables, and agent ids stay `snake_case`. Type annotate public functions and dataclasses, especially around agent message payloads. Do not check in artifacts outside `book_output/` or personal notebooks.

## Testing Guidelines
Pytest powers the suite. New files should follow the `test_<feature>.py` pattern with test names that describe behavior (`test_agent_handles_timeout`). Prefer fixtures in `conftest.py` for shared setup and stub external LLM calls with fakes from `generation_service`. Keep tests deterministic (seed `random` and `numpy.random`) and document any intentional gaps in coverage in your PR notes.

## Commit & Pull Request Guidelines
Commit subjects stay imperative and concise, mirroring existing history (`Add user-friendly model selection with presets`). Reference tickets in the body, not the subject. Each PR must state the change scope, list local checks (e.g., pytest, black, mypy), and attach UI screenshots when tweaking Streamlit pages. Avoid committing secrets; scrub `.env` updates and exclude `book_output/` when opening PRs.
