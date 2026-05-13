import io
import re
import logging
from app.models.transaction import RawTransaction

try:
    import pdfplumber
    _HAS_PDFPLUMBER = True
except ImportError:
    _HAS_PDFPLUMBER = False

log = logging.getLogger(__name__)

# Regex patterns to try, ordered most-specific to least.
# Each pattern must capture: (date, description, amount, optional balance).
_PATTERNS: list[re.Pattern] = [
    # MM/DD/YYYY or MM/DD/YY or MM-DD-YYYY  →  description  →  amount  →  optional balance
    re.compile(
        r"(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)"     # date
        r"\s+(.+?)"                                     # description (lazy)
        r"\s+(-?\$?[\d,]+\.\d{2}|\(\$?[\d,]+\.\d{2}\)|\$?[\d,]+\.\d{2}-)"  # amount
        r"(?:\s+(-?\$?[\d,]+\.\d{2}|\(\$?[\d,]+\.\d{2}\)))?"               # optional balance
        r"\s*$",
        re.MULTILINE,
    ),
    # "Apr 26"  /  "Apr 26 2025"  →  description  →  amount  →  optional balance
    re.compile(
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:,?\s+\d{4})?)"
        r"\s+(.+?)"
        r"\s+(-?\$?[\d,]+\.\d{2}|\(\$?[\d,]+\.\d{2}\)|\$?[\d,]+\.\d{2}-)"
        r"(?:\s+(-?\$?[\d,]+\.\d{2}|\(\$?[\d,]+\.\d{2}\)))?"
        r"\s*$",
        re.MULTILINE | re.IGNORECASE,
    ),
    # YYYY-MM-DD  →  description  →  amount  →  optional balance
    re.compile(
        r"(\d{4}-\d{1,2}-\d{1,2})"
        r"\s+(.+?)"
        r"\s+(-?\$?[\d,]+\.\d{2}|\(\$?[\d,]+\.\d{2}\)|\$?[\d,]+\.\d{2}-)"
        r"(?:\s+(-?\$?[\d,]+\.\d{2}|\(\$?[\d,]+\.\d{2}\)))?"
        r"\s*$",
        re.MULTILINE,
    ),
]


def _clean_amount(raw: str) -> float:
    s = raw.strip()
    negative = False
    if s.startswith('(') and s.endswith(')'):
        negative = True
        s = s[1:-1]
    if s.endswith('-'):
        negative = True
        s = s[:-1]
    s = s.replace("$", "").replace(",", "").strip()
    n = float(s)
    return -abs(n) if negative else n


def _extract_full_text(content: bytes) -> str:
    parts: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            parts.append(text)
    return "\n".join(parts)


def extract_pdf_transactions(content: bytes, filename: str | None = None) -> list[RawTransaction]:
    if not _HAS_PDFPLUMBER:
        raise RuntimeError("pdfplumber is not installed. Run: pip install pdfplumber")

    full_text = _extract_full_text(content)
    if not full_text.strip():
        raise ValueError(
            f"PDF appears to be empty or image-only (no extractable text). "
            f"Try a CSV export instead, or run OCR first."
        )

    transactions: list[RawTransaction] = []
    seen_keys: set[tuple] = set()

    for pattern in _PATTERNS:
        for match in pattern.finditer(full_text):
            groups = match.groups()
            date_str, desc, amount_str = groups[0], groups[1], groups[2]
            balance_str = groups[3] if len(groups) > 3 else None

            try:
                amount = _clean_amount(amount_str)
            except ValueError:
                continue

            desc_clean = desc.strip()
            # Filter obvious non-transaction lines (page footers, totals, summaries)
            if len(desc_clean) < 2 or len(desc_clean) > 200:
                continue
            if re.search(r"^(page|total|subtotal|balance forward|ending balance|beginning balance)\b",
                         desc_clean, re.I):
                continue

            key = (date_str.strip(), desc_clean[:40], amount)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            try:
                balance = _clean_amount(balance_str) if balance_str else None
            except ValueError:
                balance = None

            transactions.append(
                RawTransaction(
                    date=date_str.strip(),
                    description=desc_clean,
                    amount=amount,
                    balance=balance,
                    source_file=filename,
                )
            )

    log.info(
        "PDF parser extracted %d transactions from %s (text length=%d)",
        len(transactions), filename, len(full_text),
    )

    if not transactions:
        # Surface a snippet of the extracted text to aid debugging
        snippet = full_text[:300].replace("\n", " | ")
        raise ValueError(
            f"Could not find any transaction rows in PDF. "
            f"Extracted {len(full_text)} characters of text but no rows matched. "
            f"First 300 chars: {snippet!r}. "
            f"This bank's layout may not be supported — try the CSV export instead."
        )

    return transactions

