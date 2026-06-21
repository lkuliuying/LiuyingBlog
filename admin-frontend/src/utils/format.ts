export function formatDate(value?: string | null, withTime = true) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    ...(withTime ? { hour: '2-digit', minute: '2-digit', hour12: false } : {}),
  }).format(date)
}

export function compactNumber(value: number) {
  return new Intl.NumberFormat('zh-CN', { notation: 'compact' }).format(value || 0)
}

