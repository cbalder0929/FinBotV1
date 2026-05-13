import logging
import os
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.transaction import RawTransaction
from app.services.csv_parser import extract_csv_transactions
from app.services.pdf_parser import extract_pdf_transactions

router = APIRouter()
log = logging.getLogger(__name__)

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024


async def _parse_file(file: UploadFile, content: bytes) -> list[RawTransaction]:
    """Route a single file to the right deterministic parser."""
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()

    if ext == "csv":
        return extract_csv_transactions(content, file.filename)

    if ext == "pdf":
        return extract_pdf_transactions(content, file.filename)

    raise HTTPException(415, f"{file.filename}: unsupported type. Upload PDF or CSV.")


@router.post("", response_model=list[RawTransaction])
async def upload_statements(files: List[UploadFile] = File(...)):
    all_transactions: list[RawTransaction] = []
    file_errors: list[str] = []

    for file in files:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                413,
                f"{file.filename}: exceeds {os.getenv('MAX_FILE_SIZE_MB', 10)} MB limit",
            )

        try:
            transactions = await _parse_file(file, content)
            log.info("Parsed %d transactions from %s", len(transactions), file.filename)
            all_transactions.extend(transactions)
        except HTTPException:
            raise
        except ValueError as e:
            log.warning("Parse error in %s: %s", file.filename, e)
            file_errors.append(f"{file.filename}: {e}")
        except Exception as e:
            log.exception("Unexpected error parsing %s", file.filename)
            file_errors.append(f"{file.filename}: unexpected error - {e}")

    if not all_transactions:
        detail = "; ".join(file_errors) if file_errors else "No transactions found in any file."
        raise HTTPException(422, detail)

    return all_transactions
