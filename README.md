# Film-Finder
<p align="center">
  <img src="image.png" alt="My image" width="300">
</p>

## 📌 Overview
Film-Finder is a Flask-based web application that uses an OpenAI-compatible large language model to help users find movies from partial memories, scenes, characters, tone, actors, and other hints.

The app stores conversation history in a local SQLite database and supports multi-session chat flows with persistent chat titles and message history. It is designed with a simple Web UI and server-sent events (SSE) streaming responses for smooth real-time assistant updates.



## Vector DB spec
https://www.kaggle.com/datasets/antonio23/keywords-top-100-movies
Using this dataset for mapping keywords to film 



## 🚀 Key Features
- Chat-based movie discovery assistant
- Streaming responses from an OpenAI-compatible model (`openai` client)
- Automatically persists chats and messages to SQLite
- Chat list with create, rename, delete
- Message history reconciled for model context
- Netflix search link generation for confidently detected movie title
- Configurable model + temperature + token limits via environment
- System-prompt file support (default Ukrainian fallback)

## 🧩 Architecture
- `main.py`: Entry point that creates and runs the Flask app
- `app/__init__.py`: Flask app factory
- `app/models.py`: SQLAlchemy database models (Chat, Message)
- `app/routes.py`: Flask routes and API endpoints
- `app/utils.py`: Utility functions for serialization, validation, etc.
- `app/chroma_utils.py`: ChromaDB and embedding utilities
- `app/analyzer.py`: Movie analysis and LLM interaction logic
- `config.py`: Configuration management via environment variables
- `scripts/`: Utility scripts for data ingestion and testing
- `templates/index.html`: Single-page frontend UI
- `static/app.js`: Frontend logic for API calls and SSE
- `static/styles.css`: UI styling

## ⚙️ Requirements
- Python 3.11+ recommended
- Dependencies from `requirements.txt` (Flask, Flask-SQLAlchemy, openai-client, etc.)
- Local or hosted API compatible with OpenAI chat completions (e.g., LM Studio or OpenAI)

## 🛠️ Local Setup
1. Clone repository
2. Create and activate virtual env:
   - macOS/Linux:
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
   - Windows (PowerShell):
     - `python -m venv .venv`
     - `\.venv\Scripts\Activate`
3. Install deps:
   - `pip install -r requirements.txt`
4. (Optional) Customize environment variables:
   - `SECRET_KEY`, `API_BASE`, `API_KEY`, `MODEL_NAME`, `TEMPERATURE`, `MAX_TOKENS`, `SYSTEM_PROMPT_PATH`, `DATABASE_URL`
5. (Optional) Ingest movie data into ChromaDB:
   - `python -m app.scripts.ingest_movies`
6. Run app:
   - `python -m app`
7. Open `http://127.0.0.1:5000` in browser

## 🧾 Devcontainer
This repository includes devcontainer support for Visual Studio Code Remote - Containers.

1. Install VS Code + Remote - Containers extension.
2. Open folder in Container: `Remote-Containers: Reopen in Container`.
3. Container includes Python, dependencies and extensions configured by `.devcontainer`.
4. From within container:
   - `python app/main.py`
5. Open `http://127.0.0.1:5000` after container starts (port forwarding may be required).

## 🔧 Environment Variables (config.py)
- `SECRET_KEY`: Flask session key (default: `change-this-secret-key`)
- `API_BASE`: LLM API base URL (default: `http://127.0.0.1:1234/v1`)
- `API_KEY`: LLM API key (default: `lm-studio`)
- `MODEL_NAME`: model path/name (default: `google/gemma-3-4b`)
- `TEMPERATURE`: float, default `0.4`
- `MAX_TOKENS`: integer, default `700`
- `SYSTEM_PROMPT_PATH`: path to system prompt file (default `system-prompt.txt`)
- `DATABASE_URL`: SQLAlchemy URL (default `sqlite:///movie_finder.db`)

## 🗂️ DB Schema
- `Chat`: id (UUID), client_id (browser session), title, created_at, updated_at
- `Message`: id, chat_id FK, role (`user`/`assistant`), content, created_at

## 🔗 API Endpoints
The app serves frontend at `/` (Flask template `index.html`). All JSON APIs are under `/api` blueprint.

### GET `/api/chats`
- List chats for current browser session (by session client ID).
- Response: `{ "chats": [{ ... }] }`

### POST `/api/chats`
- Create new chat with optional JSON payload:
  - `{ "title": "..." }` (default: `Новий чат`).
- Response: `{ "chat": { ... } }`, status `201`.

### GET `/api/chats/<chat_id>/messages`
- Load chat metadata + messages for a given `chat_id`.
- Response includes `chat` and `messages` arrays.

### PATCH `/api/chats/<chat_id>`
- Rename chat with JSON `{ "title": "new title" }`.
- Returns updated `chat` object.

### DELETE `/api/chats/<chat_id>`
- Delete chat and related messages.
- Returns `{ "status": "deleted" }`.

### POST `/api/chats/<chat_id>/stream`
- Send user message and stream model response via SSE.
- Request JSON: `{ "message": "..." }`.
- SSE events: `chat`, `user_message`, `analysis`, `retrieval`, `token`, `done`, `error`.
- Final `done` event includes `assistant_message` and optional `netflix_search_url`.

## 🎯 Model Prompt Logic
- System prompt loaded from `config.SYSTEM_PROMPT_PATH` or default:
  `Ти корисний асистент з пошуку фільмів.`
- History is aggregated as messages from DB plus system prompt.
- Output streaming set through SSE events: `chat`, `user_message`, `token`, `done`, `error`.

## 🧠 Extracting Film Title
- The helper `extract_high_confidence_title` parses assistant text for `Назва:` line in the form of:
  - `Назва: ...`
  - `Рік: ...` (optional)
  - `Чому це підходить: ...` (optional)
- If found, `build_tmdb_search_url` returns: `https://www.netflix.com/search?q=<title>`.

## 🖥️ UI Behavior
- Sidebar: list chats + new-chat button
- Main view: chat title, description hint, past messages, composer
- Controls: rename/delete chat, send message, line breaks with Shift+Enter
- Extra panel for inferred Netflix link appears after each assistant answer

## 🧪 Troubleshooting
- `sqlite` file path if relating to `DATABASE_URL`; ensure directory writable
- `OpenAI` client errors: verify `API_BASE` and `API_KEY` for your LLM backend
- SSE stream freeze: watch browser network tab for event framing and Dot instead of chunk
- Model returns poor results: tune `TEMPERATURE` lower (0.2-0.6) and increase system prompt specificity

## 🧾 Extending the App
- Add user authentication, per-account chat isolation instead of session cookie
- Add external search engines (IMDb, TMDB) using extracted titles
- Provide conversation analytics (hit rate / known title accuracy)
- Add tests for endpoints (pytest, Flask test client)
- Dockerize for production with `docker-compose` and persistent service volume

## ℹ️ License
Add your desired license, e.g., MIT.
