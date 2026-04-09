# Film-Finder

Film-Finder is a Flask web app that helps identify movies from incomplete memories.
It combines:
- chat history persisted in SQLite,
- retrieval from a local Chroma collection,
- generation with an OpenAI-compatible chat completion API,
- SSE streaming to the browser UI.

## Dataset
- Source: https://www.kaggle.com/datasets/antonio23/keywords-top-100-movies
- File used by ingestion script: `datasets/keywords_top100_movies.json`

## Key Features
- Multi-chat session flow with create, rename, and delete
- Movie signal extraction from full user history
- Retrieval gating by confidence and keyword count
- Chroma vector search with sentence-transformers embeddings
- Streaming assistant output via SSE (`token`, `done`, `error`)
- Auto-generated TMDB search link when title is detected (`tmdb_search_url`)

## Project Structure
- `app/main.py`: app entrypoint
- `app/__init__.py`: Flask app factory and SQLAlchemy init
- `app/routes.py`: REST + SSE endpoints
- `app/models.py`: `Chat` and `Message` models
- `app/analyzer.py`: analysis logic and prompt rules
- `app/chroma_utils.py`: embedding + Chroma access
- `app/utils.py`: serialization and helper utilities
- `app/static/`: frontend JS/CSS
- `app/templates/index.html`: main page
- `app/scripts/ingest_movies.py`: dataset to Chroma ingestion

## Requirements
- Python 3.11+
- Dependencies in `requirements.txt`
- OpenAI-compatible endpoint (`OPENAI_BASE_URL`) and API key (`OPENAI_API_KEY`)

## Local Run
1. Create and activate venv.
2. Install dependencies.
3. Optionally add `.env` values.
4. Ingest dataset to Chroma.
5. Start the app.

PowerShell example:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python -m app.scripts.ingest_movies
python -m app.main
```

Open: `http://127.0.0.1:5000`

## Docker Compose
Start:

```bash
docker compose up --build
```

Important runtime notes:
- App writes SQLite and Chroma data to writable paths in `/tmp` by default in compose.
- Hugging Face cache paths are also configured under `/tmp/film_finder_cache`.

## Environment Variables
Configured in `app/config.py`.

- `SECRET_KEY` (default: `change-this-secret-key`)
- `OPENAI_BASE_URL` or fallback `API_BASE`
- `OPENAI_API_KEY` or fallback `API_KEY`
- `MODEL_NAME` (default: `gemma3:27b`)
- `TEMPERATURE` (default: `0.4`)
- `MAX_TOKENS` (default: `700`)
- `SYSTEM_PROMPT_PATH` (default: `<repo>/system-prompt.txt`)
- `DATABASE_URL` (default: `sqlite:////tmp/movie_finder.db`)
- `CHROMA_PATH` (default: `<repo>/chroma_movies`, with writable fallback to temp)
- `COLLECTION_NAME` (default: `movies`)
- `EMBEDDING_MODEL` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `RETRIEVAL_TOP_K` (default: `5`)
- `HF_TOKEN` (recommended for higher Hugging Face limits)
- `APP_CACHE_DIR`, `HF_HOME`, `HF_HUB_CACHE`, `TRANSFORMERS_CACHE`, `SENTENCE_TRANSFORMERS_HOME`

The config includes writable-path fallback logic for read-only environments.

## API

### `GET /api/chats`
Returns chats for current browser session.

### `POST /api/chats`
Creates chat. Optional body: `{ "title": "..." }`.

### `GET /api/chats/<chat_id>/messages`
Returns chat metadata and messages.

### `PATCH /api/chats/<chat_id>`
Renames chat. Body: `{ "title": "new title" }`.

### `DELETE /api/chats/<chat_id>`
Deletes chat and its messages.

### `POST /api/chats/<chat_id>/stream`
Body: `{ "message": "..." }`

SSE events emitted:
- `chat`
- `user_message`
- `analysis`
- `retrieval`
- `token`
- `done`
- `error`

`done` payload includes:
- `assistant_message`
- `detected_title`
- `tmdb_search_url`

## Retrieval and Answering Flow
1. Analyzer extracts structured signals from user messages only.
2. Retrieval is used when confidence is:
    - `high`, or
    - `medium` with at least 5 aggregated keywords.
3. Retrieved candidates are injected into final model prompt.
4. Assistant response is streamed and persisted.
5. If `Title: ...` is found, a TMDB search URL is generated.

## Troubleshooting
- Read-only filesystem errors:
   use temp-backed paths (`/tmp`) for DB, Chroma, and caches.
- Hugging Face warning about unauthenticated requests:
   set `HF_TOKEN` to improve limits/speed.
- Empty or weak retrieval:
   check ingestion and tune prompt/query quality.

## License
Add your preferred license (for example: MIT).
