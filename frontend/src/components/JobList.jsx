// @ts-nocheck
import { useEffect, useState, useMemo } from 'react'
import { listJobs, secureParse } from '../api'

function formatDate(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr)
  if (isNaN(d)) return dateStr
  const now = new Date()
  const dd = Math.floor((now - d) / 86400000)
  if (dd === 0) return 'today'
  if (dd === 1) return 'yesterday'
  if (dd < 7) return dd + 'd ago'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function groupJobsByDate(jobs) {
  const g = {}; const now = new Date()
  const order = ['Today', 'Yesterday', 'This Week', 'This Month', '2-3 Months Ago', 'Older']
  jobs.forEach(j => {
    let l = 'Older'
    if (j.posted_date) {
      const d = new Date(j.posted_date)
      if (!isNaN(d)) {
        const dd = Math.floor((now - d) / 86400000)
        if (dd <= 0) l = 'Today'
        else if (dd === 1) l = 'Yesterday'
        else if (dd <= 7) l = 'This Week'
        else if (dd <= 30) l = 'This Month'
        else if (dd <= 90) l = '2-3 Months Ago'
        else l = 'Older'
      }
    }
    if (!g[l]) g[l] = []; g[l].push(j)
  })
  // Sort groups by time order
  const sorted = {}
  order.forEach(k => { if (g[k]) sorted[k] = g[k] })
  return sorted
}

function groupJobsBySource(jobs) {
  const g = {}
  jobs.forEach(j => { const s = (j.source||'unknown').toLowerCase(); if (!g[s]) g[s] = []; g[s].push(j) })
  return g
}

const SC = { indeed:{bg:'bg-amber-400/10',text:'text-amber-400/90',border:'border-amber-400/20',icon:'iy'}, linkedin:{bg:'bg-blue-400/10',text:'text-blue-400/90',border:'border-blue-400/20',icon:'in'}, glassdoor:{bg:'bg-emerald-400/10',text:'text-emerald-400/90',border:'border-emerald-400/20',icon:'gd'}, naukri:{bg:'bg-sky-400/10',text:'text-sky-400/90',border:'border-sky-400/20',icon:'nk'}, dice:{bg:'bg-violet-400/10',text:'text-violet-400/90',border:'border-violet-400/20',icon:'dc'}, remoteok:{bg:'bg-teal-400/10',text:'text-teal-400/90',border:'border-teal-400/20',icon:'ro'}, arbeitnow:{bg:'bg-orange-400/10',text:'text-orange-400/90',border:'border-orange-400/20',icon:'an'}, remotive:{bg:'bg-cyan-400/10',text:'text-cyan-400/90',border:'border-cyan-400/20',icon:'rm'}, jobicy:{bg:'bg-pink-400/10',text:'text-pink-400/90',border:'border-pink-400/20',icon:'jc'} }
const DS = {bg:'bg-zinc-400/10',text:'text-zinc-400/90',border:'border-zinc-400/20',icon:'??'}

function HighlightedSnippet({ text, skill }) {
  if (!text || !skill) return text ? <p className='text-[11px] text-zinc-500 line-clamp-2 leading-relaxed'>{text}</p> : null
  const re = new RegExp('(' + skill.replace(/[-\/\^+?.()|[\]{}]/g, '\$&') + ')', 'gi')
  const parts = text.split(re)
  return <p className='text-[11px] text-zinc-500 line-clamp-2 leading-relaxed'>{parts.map((p,i) => re.test(p) ? <span key={i} className='inline-block rounded bg-indigo-500/15 border border-indigo-500/20 px-1 py-px text-indigo-300 font-medium mx-px'>{p}</span> : <span key={i}>{p}</span>)}</p>
}

function MapPin() { return <svg className='w-3 h-3' viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='2' strokeLinecap='round' strokeLinejoin='round'><path d='M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z'/><circle cx='12' cy='10' r='3'/></svg> }

function SourceBadge({ source }) {
  const s = SC[(source||'').toLowerCase()] || DS
  return <span className={'inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-mono font-semibold uppercase tracking-wider ' + s.bg + ' ' + s.text + ' ' + s.border}><span className='opacity-70'>{s.icon}</span>{(source||'unknown').toUpperCase()}</span>
}

function JobSkeleton() { return <div className='glass-card p-5 space-y-3'><div className='flex items-start justify-between'><div className='flex-1 space-y-2'><div className='skeleton h-3.5 w-3/4 rounded'/><div className='skeleton h-2.5 w-1/3 rounded'/></div></div><div className='space-y-1.5'><div className='skeleton h-2 w-full rounded'/><div className='skeleton h-2 w-2/3 rounded'/></div></div> }

function JobCard({ job, index, selectedSkill, teeMode, attestation }) {
  const posted = formatDate(job.posted_date)
  return (
    <a href={job.url} target='_blank' rel='noopener noreferrer' className='group block glass-card p-5 transition-all duration-200 ease-out hover:border-indigo-500/20 hover:scale-[1.005] hover:shadow-[0_0_20px_-6px_rgba(99,102,241,0.12)] card-enter' style={{animationDelay: Math.min(index*30,300)+'ms'}}>
      <div className='flex items-start justify-between gap-3'>
        <div className='min-w-0 flex-1'>
          <h3 className='text-sm font-semibold text-zinc-100 leading-snug group-hover:text-indigo-300 transition-colors truncate'>{job.title}</h3>
          {job.company && <p className='text-xs text-zinc-400 mt-0.5 font-medium'>{job.company}</p>}
        </div>
        <span className='text-[10px] text-zinc-700 group-hover:text-indigo-400/60 transition-colors shrink-0 mt-0.5'>↗</span>
      </div>
      <div className='mt-3 flex flex-wrap items-center gap-2'>
        {job.location && <span className='inline-flex items-center gap-1 text-[11px] text-zinc-500'><MapPin />{job.location}</span>}
        {posted && <span className='text-[11px] text-zinc-600 font-mono'>{posted}</span>}
        {job.source && <SourceBadge source={job.source} />}
        {teeMode && attestation && <span className='inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-mono font-semibold uppercase tracking-wider bg-emerald-400/10 text-emerald-300 border-emerald-400/20' title={attestation.attestation_signature}><svg className='w-2.5 h-2.5' viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='2.5'><rect x='3' y='11' width='18' height='11' rx='2' ry='2'/><path d='M7 11V7a5 5 0 0 1 10 0v4'/></svg>Attested Enclave</span>}
      </div>
      {job.description && <div className='mt-3 pt-3 border-t border-white/[0.03]'><HighlightedSnippet text={job.description} skill={selectedSkill} /></div>}
    </a>
  )
}

function EmptyState({ skill, onRefresh }) {
  return <div className='py-16 flex flex-col items-center gap-4'>
    <div className='w-12 h-12 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center'><svg className='w-5 h-5 text-zinc-600' viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='1.5'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.35-4.35'/></svg></div>
    <div className='text-center'><p className='text-sm text-zinc-400'>No listings for <span className='text-zinc-200 font-semibold'>{skill}</span> yet</p><p className='text-[11px] text-zinc-600 mt-1 font-mono'>scrape live data to see results here</p></div>
    {onRefresh && <button type='button' onClick={onRefresh} className='mt-2 inline-flex items-center gap-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 px-4 py-2 text-xs font-medium text-indigo-300 hover:bg-indigo-500/15 transition-colors cursor-pointer'>Trigger Web Unlocker to Scrape Live Listings</button>}
  </div>
}

function GroupHeader({ label, count }) { return <div className='flex items-center gap-2 pt-3 pb-1 px-1'><span className='text-[10px] text-zinc-500 font-mono uppercase tracking-wider'>{label}</span><span className='text-[10px] text-zinc-600 font-mono'>({count})</span><div className='flex-1 h-px bg-white/[0.04]'/></div> }

export default function JobList({ skill, source, limit = 50, onRefresh, teeMode }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [attestations, setAttestations] = useState({})
  const [sortBy, setSortBy] = useState("date")
  const [sortDir, setSortDir] = useState("desc")
  const [groupBy, setGroupBy] = useState("none")
  const [showCount, setShowCount] = useState(15)

  useEffect(() => {
    if (!skill) { setJobs([]); return }
    let cancelled = false; setLoading(true); setError(null); setShowCount(15)
    listJobs({ skill, source, limit })
      .then(d => { if (!cancelled) setJobs(d) })
      .catch(e => { if (!cancelled) setError(e.message || "Failed") })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [skill, source, limit])

  useEffect(() => {
    if (!teeMode || !jobs.length) return
    jobs.forEach(async (job) => {
      if (attestations[job.id]) return
      try { const r = await secureParse({ jobTitle: job.title, jobDescription: job.description || "" }); setAttestations(p => ({...p, [job.id]: r})) } catch {}
    })
  }, [teeMode, jobs])

  const sortedJobs = useMemo(() => {
    const arr = [...jobs]
    arr.sort((a, b) => {
      let c = 0
      if (sortBy === "date") c = (a.posted_date ? new Date(a.posted_date).getTime() : 0) - (b.posted_date ? new Date(b.posted_date).getTime() : 0)
      else if (sortBy === "company") c = (a.company||"").localeCompare(b.company||"")
      else if (sortBy === "source") c = (a.source||"").localeCompare(b.source||"")
      else if (sortBy === "title") c = (a.title||"").localeCompare(b.title||"")
      return sortDir === "asc" ? c : -c
    })
    return arr
  }, [jobs, sortBy, sortDir])

  const visibleJobs = sortedJobs.slice(0, showCount)
  const hasMore = showCount < sortedJobs.length
  const toggleSort = (f) => { if (sortBy === f) setSortDir(d => d==="asc"?"desc":"asc"); else { setSortBy(f); setSortDir("desc") } }

  const renderJobs = () => {
    if (groupBy === "none") return <div className="space-y-3">{visibleJobs.map((job,i) => <JobCard key={job.id||job.url||i} job={job} index={i} selectedSkill={skill} teeMode={teeMode} attestation={attestations[job.id]} />)}</div>
    const groups = groupBy === "date" ? groupJobsByDate(sortedJobs) : groupJobsBySource(sortedJobs)
    let fi = 0
    return <div className="space-y-1">{Object.keys(groups).map(k => <div key={k}><GroupHeader label={k} count={groups[k].length} /><div className="space-y-3">{groups[k].map(job => { const idx=fi++; return <JobCard key={job.id||job.url||idx} job={job} index={idx} selectedSkill={skill} teeMode={teeMode} attestation={attestations[job.id]} /> })}</div></div>)}</div>
  }

  if (!skill) return null
  const n = jobs.length
  const sb = (k) => <button key={k} type="button" onClick={() => toggleSort(k)} className={"px-2 py-0.5 rounded text-[9px] font-mono uppercase tracking-wider transition-colors cursor-pointer " + (sortBy===k ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/20" : "text-zinc-500 hover:text-zinc-300 border border-transparent")}>{k.charAt(0).toUpperCase()+k.slice(1)}</button>
  const gb = (k) => <button key={k} type="button" onClick={() => setGroupBy(k)} className={"px-2 py-0.5 rounded text-[9px] font-mono uppercase tracking-wider transition-colors cursor-pointer " + (groupBy===k ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/20" : "text-zinc-500 hover:text-zinc-300 border border-transparent")}>{k==="none"?"None":k.charAt(0).toUpperCase()+k.slice(1)}</button>

  return (
    <div className="glass-card p-6 mb-8">
      <div className="mb-4 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <h2 className="heading-section text-sm text-zinc-200 uppercase tracking-wider">Real Listings</h2>
          <p className="text-[11px] text-zinc-500 mt-0.5 font-mono">matching <span className="text-zinc-300 font-medium">{skill}</span>{n > 0 && <span className="text-zinc-600 ml-1.5">&middot; {n} results</span>}</p>
        </div>
        {n > 0 && !loading && <div className="flex items-center gap-3 flex-wrap"><div className="flex items-center gap-1"><span className="text-[9px] text-zinc-600 font-mono uppercase tracking-wider mr-1">Sort:</span>{["date","company","source","title"].map(sb)}</div><div className="flex items-center gap-1"><span className="text-[9px] text-zinc-600 font-mono uppercase tracking-wider mr-1">Group:</span>{["none","date","source"].map(gb)}</div></div>}
      </div>
      {loading && <div className="space-y-3">{Array.from({length:5}).map((_,i) => <JobSkeleton key={i} />)}</div>}
      {error && !loading && <div className="py-10 text-center"><span className="text-sm text-red-400 font-mono">{error}</span></div>}
      {!loading && !error && n === 0 && <EmptyState skill={skill} onRefresh={onRefresh} />}
      {!loading && !error && n > 0 && (
        <div className="max-h-[700px] overflow-y-auto pr-1 fade-edges">
          {renderJobs()}
          {hasMore && <div className="mt-4 text-center"><button type="button" onClick={() => setShowCount(x=>x+20)} className="text-[11px] text-zinc-500 font-mono hover:text-indigo-300 cursor-pointer">Show more ({sortedJobs.length - showCount} remaining)</button></div>}
          {!hasMore && sortedJobs.length > 15 && <div className="mt-4 text-center"><button type="button" onClick={() => setShowCount(15)} className="text-[11px] text-zinc-500 font-mono hover:text-indigo-300 cursor-pointer">Show less</button></div>}
        </div>
      )}
    </div>
  )
}
