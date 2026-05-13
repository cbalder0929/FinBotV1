const fmtCurrency = (n) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)

export default function SummaryCards({ summary }) {
  if (!summary) return null

  const cards = [
    {
      label: 'Total Spent',
      value: fmtCurrency(summary.totalSpent),
      sub: `${summary.transactionCount} transactions`,
      icon: 'OUT',
      accent: 'border-red-500/30 bg-red-500/5',
      valueClass: 'text-red-400',
    },
    {
      label: 'Total Income',
      value: fmtCurrency(summary.totalIncome),
      sub: 'Deposits and credits',
      icon: 'IN',
      accent: 'border-emerald-500/30 bg-emerald-500/5',
      valueClass: 'text-emerald-400',
    },
    {
      label: 'Top Category',
      value: summary.topCategory?.name ?? '-',
      sub: summary.topCategory ? fmtCurrency(summary.topCategory.amount) : '',
      icon: 'TOP',
      accent: 'border-blue-500/30 bg-blue-500/5',
      valueClass: 'text-blue-400',
    },
    {
      label: 'Flagged',
      value: summary.flaggedCount,
      sub: summary.flaggedCount ? 'Unusually large amounts' : 'No anomalies detected',
      icon: 'FLAG',
      accent: summary.flaggedCount
        ? 'border-amber-500/30 bg-amber-500/5'
        : 'border-navy-600 bg-navy-800/50',
      valueClass: summary.flaggedCount ? 'text-amber-400' : 'text-slate-400',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
      {cards.map((card) => (
        <div key={card.label} className={`panel border ${card.accent} p-4 animate-slide-up`}>
          <div className="flex items-center justify-between mb-2 gap-3">
            <span className="text-xs font-mono text-slate-500 uppercase tracking-wider">
              {card.label}
            </span>
            <span className="text-[10px] font-mono text-slate-500">{card.icon}</span>
          </div>
          <p className={`text-xl font-bold font-mono ${card.valueClass}`}>{card.value}</p>
          <p className="text-xs text-slate-500 mt-1">{card.sub}</p>
        </div>
      ))}
    </div>
  )
}
