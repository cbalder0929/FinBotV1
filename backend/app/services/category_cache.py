"""
Persistent merchant categorization cache.

Once Claude has classified a merchant (e.g. "STARBUCKS"), we save the result
so the next "STARBUCKS #5678 ANYWHERE USA" transaction is matched locally
without spending another API call.

Cache is a plain JSON file at backend/cache/merchant_cache.json.
Delete that file to reset.
"""
import json
import logging
import re
from pathlib import Path
from threading import Lock

log = logging.getLogger(__name__)

# Resolve to <repo>/backend/cache/merchant_cache.json regardless of CWD
_CACHE_FILE = Path(__file__).resolve().parents[2] / "cache" / "merchant_cache.json"
_LOCK = Lock()
_CACHE: dict[str, dict] | None = None

# Words that appear in transaction descriptions but are not part of the brand
_STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "to", "for", "on", "at",
    "purchase", "payment", "pos", "debit", "credit", "card", "ach",
    "transaction", "trans", "txn", "ref", "auth",
}


def _normalize_key(description: str) -> str:
    """
    Extract a brand-style cache key from a noisy transaction description.

    "STARBUCKS #1234 CHICAGO IL 04/26"  ->  "starbucks chicago"
    "PAYMENT TO AT&T   12345"           ->  "at t"
    """
    # Lowercase, drop digits + most punctuation
    cleaned = re.sub(r"[^a-z&\s]", " ", description.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return ""

    words = [w for w in cleaned.split() if w not in _STOPWORDS]
    if not words:
        return ""

    # First two meaningful words are usually enough to identify a merchant
    return " ".join(words[:2])


def _load() -> dict[str, dict]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    with _LOCK:
        if _CACHE is not None:
            return _CACHE
        if _CACHE_FILE.exists():
            try:
                _CACHE = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                log.warning("Failed to load merchant cache (%s); starting fresh.", e)
                _CACHE = {}
        else:
            _CACHE = {}
    return _CACHE


def lookup(description: str) -> dict | None:
    """Return the cached classification for this description, or None."""
    key = _normalize_key(description)
    if not key:
        return None
    return _load().get(key)


def remember(description: str, classification: dict) -> None:
    """Persist a classification so future similar descriptions skip the API."""
    key = _normalize_key(description)
    if not key:
        return

    cache = _load()
    cache[key] = classification

    with _LOCK:
        try:
            _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
        except OSError as e:
            log.warning("Failed to persist merchant cache: %s", e)


def stats() -> dict:
    """Useful for debugging — returns cache size + sample keys."""
    cache = _load()
    return {"size": len(cache), "keys_sample": list(cache.keys())[:10]}
