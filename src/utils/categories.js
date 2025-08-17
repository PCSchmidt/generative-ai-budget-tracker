// Category utilities: color palette, icons, helpers

export const CATEGORY_META = {
  'Food & Dining': { color: '#3b82f6', bg: '#eff6ff', icon: '🍽️' },
  Transportation: { color: '#f97316', bg: '#fff7ed', icon: '🚗' },
  Entertainment: { color: '#8b5cf6', bg: '#f5f3ff', icon: '🎬' },
  Utilities: { color: '#6366f1', bg: '#eef2ff', icon: '💡' },
  Housing: { color: '#0ea5e9', bg: '#f0f9ff', icon: '🏠' },
  Healthcare: { color: '#059669', bg: '#ecfdf5', icon: '🏥' },
  Shopping: { color: '#d946ef', bg: '#fdf4ff', icon: '🛍️' },
  Other: { color: '#64748b', bg: '#f1f5f9', icon: '💳' }
};

export const ALL_CATEGORIES = Object.keys(CATEGORY_META);

export function getCategoryMeta(category) {
  return CATEGORY_META[category] || CATEGORY_META['Other'];
}

export function buildCategoryBreakdown(expenses = []) {
  const breakdown = {};
  for (const e of expenses) {
    const cat = e.category || 'Other';
    breakdown[cat] = (breakdown[cat] || 0) + (e.amount || 0);
  }
  return breakdown;
}

export function formatCurrency(amount) {
  return `$${Number(amount || 0).toFixed(2)}`;
}

export function getCategoryIcon(category) {
  return getCategoryMeta(category).icon;
}
