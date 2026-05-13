import json
import logging
import os

import anthropic
from fastapi import APIRouter, HTTPException, Query

from app.models.transaction import EnrichedTransaction, RawTransaction
from app.services.claude_service import categorize_offline, categorize_transactions
from app.services.transaction_validation import apply_anomaly_flags

router = APIRouter()
log = logging.getLogger(__name__)

BATCH_SIZE = 50


@router.post("", response_model=list[EnrichedTransaction])
async def analyze_transactions(
    transactions: list[RawTransaction],
    offline: bool = Query(False, description="Skip Claude entirely; rules + cache only."),
):
    if not transactions:
        raise HTTPException(400, "No transactions provided")

    # Caller asked for offline mode (or no API key configured) -> never call Claude
    if offline or not os.environ.get("ANTHROPIC_API_KEY"):
        log.info("Running offline categorization (rules + cache only) for %d txns.",
                 len(transactions))
        return apply_anomaly_flags(categorize_offline(transactions))

    results: list[EnrichedTransaction] = []
    try:
        for i in range(0, len(transactions), BATCH_SIZE):
            batch = transactions[i : i + BATCH_SIZE]
            enriched = await categorize_transactions(batch)
            results.extend(enriched)
    except (anthropic.AuthenticationError, anthropic.RateLimitError,
            anthropic.PermissionDeniedError) as e:
        # API key bad / out of credits / rate-limited — degrade instead of erroring out
        log.warning(
            "Claude unavailable (%s: %s). Falling back to offline categorization.",
            type(e).__name__, e,
        )
        return apply_anomaly_flags(categorize_offline(transactions))
    except anthropic.NotFoundError as e:
        log.error("Anthropic model not found: %s", e)
        raise HTTPException(
            500,
            f"Claude model not available on this account: {e}. "
            "Check that 'claude-sonnet-4-6' is enabled at console.anthropic.com.",
        ) from e
    except anthropic.APIConnectionError as e:
        log.error("Anthropic connection error: %s", e)
        raise HTTPException(
            502,
            "Could not reach the Anthropic API. Check your internet connection.",
        ) from e
    except anthropic.APIStatusError as e:
        log.error("Anthropic API error %s: %s", e.status_code, e)
        raise HTTPException(502, f"Anthropic API error ({e.status_code}): {e.message}") from e
    except json.JSONDecodeError as e:
        log.error("Claude returned malformed JSON: %s", e)
        raise HTTPException(
            502,
            f"Claude returned malformed JSON ({e.msg}). Try clicking Analyze again.",
        ) from e
    except Exception as e:
        log.exception("Unexpected error during analysis")
        raise HTTPException(500, f"Analysis failed: {type(e).__name__}: {e}") from e

    return apply_anomaly_flags(results)
