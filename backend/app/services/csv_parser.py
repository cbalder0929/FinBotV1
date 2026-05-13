import io
import re
from app.models.transaction import RawTransaction

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False


# Column-name keyword aliases (substring match, case-insensitive).
# Order matters: more-specific matches should appear first.
_DATE_KEYWORDS    = ['transaction date', 'trans date', 'posted date', 'posting date', 'post date', 'date']
_DESC_KEYWORDS    = ['transaction description', 'description', 'memo', 'details', 'payee', 'merchant', 'name']
_AMOUNT_KEYWORDS  = ['transaction amount', 'amount', 'charge']
_DEBIT_KEYWORDS   = ['debit', 'withdrawal', 'payment', 'charge']
_CREDIT_KEYWORDS  = ['credit', 'deposit']
_BALANCE_KEYWORDS = ['running balance', 'available balance', 'balance']


def _find_col(df_cols: list[str], keywords: list[str]) -> str | None:
    """Find the first column whose name (lowercased) contains any keyword."""
    lowered = {c.lower().strip(): c for c in df_cols}
    # Try exact match first
    for kw in keywords:
        if kw in lowered:
            return lowered[kw]
    # Then substring match
    for kw in keywords:
        for low, orig in lowered.items():
            if kw in low:
                return orig
    return None


def _read_csv_smart(content: bytes) -> 'pd.DataFrame':
    """
    Read CSV with header-row detection. Some bank exports include a few
    title/summary rows above the actual table. Try a few skiprows values.
    """
    raw = content.decode('utf-8-sig', errors='replace')

    # Try increasing skiprows until we find a header that looks like transactions
    for skip in range(0, 8):
        try:
            df = pd.read_csv(io.StringIO(raw), skiprows=skip)
        except Exception:
            continue
        cols_lower = ' '.join(str(c).lower() for c in df.columns)
        if any(k in cols_lower for k in ['date', 'description', 'amount', 'memo', 'debit', 'credit']):
            return df

    # Fall back: just read with default
    return pd.read_csv(io.StringIO(raw))


def _to_float(val) -> float | None:
    """Parse a money string. Handles $, commas, parentheses-as-negative, trailing minus."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ('nan', 'none', 'null', '-'):
        return None
    # Parentheses denote negative: (123.45) → -123.45
    negative = False
    if s.startswith('(') and s.endswith(')'):
        negative = True
        s = s[1:-1]
    # Trailing minus: 123.45-
    if s.endswith('-'):
        negative = True
        s = s[:-1]
    s = s.replace('$', '').replace(',', '').strip()
    try:
        n = float(s)
        return -abs(n) if negative else n
    except ValueError:
        return None


def extract_csv_transactions(content: bytes, filename: str | None = None) -> list[RawTransaction]:
    if not _HAS_PANDAS:
        raise RuntimeError("pandas is not installed. Run: pip install pandas")

    df = _read_csv_smart(content)
    df.columns = [str(c).strip() for c in df.columns]
    cols = df.columns.tolist()

    date_col    = _find_col(cols, _DATE_KEYWORDS)
    desc_col    = _find_col(cols, _DESC_KEYWORDS)
    amount_col  = _find_col(cols, _AMOUNT_KEYWORDS)
    debit_col   = _find_col(cols, _DEBIT_KEYWORDS) if not amount_col else None
    credit_col  = _find_col(cols, _CREDIT_KEYWORDS) if not amount_col else None
    balance_col = _find_col(cols, _BALANCE_KEYWORDS)

    # Avoid amount/debit/credit double-binding to the same column
    if debit_col == amount_col:
        debit_col = None
    if credit_col == amount_col:
        credit_col = None

    if not date_col or not desc_col or not (amount_col or debit_col or credit_col):
        raise ValueError(
            f"Could not identify required columns in CSV. "
            f"Found columns: {cols}. "
            f"Need a date column, a description column, and either an amount column "
            f"or separate debit/credit columns."
        )

    transactions: list[RawTransaction] = []
    for _, row in df.iterrows():
        try:
            date_val = row.get(date_col)
            desc_val = row.get(desc_col)
            if pd.isna(date_val) or pd.isna(desc_val):
                continue

            # Resolve amount
            if amount_col:
                amount = _to_float(row.get(amount_col))
            else:
                debit  = _to_float(row.get(debit_col))  if debit_col  else None
                credit = _to_float(row.get(credit_col)) if credit_col else None
                if debit and debit > 0:
                    amount = -debit  # debits are outflows
                elif credit and credit > 0:
                    amount = credit
                else:
                    amount = debit if debit is not None else credit

            if amount is None:
                continue

            balance = _to_float(row.get(balance_col)) if balance_col else None

            transactions.append(
                RawTransaction(
                    date=str(date_val).strip(),
                    description=str(desc_val).strip(),
                    amount=amount,
                    balance=balance,
                    source_file=filename,
                )
            )
        except Exception:
            continue  # skip malformed rows but keep parsing

    return transactions
