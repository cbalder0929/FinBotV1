import json
import logging
import os

import anthropic

from app.models.transaction import EnrichedTransaction, RawTransaction
from app.services import category_cache
from app.services.categorizer import (
    CATEGORY_EMOJIS,
    category_emoji,
    clean_merchant,
    rule_based_category,
)

log = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """You are FinBot, a financial data analyst. You receive raw transaction descriptions from bank and credit card statements. Your job is to:
1. Clean up the merchant name (remove transaction IDs, location codes, trailing numbers)
2. Assign a category from: [Food, Dining, Transport, Cannabis, Utilities, Shopping, Health, Entertainment, Income, Other]
3. Write a short human-readable note (max 10 words) about what the purchase likely was

Category guidelines:
- Dispensary / Sunnyside / Zen Leaf / Cresco / MedMen -> Cannabis
- Mariano's / Whole Foods / ALDI / Jewel / Costco / Trader Joe's -> Food
- Uber / Lyft / CTA Ventra / Greyhound / Amtrak -> Transport
- Portillo's / Geja's / Avec / Chipotle / Starbucks -> Dining
- ComEd / AT&T / Comcast / Nicor / Verizon / T-Mobile -> Utilities
- Amazon / Target / Walmart / Macy's / Best Buy -> Shopping
- CVS / Walgreens / hospital / doctor / dental -> Health
- Netflix / Spotify / AMC / Steam / Ticketmaster -> Entertainment
- Direct Deposit / Payroll / Venmo received / Zelle received -> Income
- Government fees / misc / unclear -> Other

Return ONLY a valid JSON array. No preamble. No markdown fences. No explanation.
Schema: [{ "merchant": str, "category": str, "subcategory": str|null, "note": str }]"""


def _from_cache(txn: RawTransaction, hit: dict) -> EnrichedTransaction:
    """Build an EnrichedTransaction from a cached classification."""
    category = hit.get("category", "Other")
    if category not in CATEGORY_EMOJIS:
        category = "Other"
    return EnrichedTransaction(
        date=txn.date,
        description=txn.description,
        amount=txn.amount,
        balance=txn.balance,
        merchant=hit.get("merchant", clean_merchant(txn.description)),
        category=category,
        subcategory=hit.get("subcategory"),
        emoji=category_emoji(category),
        note=hit.get("note", "Cached merchant lookup"),
        flagged=False,
    )


def _from_rule(txn: RawTransaction, category: str, emoji: str) -> EnrichedTransaction:
    """Build an EnrichedTransaction from a rule match (no API call needed)."""
    return EnrichedTransaction(
        date=txn.date,
        description=txn.description,
        amount=txn.amount,
        balance=txn.balance,
        merchant=clean_merchant(txn.description),
        category=category,
        subcategory=None,
        emoji=emoji,
        note=f"Matched by {category.lower()} rule",
        flagged=False,
    )


async def categorize_transactions(
    transactions: list[RawTransaction],
) -> list[EnrichedTransaction]:
    """
    Three-tier categorization to minimize API usage:

    Tier 1 — rule-based pattern match (free, instant)
    Tier 2 — persistent merchant cache (free, instant; remembers Claude's past answers)
    Tier 3 — Claude API call (only for genuinely unseen merchants)

    The result for any new merchant is then written back to the cache so we
    never spend two API calls on the same brand.
    """
    results: list[EnrichedTransaction | None] = [None] * len(transactions)
    needs_ai: list[RawTransaction] = []
    needs_ai_indexes: list[int] = []

    rule_hits = cache_hits = api_calls = 0

    for index, txn in enumerate(transactions):
        # Tier 1: rule-based
        category, emoji = rule_based_category(txn.description)
        if category != "Other":
            results[index] = _from_rule(txn, category, emoji)
            rule_hits += 1
            continue

        # Tier 2: persistent cache
        cached = category_cache.lookup(txn.description)
        if cached is not None:
            results[index] = _from_cache(txn, cached)
            cache_hits += 1
            continue

        # Tier 3: needs AI
        needs_ai.append(txn)
        needs_ai_indexes.append(index)

    if not needs_ai:
        log.info(
            "Categorized %d transactions with zero API calls (rules=%d, cache=%d).",
            len(transactions), rule_hits, cache_hits,
        )
        return [t for t in results if t is not None]

    api_calls = len(needs_ai)
    log.info(
        "Categorizing: rules=%d, cache=%d, sending %d new merchants to Claude.",
        rule_hits, cache_hits, api_calls,
    )

    client = _get_client()
    payload = [
        {"date": t.date, "description": t.description, "amount": t.amount}
        for t in needs_ai
    ]

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Categorize these transactions:\n{json.dumps(payload, indent=2)}",
            }
        ],
    )

    raw_json = message.content[0].text.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
    raw_json = raw_json.strip()

    enriched_data: list[dict] = json.loads(raw_json)

    for response_index, txn in enumerate(needs_ai):
        original_index = needs_ai_indexes[response_index]
        data = enriched_data[response_index] if response_index < len(enriched_data) else {}

        category = data.get("category", "Other")
        if category not in CATEGORY_EMOJIS:
            category = "Other"

        merchant = data.get("merchant") or clean_merchant(txn.description)
        subcategory = data.get("subcategory")
        note = data.get("note", "")

        results[original_index] = EnrichedTransaction(
            date=txn.date,
            description=txn.description,
            amount=txn.amount,
            balance=txn.balance,
            merchant=merchant,
            category=category,
            subcategory=subcategory,
            emoji=category_emoji(category),
            note=note,
            flagged=False,
        )

        # Save back to cache so the next "Starbucks" never hits the API
        category_cache.remember(
            txn.description,
            {
                "merchant": merchant,
                "category": category,
                "subcategory": subcategory,
                "note": note,
            },
        )

    return [t for t in results if t is not None]


def categorize_offline(transactions: list[RawTransaction]) -> list[EnrichedTransaction]:
    """
    Synchronous, AI-free categorization.

    Used when the API key is missing/invalid or you've hit rate limits.
    Tier 1 (rules) and Tier 2 (cache) only — anything unseen falls back to "Other".
    """
    results: list[EnrichedTransaction] = []
    for txn in transactions:
        category, emoji = rule_based_category(txn.description)
        if category != "Other":
            results.append(_from_rule(txn, category, emoji))
            continue

        cached = category_cache.lookup(txn.description)
        if cached is not None:
            results.append(_from_cache(txn, cached))
            continue

        results.append(
            EnrichedTransaction(
                date=txn.date,
                description=txn.description,
                amount=txn.amount,
                balance=txn.balance,
                merchant=clean_merchant(txn.description),
                category="Other",
                subcategory=None,
                emoji=category_emoji("Other"),
                note="Unrecognized merchant (offline mode)",
                flagged=False,
            )
        )
    return results
