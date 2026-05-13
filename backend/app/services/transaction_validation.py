from collections import defaultdict

from app.models.transaction import EnrichedTransaction


FLAG_MULTIPLIER = 2.0
MIN_CATEGORY_SAMPLES = 2


def apply_anomaly_flags(
    transactions: list[EnrichedTransaction],
) -> list[EnrichedTransaction]:
    """
    Flag unusually large outflows using deterministic category averages.

    Income and credits are excluded because this flag is intended to surface
    spending anomalies in expense categories.
    """
    outflows_by_category: dict[str, list[float]] = defaultdict(list)
    for transaction in transactions:
        if transaction.amount < 0:
            outflows_by_category[transaction.category].append(abs(transaction.amount))

    averages = {
        category: sum(amounts) / len(amounts)
        for category, amounts in outflows_by_category.items()
        if len(amounts) >= MIN_CATEGORY_SAMPLES
    }

    for transaction in transactions:
        average = averages.get(transaction.category)
        transaction.flagged = (
            transaction.amount < 0
            and average is not None
            and abs(transaction.amount) > average * FLAG_MULTIPLIER
        )

    return transactions
