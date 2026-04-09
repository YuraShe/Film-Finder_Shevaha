import os
import tempfile
from pathlib import Path
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_TMP_DIR = Path(tempfile.gettempdir())

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
API_BASE = os.getenv("OPENAI_BASE_URL") or os.getenv("API_BASE")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:27b")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.4"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "700"))

SYSTEM_PROMPT_PATH = os.getenv(
    "SYSTEM_PROMPT_PATH",
    str(BASE_DIR.parent / "system-prompt.txt")
)

def _is_writable_dir(path: Path) -> bool:
    """Vrátí True, pokud je adresář zapisovatelný — ověří vytvořením testovacího souboru."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _sqlite_file_from_url(db_url: str) -> Path | None:
    """Extrahuje cestu k souboru SQLite z URL SQLAlchemy, je-li to relevantní."""
    if not db_url.startswith("sqlite:///"):
        return None

    raw_path = db_url.replace("sqlite:///", "", 1)
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = BASE_DIR.parent / db_path

    return db_path


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:////data/movie_finder.db"
)

sqlite_file = _sqlite_file_from_url(DATABASE_URL)
if sqlite_file:
    if not _is_writable_dir(sqlite_file.parent):
        fallback_db = RUNTIME_TMP_DIR / "movie_finder.db"
        DATABASE_URL = f"sqlite:///{fallback_db.as_posix()}"

default_chroma_path = Path("/data/chroma_movies")
chroma_env = os.getenv("CHROMA_PATH")
CHROMA_PATH = chroma_env or str(default_chroma_path)

if not _is_writable_dir(Path(CHROMA_PATH)):
    fallback_chroma = BASE_DIR.parent / "chroma_movies"
    CHROMA_PATH = str(fallback_chroma) if _is_writable_dir(fallback_chroma) else str(RUNTIME_TMP_DIR / "chroma_movies")

CHROMA_HOST = os.getenv("CHROMA_HOST", "")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "movies")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Keep model/cache files in a writable location. Some runtimes mount /app as read-only.
HF_TOKEN = os.getenv("HF_TOKEN")


_cache_candidates = []
env_cache = os.getenv("APP_CACHE_DIR")
if env_cache:
    _cache_candidates.append(Path(env_cache))

_cache_candidates.extend(
    [
        Path("/data/film_finder_cache"),
        BASE_DIR.parent / ".cache",
        RUNTIME_TMP_DIR / "film_finder_cache",
        Path.home() / ".cache" / "film_finder",
    ]
)

APP_CACHE_DIR = next((p for p in _cache_candidates if _is_writable_dir(p)), RUNTIME_TMP_DIR)
HF_HOME = Path(os.getenv("HF_HOME", str(APP_CACHE_DIR / "huggingface")))
HF_HUB_CACHE = Path(os.getenv("HF_HUB_CACHE", str(HF_HOME / "hub")))
TRANSFORMERS_CACHE = Path(os.getenv("TRANSFORMERS_CACHE", str(HF_HOME / "transformers")))
SENTENCE_TRANSFORMERS_HOME = Path(
    os.getenv("SENTENCE_TRANSFORMERS_HOME", str(APP_CACHE_DIR / "sentence_transformers"))
)

for cache_path in (HF_HOME, HF_HUB_CACHE, TRANSFORMERS_CACHE, SENTENCE_TRANSFORMERS_HOME):
    try:
        cache_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

os.environ["HF_HOME"] = str(HF_HOME)
os.environ["HF_HUB_CACHE"] = str(HF_HUB_CACHE)
os.environ["TRANSFORMERS_CACHE"] = str(TRANSFORMERS_CACHE)
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(SENTENCE_TRANSFORMERS_HOME)
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))

client = OpenAI(base_url=API_BASE, api_key=API_KEY, timeout=30.0)