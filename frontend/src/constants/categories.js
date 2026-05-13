export const CATEGORIES = [
  { id: 'all', label: 'All', icon: 'All', color: 'bg-slate-600 text-slate-100' },
  { id: 'Food', label: 'Food', icon: 'Food', color: 'bg-emerald-900 text-emerald-300' },
  { id: 'Dining', label: 'Dining', icon: 'Dine', color: 'bg-orange-900 text-orange-300' },
  { id: 'Transport', label: 'Transport', icon: 'Ride', color: 'bg-blue-900 text-blue-300' },
  { id: 'Cannabis', label: 'Cannabis', icon: 'Leaf', color: 'bg-green-900 text-green-300' },
  { id: 'Utilities', label: 'Utilities', icon: 'Util', color: 'bg-yellow-900 text-yellow-300' },
  { id: 'Shopping', label: 'Shopping', icon: 'Shop', color: 'bg-pink-900 text-pink-300' },
  { id: 'Health', label: 'Health', icon: 'Med', color: 'bg-red-900 text-red-300' },
  { id: 'Entertainment', label: 'Entertainment', icon: 'Fun', color: 'bg-purple-900 text-purple-300' },
  { id: 'Income', label: 'Income', icon: 'Pay', color: 'bg-teal-900 text-teal-300' },
  { id: 'Other', label: 'Other', icon: 'Misc', color: 'bg-slate-700 text-slate-300' },
]

export const getCategoryMeta = (id) =>
  CATEGORIES.find((c) => c.id === id) ?? CATEGORIES[CATEGORIES.length - 1]
