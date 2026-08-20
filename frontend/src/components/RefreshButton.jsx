import { useState } from 'react'
import { triggerRefresh } from '../api'

export default function RefreshButton({ onRefreshed, source = 'indeed' }) {
  const [state, setState] = useState('idle')
  const [message, setMessage] = useState('')

  async function handleClick() {
    setState('loading')
    setMessage('')
    try {
      const result = await triggerRefresh({ source })
      setState('done')
      setMessage(
        result.jobs_new > 0
          ? `${result.jobs_scraped} scraped, ${result.jobs_new} new`
          : `${result.jobs_scraped} checked, no new`
      )
      onRefreshed?.()
      setTimeout(() => setState('idle'), 4000)
    } catch (e) {
      setState('error')
      setMessage(e?.response?.data?.detail || e.message || 'Failed')
      setTimeout(() => setState('idle'), 6000)
    }
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={handleClick}
        disabled={state === 'loading'}
        className={`
          inline-flex items-center gap-2 rounded px-4 py-1.5 text-xs font-medium font-mono
          transition-colors duration-150 disabled:opacity-60 border
          ${state === 'idle' ? 'bg-surface-2 border-surface-3 text-zinc-300 hover:bg-surface-3 hover:text-zinc-100' : ''}
          ${state === 'loading' ? 'bg-surface-2 border-accent/30 text-accent' : ''}
          ${state === 'done' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : ''}
          ${state === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' : ''}
        `}
      >
        <span className={state === 'loading' ? 'spin' : ''}>
          {state === 'loading' ? '○' : state === 'done' ? '✓' : state === 'error' ? '✕' : '↻'}
        </span>
        {state === 'loading'
          ? `scraping ${source}...`
          : 'refresh'
        }
      </button>
      {message && (
        <span className={`text-[11px] font-mono max-w-[200px] truncate ${
          state === 'error' ? 'text-red-400' : state === 'done' ? 'text-emerald-400' : 'text-zinc-500'
        }`}>
          {message}
        </span>
      )}
    </div>
  )
}
