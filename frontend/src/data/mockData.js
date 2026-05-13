export const computeSummary = (transactions) => {
  const spending = transactions.filter((transaction) => transaction.amount < 0)
  const income = transactions.filter((transaction) => transaction.amount > 0)
  const total = spending.reduce((sum, transaction) => sum + Math.abs(transaction.amount), 0)

  const byCategory = {}
  spending.forEach((transaction) => {
    byCategory[transaction.category] =
      (byCategory[transaction.category] ?? 0) + Math.abs(transaction.amount)
  })

  const topCategory = Object.entries(byCategory).sort((a, b) => b[1] - a[1])[0]
  const flagged = transactions.filter((transaction) => transaction.flagged).length

  return {
    totalSpent: total,
    totalIncome: income.reduce((sum, transaction) => sum + transaction.amount, 0),
    transactionCount: transactions.length,
    topCategory: topCategory ? { name: topCategory[0], amount: topCategory[1] } : null,
    flaggedCount: flagged,
    byCategory,
  }
}
