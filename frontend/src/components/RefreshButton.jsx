import { useState } from 'react'
import { triggerRefresh } from '../api'

export default function RefreshButton({ onRefreshed }) {
  const [state, setState] = useState('idle') // idle | loading | done | error
  const [message, setMessage] = useState('')

  async function handleClick() {
    setState('loading')
    setMessage('')
    try {
      const result = await triggerRefresh({ source: 'indeed' })
      setState('done')
      setMessage(`Scraped ${result.jobs_scraped} (${result.jobs_new} new)`)
      onRefreshed?.()
    } catch (e) {
      setState('error')
      const status = e?.response?.status
      const detail = e?.response?.data?.detail
      if (status === 503) {
        setMessage(detail || 'Scraper not configured (sample data still works).')
      } else {
        setMessage(e.message || 'Refresh failed.')
      }
    }
  }

  const tone =
    state === 'error' ? 'bg-rose-500/10 text-rose-300'
    : state === 'done' ? 'bg-emerald-500/10 text-emerald-300'
    : 'bg-slate-800 text-slate-200 hover:bg-slate-700'

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={handleClick}
        disabled={state === 'loading'}
        className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${tone} disabled:opacity-60`}
      >
        <span className={state === 'loading' ? 'animate-spin' : ''}>
          {state === 'loading' ? '⟳' : '🔄'}
        </span>
        {state === 'loading' ? 'Refreshing…' : 'Refresh data'}
      </button>
      {message && (
        <span className="text-xs text-slate-400">{message}</span>
      )}
    </div>
  )
}
