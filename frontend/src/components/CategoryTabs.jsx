import { CATEGORIES } from '../constants/categories'

export default function CategoryTabs({ active, onChange, transactions }) {
  const counts = transactions.reduce((acc, t) => {
    acc[t.category] = (acc[t.category] ?? 0) + 1
    return acc
  }, {})

  const visibleCategories = CATEGORIES.filter(
    (c) => c.id === 'all' || counts[c.id],
  )

  return (
    <div className="flex flex-wrap gap-1.5">
      {visibleCategories.map((cat) => {
        const count = cat.id === 'all' ? transactions.length : (counts[cat.id] ?? 0)
        return (
          <button
            key={cat.id}
            onClick={() => onChange(cat.id)}
            className={[
              'tab flex items-center gap-1.5',
              active === cat.id ? 'tab-active' : '',
            ].join(' ')}
          >
            <span className="text-[10px] font-mono text-slate-500">{cat.icon}</span>
            <span>{cat.label}</span>
            <span
              className={`text-xs rounded-full px-1.5 py-0 font-mono ${
                active === cat.id ? 'bg-navy-600 text-slate-200' : 'bg-navy-800 text-slate-500'
              }`}
            >
              {count}
            </span>
          </button>
        )
      })}
    </div>
  )
}
