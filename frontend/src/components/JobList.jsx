import { useEffect, useState } from 'react'
import { listJobs } from '../api'

/* ── Helpers ─────────────────────────────────────────────────────────────── */

function formatDate(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr)
  if (isNaN(d)) return dateStr
  const now = new Date()
  const diffMs = now - d
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function sourceColor(source) {
  const s = (source || '').toLowerCase()
  if (s === 'indeed') return 'text-amber-400 bg-amber-400/10 border-amber-400/20'
  if (s === 'naukri') return 'text-sky-400 bg-sky-400/10 border-sky-400/20'
  return 'text-slate-400 bg-slate-400/10 border-slate-400/20'
}

/* ── Skeleton loader ────────────────────────────────────────────────────── */

function JobSkeleton() {
  return (
    <div className="rounded-xl bg-slate-800/40 border border-slate-700/30 p-4 space-y-3">
      <div className="skeleton h-4 w-3/4 rounded" />
      <div className="skeleton h-3 w-1/2 rounded" />
      <div className="flex gap-2">
        <div className="skeleton h-3 w-24 rounded" />
        <div className="skeleton h-3 w-16 rounded" />
      </div>
    </div>
  )
}

/* ── Single job card ─────────────────────────────────────────────────────── */

function JobCard({ job, index }) {
  const posted = formatDate(job.posted_date)

  return (
    <a
      href={job.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block rounded-xl bg-slate-800/40 border border-slate-700/30 p-4 transition-all duration-200 hover:bg-slate-800/70 hover:border-indigo-500/30 hover:shadow-lg hover:shadow-indigo-500/5"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Title */}
      <h3 className="text-sm font-semibold text-slate-100 leading-snug group-hover:text-indigo-300 transition-colors line-clamp-2 pr-6">
        <span className="mr-1.5 opacity-60">💼</span>
        {job.title}
        <span className="inline-block ml-1.5 text-[10px] text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity align-middle">↗</span>
      </h3>

      {/* Company */}
      {job.company && (
        <p className="mt-1.5 text-xs text-slate-400">
          <span className="mr-1">🏢</span>
          {job.company}
        </p>
      )}

      {/* Location + Source + Date */}
      <div className="mt-2.5 flex flex-wrap items-center gap-2 text-[11px]">
        {job.location && (
          <span className="inline-flex items-center gap-1 text-slate-500">
            <span>📍</span>
            <span>{job.location}</span>
          </span>
        )}
        {posted && (
          <span className="inline-flex items-center gap-1 text-slate-500">
            <span>📅</span>
            <span>{posted}</span>
          </span>
        )}
        {job.source && (
          <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium ${sourceColor(job.source)}`}>
            🌐 {job.source}
          </span>
        )}
      </div>

      {/* Description snippet */}
      {job.description && (
        <p className="mt-2 text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
          {job.description}
        </p>
      )}
    </a>
  )
}

/* ── Empty state ─────────────────────────────────────────────────────────── */

function EmptyState({ skill }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 gap-3">
      <span className="text-3xl">🔍</span>
      <p className="text-sm text-slate-400 text-center max-w-xs">
        No scraped jobs for <span className="font-semibold text-slate-200">{skill}</span> yet.
      </p>
      <p className="text-xs text-slate-500 text-center max-w-xs">
        Click <span className="font-medium text-indigo-400">Refresh</span> to scrape live listings from Indeed.
      </p>
    </div>
  )
}

/* ── Main component ──────────────────────────────────────────────────────── */

export default function JobList({ skill, source, limit = 10 }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!skill) { setJobs([]); return }
    let cancelled = false
    setLoading(true)
    setError(null)

    listJobs({ skill, source, limit })
      .then((data) => {
        if (!cancelled) setJobs(data)
      })
      .catch((e) => {
        if (!cancelled) setError(e.message || 'Failed to load jobs')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [skill, source, limit])

  // No skill selected — don't render
  if (!skill) return null

  return (
    <div className="mt-5 rounded-2xl bg-slate-900/70 border border-slate-800/60 p-5 shadow-lg shadow-black/10 card-glow animate-fade-in">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-slate-100">
          💼 Job Listings
        </h2>
        <p className="text-[11px] text-slate-500 mt-0.5">
          Real scraped postings mentioning <span className="font-medium text-slate-400">{skill}</span>
          {jobs.length > 0 && (
            <span className="ml-1.5 text-slate-600">· {jobs.length} found</span>
          )}
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <JobSkeleton key={i} />
          ))}
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="flex flex-col items-center justify-center py-8 gap-2">
          <span className="text-2xl">⚠️</span>
          <span className="text-sm text-rose-400">{error}</span>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && jobs.length === 0 && (
        <EmptyState skill={skill} />
      )}

      {/* Job list */}
      {!loading && !error && jobs.length > 0 && (
        <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1 scrollbar-thin">
          {jobs.map((job, i) => (
            <JobCard key={job.id || job.url || i} job={job} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
