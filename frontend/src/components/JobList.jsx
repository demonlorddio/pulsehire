import { useEffect, useState } from 'react'
import { listJobs } from '../api'

/* ── Helpers ────────────────────────────────────────────────────────────── */

function formatDate(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr)
  if (isNaN(d)) return dateStr
  const now = new Date()
  const diffMs = now - d
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'today'
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const SOURCE_COLORS = {
  indeed:    { bg: 'bg-amber-400/10',  text: 'text-amber-400/90',  border: 'border-amber-400/20',  icon: 'iy' },
  linkedin:  { bg: 'bg-blue-400/10',   text: 'text-blue-400/90',   border: 'border-blue-400/20',   icon: 'in' },
  glassdoor: { bg: 'bg-emerald-400/10', text: 'text-emerald-400/90', border: 'border-emerald-400/20', icon: 'gd' },
  naukri:    { bg: 'bg-sky-400/10',    text: 'text-sky-400/90',    border: 'border-sky-400/20',    icon: 'nk' },
  dice:      { bg: 'bg-violet-400/10', text: 'text-violet-400/90', border: 'border-violet-400/20', icon: 'dc' },
  remoteok:  { bg: 'bg-teal-400/10',   text: 'text-teal-400/90',   border: 'border-teal-400/20',   icon: 'ro' },
}
const DEFAULT_SOURCE = { bg: 'bg-zinc-400/10', text: 'text-zinc-400/90', border: 'border-zinc-400/20', icon: '??' }

function getSourceStyle(source) {
  return SOURCE_COLORS[(source || '').toLowerCase()] || DEFAULT_SOURCE
}

/** Highlight `skill` inside `text` — wraps matches in indigo pill badges */
function HighlightedSnippet({ text, skill }) {
  if (!text || !skill) return text ? (
    <p className="text-[11px] text-zinc-500 line-clamp-2 leading-relaxed">{text}</p>
  ) : null

  // Case-insensitive split on the skill word
  const escaped = skill.replace(/[-\/\^$*+?.()|[\]{}]/g, '\$&')
  const re = new RegExp(`(${escaped})`, 'gi')
  const parts = text.split(re)

  return (
    <p className="text-[11px] text-zinc-500 line-clamp-2 leading-relaxed">
      {parts.map((part, i) =>
        re.test(part) ? (
          <span
            key={i}
            className="inline-block rounded bg-indigo-500/15 border border-indigo-500/20
                       px-1 py-px text-indigo-300 font-medium mx-px"
          >
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </p>
  )
}

/* ── Map pin SVG ────────────────────────────────────────────────────────── */
function MapPin({ className = 'w-3 h-3' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}

/* ── Source favicon pill ────────────────────────────────────────────────── */
function SourceBadge({ source }) {
  const s = getSourceStyle(source)
  const label = (source || 'unknown').toUpperCase()
  return (
    <span className={`inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5
                       text-[9px] font-mono font-semibold uppercase tracking-wider
                       ${s.bg} ${s.text} ${s.border}`}>
      <span className="opacity-70">{s.icon}</span>
      {label}
    </span>
  )
}

/* ── Skeleton ───────────────────────────────────────────────────────────── */
function JobSkeleton() {
  return (
    <div className="glass-card p-5 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-2">
          <div className="skeleton h-3.5 w-3/4 rounded" />
          <div className="skeleton h-2.5 w-1/3 rounded" />
        </div>
        <div className="skeleton h-5 w-12 rounded-md" />
      </div>
      <div className="flex gap-2">
        <div className="skeleton h-2 w-24 rounded" />
        <div className="skeleton h-2 w-16 rounded" />
      </div>
      <div className="space-y-1.5">
        <div className="skeleton h-2 w-full rounded" />
        <div className="skeleton h-2 w-2/3 rounded" />
      </div>
    </div>
  )
}

/* ── Single job card ────────────────────────────────────────────────────── */
function JobCard({ job, index, selectedSkill }) {
  const posted = formatDate(job.posted_date)

  return (
    <a
      href={job.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block glass-card p-5
                 transition-all duration-200 ease-out
                 hover:border-indigo-500/20 hover:scale-[1.005]
                 hover:shadow-[0_0_20px_-6px_rgba(99,102,241,0.12)]
                 card-enter"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Row 1: Title + Source badge */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-zinc-100 leading-snug
                         group-hover:text-indigo-300 transition-colors truncate">
            {job.title}
          </h3>
          {job.company && (
            <p className="text-xs text-zinc-400 mt-0.5 font-medium">{job.company}</p>
          )}
        </div>
        <span className="text-[10px] text-zinc-700 group-hover:text-indigo-400/60
                         transition-colors shrink-0 mt-0.5">
          ↗
        </span>
      </div>

      {/* Row 2: Meta badges */}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {job.location && (
          <span className="inline-flex items-center gap-1 text-[11px] text-zinc-500">
            <MapPin className="w-3 h-3 text-zinc-600" />
            {job.location}
          </span>
        )}
        {posted && (
          <span className="text-[11px] text-zinc-600 font-mono">{posted}</span>
        )}
        {job.source && <SourceBadge source={job.source} />}
      </div>

      {/* Row 3: Description snippet with highlighted skill */}
      {job.description && (
        <div className="mt-3 pt-3 border-t border-white/[0.03]">
          <HighlightedSnippet text={job.description} skill={selectedSkill} />
        </div>
      )}
    </a>
  )
}

/* ── Empty state ────────────────────────────────────────────────────────── */
function EmptyState({ skill, onRefresh }) {
  return (
    <div className="py-16 flex flex-col items-center gap-4">
      {/* Decorative icon */}
      <div className="w-12 h-12 rounded-xl bg-white/[0.03] border border-white/[0.06]
                      flex items-center justify-center">
        <svg className="w-5 h-5 text-zinc-600" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
      </div>

      <div className="text-center">
        <p className="text-sm text-zinc-400">
          No listings for <span className="text-zinc-200 font-semibold">{skill}</span> yet
        </p>
        <p className="text-[11px] text-zinc-600 mt-1 font-mono">
          scrape live data to see results here
        </p>
      </div>

      {onRefresh && (
        <button
          type="button"
          onClick={onRefresh}
          className="mt-2 inline-flex items-center gap-2 rounded-lg
                     bg-indigo-500/10 border border-indigo-500/20
                     px-4 py-2 text-xs font-medium text-indigo-300
                     hover:bg-indigo-500/15 hover:border-indigo-500/30
                     transition-colors cursor-pointer"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
            <path d="M16 16h5v5" />
          </svg>
          Trigger Web Unlocker to Scrape Live Listings
        </button>
      )}
    </div>
  )
}

/* Main component */
export default function JobList({ skill, source, limit = 5, onRefresh }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!skill) { setJobs([]); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    listJobs({ skill, source, limit })
      .then((data) => { if (!cancelled) setJobs(data) })
      .catch((e) => { if (!cancelled) setError(e.message || 'Failed to load jobs') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [skill, source, limit])

  if (!skill) return null
  const jobCount = jobs.length

  return (
    <div className="glass-card p-6 mb-8">
      <div className="mb-5 flex items-end justify-between">
        <div>
          <h2 className="heading-section text-sm text-zinc-200 uppercase tracking-wider">Real Listings</h2>
          <p className="text-[11px] text-zinc-500 mt-0.5 font-mono">
            matching <span className="text-zinc-300 font-medium">{skill}</span>
            {jobCount > 0 && <span className="text-zinc-600 ml-1.5">&middot; {jobCount} {jobCount === 1 ? 'result' : 'results'}</span>}
          </p>
        </div>
      </div>
      {loading && <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <JobSkeleton key={i} />)}</div>}
      {error && !loading && <div className="py-10 text-center"><span className="text-sm text-red-400 font-mono">{error}</span></div>}
      {!loading && !error && jobCount === 0 && <EmptyState skill={skill} onRefresh={onRefresh} />}
      {!loading && !error && jobCount > 0 && (
        <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1 fade-edges">
          {jobs.map((job, i) => <JobCard key={job.id || job.url || i} job={job} index={i} selectedSkill={skill} />)}
        </div>
      )}
    </div>
  )
}
