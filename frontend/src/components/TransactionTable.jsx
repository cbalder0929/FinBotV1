import { getCategoryMeta } from '../constants/categories'

const fmtCurrency = (n) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Math.abs(n))

const fmtDate = (iso) => {
  const [y, m, d] = iso.split('-')
  if (!y || !m || !d) return iso
  return `${m}/${d}/${y.slice(2)}`
}

function SortIcon({ col, sortConfig }) {
  if (sortConfig.key !== col) return <span className="text-slate-700 ml-1">sort</span>
  return <span className="text-accent-blue ml-1">{sortConfig.dir === 'asc' ? 'up' : 'down'}</span>
}

export default function TransactionTable({ transactions, sortConfig, onSort }) {
  const maxAbs = Math.max(...transactions.map((t) => Math.abs(t.amount)), 1)

  const cols = [
    { key: 'date', label: 'Date' },
    { key: 'merchant', label: 'Merchant' },
    { key: 'category', label: 'Category' },
    { key: 'amount', label: 'Amount' },
  ]

  return (
    <div className="overflow-x-auto -mx-4 px-4">
      <table className="w-full min-w-[760px] text-sm border-collapse">
        <thead>
          <tr className="border-b border-navy-700">
            {cols.map((col) => (
              <th
                key={col.key}
                onClick={() => onSort(col.key)}
                className={[
                  'py-2 px-3 text-xs font-mono text-slate-500 uppercase tracking-wider',
                  'cursor-pointer hover:text-slate-300 transition-colors select-none',
                  col.key === 'amount' ? 'text-right' : 'text-left',
                ].join(' ')}
              >
                {col.label}
                <SortIcon col={col.key} sortConfig={sortConfig} />
              </th>
            ))}
            <th className="w-12" />
          </tr>
        </thead>
        <tbody>
          {transactions.length === 0 && (
            <tr>
              <td colSpan={5} className="text-center text-slate-600 py-12 font-mono text-sm">
                No transactions in this category
              </td>
            </tr>
          )}
          {transactions.map((transaction, i) => {
            const meta = getCategoryMeta(transaction.category)
            const barWidth = Math.round((Math.abs(transaction.amount) / maxAbs) * 100)
            const isPositive = transaction.amount > 0

            return (
              <tr
                key={transaction.id ?? `${transaction.date}-${transaction.description}-${i}`}
                className="border-b border-navy-800 hover:bg-navy-800/50 transition-colors row-enter"
                style={{ animationDelay: `${i * 0.03}s` }}
              >
                <td className="py-3 px-3 text-slate-500 font-mono text-xs whitespace-nowrap">
                  {fmtDate(transaction.date)}
                </td>
                <td className="py-3 px-3 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-500 shrink-0 w-10">
                      {meta.icon}
                    </span>
                    <div className="min-w-0">
                      <p className="font-medium text-slate-200 truncate">{transaction.merchant}</p>
                      <p className="text-xs text-slate-500 truncate">{transaction.note}</p>
                    </div>
                  </div>
                </td>
                <td className="py-3 px-3">
                  <span className={`badge text-xs ${meta.color}`}>{transaction.category}</span>
                </td>
                <td className="py-3 px-3 text-right">
                  <div>
                    <span
                      className={`font-mono font-semibold ${
                        isPositive ? 'text-emerald-400' : 'text-slate-200'
                      }`}
                    >
                      {isPositive ? '+' : '-'}
                      {fmtCurrency(transaction.amount)}
                    </span>
                    {!isPositive && (
                      <div className="mt-1 h-1 rounded-full bg-navy-700 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-accent-blue/60"
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                    )}
                  </div>
                </td>
                <td className="py-3 px-2 text-center">
                  {transaction.flagged && (
                    <span
                      title="Unusually high amount"
                      className="inline-flex w-6 h-6 items-center justify-center rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-300 text-xs font-bold"
                    >
                      !
                    </span>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
