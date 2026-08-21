import { useState, useRef, useEffect } from 'react'

/**
 * Custom dark-themed dropdown that replaces native <select>.
 * Fully styled to match the glassmorphism dark theme.
 */
export default function DarkSelect({ label, value, onChange, options }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const selected = options.find((o) => o.value === value)
  const displayLabel = selected?.label || 'Select...'

  return (
    <label className="block">
      <span className="mono-label mb-1.5 block">{label}</span>
      <div ref={ref} className="relative">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="glass-flat rounded-lg px-3 py-2 text-xs text-zinc-300 w-full
                     text-left cursor-pointer transition-colors
                     hover:border-white/[0.08] focus:outline-none focus:ring-1 focus:ring-indigo-400/30
                     flex items-center justify-between gap-2"
        >
          <span className="truncate font-mono">{displayLabel}</span>
          <svg
            className={`w-3 h-3 text-zinc-500 transition-transform ${open ? 'rotate-180' : ''}`}
            viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2"
          >
            <path d="M3 4.5L6 7.5L9 4.5" />
          </svg>
        </button>

        {open && (
          <div className="absolute z-[200] mt-1 w-full rounded-lg overflow-hidden
                          bg-slate-950 border border-white/[0.12]
                          shadow-[0_8px_32px_-4px_rgba(0,0,0,0.8),0_0_0_1px_rgba(255,255,255,0.05)]
                          max-h-60 overflow-y-auto
                          animate-[fadeIn_0.15s_ease]">
            {options.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  onChange(opt.value, ref.current)
                  setOpen(false)
                }}
                className={`w-full text-left px-3 py-2.5 text-xs font-mono transition-colors cursor-pointer
                           ${opt.value === value
                             ? 'bg-indigo-500/15 text-indigo-300 border-l-2 border-indigo-400'
                             : 'text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200 border-l-2 border-transparent'
                           }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </label>
  )
}
