import { useState } from 'react'
import { triggerRefresh } from '../api'

export default function RefreshButton({ onRefreshed, source = 'indeed' }) {
  const [state, setState] = useState('idle') // idle | loading | done | error
  const [message, setMessage] = useState('')

  async function handleClick() {
    setState('loading')
    setMessage('')
    try {
      const result = await triggerRefresh({ source })
      setState('done')
      setMessage(
        result.jobs_new > 0
          ? `✓ Scraped ${result.jobs_scraped} jobs (${result.jobs_new} new)`
          : `✓ Checked ${result.jobs_scraped} jobs (no new results)`
      )
      onRefreshed?.()
      // Reset to idle after 4 seconds
      setTimeout(() => setState('idle'), 4000)
    } catch (e) {
      setState('error')
      const status = e?.response?.status
      const detail = e?.response?.data?.detail
      if (status === 503) {
        setMessage(detail || 'Scraper not configured (sample data still works).')
      } else {
        setMessage(e.message || 'Refresh failed. Check backend server.')
      }
      setTimeout(() => setState('idle'), 6000)
    }
  }

  const btnClasses = {
    idle:    'bg-slate-800 border-slate-700/50 text-slate-200 hover:bg-slate-700/80 hover:border-slate-600',
    loading: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300',
    done:    'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
    error:   'bg-rose-500/10 border-rose-500/30 text-rose-300',
  }

  const msgClasses = {
    idle:    'text-slate-500',
    loading: 'text-indigo-400',
    done:    'text-emerald-400',
    error:   'text-rose-400',
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={handleClick}
        disabled={state === 'loading'}
        className={`
          inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium
          transition-all duration-200 disabled:opacity-70
          ${btnClasses[state]}
        `}
      >
        <span className={state === 'loading' ? 'animate-spin-slow' : ''}>
          {state === 'loading' ? '⟳' : state === 'done' ? '✓' : state === 'error' ? '✕' : '🔄'}
        </span>
        {state === 'loading' ? `Scraping ${source.charAt(0).toUpperCase() + source.slice(1)}…` : 'Refresh data'}
      </button>
      {message && (
        <span className={`text-xs max-w-xs ${msgClasses[state]}`}>
          {message}
        </span>
      )}
    </div>
  )
}
