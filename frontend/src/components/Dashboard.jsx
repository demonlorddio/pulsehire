import { useEffect, useState } from 'react'
import TopSkillsChart from './TopSkillsChart'
import SkillTrendChart from './SkillTrendChart'
import FilterPanel from './FilterPanel'
import RefreshButton from './RefreshButton'
import { listSkills, getStats } from '../api'
import JobList from './JobList'

export default function Dashboard() {
  const [skills, setSkills] = useState([])
  const [days, setDays] = useState(30)
  const [source, setSource] = useState(null)
  const [skill, setSkill] = useState(null)
  const [stats, setStats] = useState(null)
  const [refreshTick, setRefreshTick] = useState(0)

  useEffect(() => {
    listSkills().then(setSkills).catch(() => {})
  }, [])

  useEffect(() => {
    getStats().then(setStats).catch(() => {})
  }, [refreshTick])

  const lastRefreshed = stats?.last_refresh
    ? new Date(stats.last_refresh).toLocaleString()
    : null

  return (
    <div className="min-h-screen px-4 sm:px-8 py-6 sm:py-10 max-w-7xl mx-auto">

      {/* ── Header ────────────────────────────────────────────────────── */}
      <header className="mb-8 animate-fade-in">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
                <span className="gradient-text">Pulse</span>
                <span className="text-slate-100">Hire</span>
              </h1>
              <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-[10px] font-medium text-emerald-400 uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-glow" />
                Live
              </span>
            </div>
            <p className="text-slate-400 text-sm sm:text-base">
              Real-time pulse of the tech job market —{' '}
              <span className="italic text-slate-300">stop guessing, start tracking.</span>
            </p>
          </div>

          {/* Stat tiles */}
          {stats && (
            <div className="flex gap-3">
              <Stat icon="💼" label="Jobs" value={stats.total_jobs} delay={0} />
              <Stat icon="🔗" label="Mentions" value={stats.total_skill_mentions} delay={100} />
              <Stat icon="🎯" label="Skills" value={stats.skills_tracked} delay={200} />
            </div>
          )}
        </div>

        {/* Last refreshed */}
        {lastRefreshed && (
          <p className="mt-3 text-[11px] text-slate-500">
            Last refreshed: <span className="text-slate-400">{lastRefreshed}</span>
            {stats?.last_refresh_status === 'ok' && (
              <span className="ml-1.5 text-emerald-500">✓</span>
            )}
          </p>
        )}
      </header>

      {/* ── Filters + Refresh ─────────────────────────────────────────── */}
      <section className="mb-6 animate-fade-in-delay-1">
        <div className="flex flex-col sm:flex-row sm:items-end gap-3">
          <div className="flex-1">
            <FilterPanel
              days={days}
              onDaysChange={setDays}
              source={source}
              onSourceChange={setSource}
              skill={skill}
              onSkillChange={setSkill}
              skills={skills}
            />
          </div>
          <div className="sm:ml-auto">
            <RefreshButton onRefreshed={() => setRefreshTick((n) => n + 1)} />
          </div>
        </div>
      </section>

      {/* ── Charts ────────────────────────────────────────────────────── */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-5 animate-fade-in-delay-2">
        <Card
          title="🔥 Top Skills"
          subtitle={`Mentioned across job postings · last ${days} days`}
        >
          <TopSkillsChart key={`top-${days}-${source || 'all'}`} days={days} source={source} />
        </Card>
        <Card
          title="📈 Skill Trend"
          subtitle="Compare week-over-week momentum"
        >
          <SkillTrendChart key={`trend-${skill}-${days}`} skill={skill} days={days} />
        </Card>
      </section>

      {/* ── Job Listings ──────────────────────────────────────────────── */}
      <section className="mt-5 animate-fade-in-delay-2">
        <JobList skill={skill} source={source} limit={10} />
      </section>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer className="mt-12 pb-6 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-slate-900/50 border border-slate-800 px-4 py-2">
          <span className="text-[11px] text-slate-500">
            Built for the <span className="text-slate-400 font-medium">Into the Scrape-Verse</span> Hackathon
          </span>
          <span className="text-slate-700">·</span>
          <span className="text-[11px] text-slate-500">
            Real-time data via <span className="text-indigo-400/80 font-medium">Bright Data</span> Web Unlocker
          </span>
        </div>
      </footer>
    </div>
  )
}

/* ── Stat tile ──────────────────────────────────────────────────────────── */
function Stat({ icon, label, value, delay = 0 }) {
  const [displayed, setDisplayed] = useState(0)

  useEffect(() => {
    if (value == null) return
    // Animate count-up
    const duration = 600
    const start = performance.now()
    const from = 0
    const timer = setTimeout(() => {
      const tick = (now) => {
        const elapsed = now - start
        const progress = Math.min(elapsed / duration, 1)
        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3)
        setDisplayed(Math.round(from + (value - from) * eased))
        if (progress < 1) requestAnimationFrame(tick)
      }
      requestAnimationFrame(tick)
    }, delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return (
    <div className="group relative rounded-xl bg-slate-900/80 border border-slate-800/80 px-4 py-3 min-w-[100px] text-center transition-all duration-200 hover:border-slate-700 hover:bg-slate-900">
      <div className="text-2xl mb-0.5">{icon}</div>
      <div className="text-xl font-bold text-slate-100 stat-value">
        {displayed.toLocaleString()}
      </div>
      <div className="text-[9px] uppercase tracking-widest text-slate-500 font-medium">
        {label}
      </div>
    </div>
  )
}

/* ── Card wrapper ───────────────────────────────────────────────────────── */
function Card({ title, subtitle, children }) {
  return (
    <div className="rounded-2xl bg-slate-900/70 border border-slate-800/60 p-5 shadow-lg shadow-black/10 card-glow">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-slate-100">{title}</h2>
        {subtitle && (
          <p className="text-[11px] text-slate-500 mt-0.5">{subtitle}</p>
        )}
      </div>
      {children}
    </div>
  )
}
