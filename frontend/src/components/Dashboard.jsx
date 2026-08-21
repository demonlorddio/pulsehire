import { useEffect, useRef, useState } from 'react'
import TopSkillsChart from './TopSkillsChart'
import SkillTrendChart from './SkillTrendChart'
import FilterPanel from './FilterPanel'
import RefreshButton from './RefreshButton'
import { listSkills, getStats, triggerRefresh } from '../api'
import JobList from './JobList'
import FloatingParticles from './FloatingParticles'

export default function Dashboard() {
  const [skills, setSkills] = useState([])
  const [days, setDays] = useState(30)
  const [source, setSource] = useState(null)
  const [skill, setSkill] = useState(null)
  const [stats, setStats] = useState(null)
  const [teeMode, setTeeMode] = useState(false)
  const [refreshTick, setRefreshTick] = useState(0)
  

  useEffect(() => { listSkills().then(setSkills).catch(() => {}) }, [])
  useEffect(() => { getStats().then(setStats).catch(() => {}) }, [refreshTick])

  const lastRefreshed = stats?.last_refresh
    ? new Date(stats.last_refresh).toLocaleString()
    : null

  return (
    <div className="min-h-screen relative">
      <div className="max-w-[1600px] mx-auto flex flex-col lg:flex-row min-h-screen">

        {/* ═══════════════ LEFT SIDEBAR ═══════════════ */}
        <aside className="lg:w-[320px] lg:min-h-screen lg:sticky lg:top-0 border-b lg:border-b-0 lg:border-r border-white/[0.04] flex flex-col relative overflow-hidden">
          <div className="p-6 lg:p-8 flex flex-col flex-1 stagger relative">
            <FloatingParticles />

            {/* Logo */}
            <div className="mb-6">
              <h1 className="text-2xl font-extrabold tracking-tighter leading-none">
                <span className="text-gradient">Pulse</span>
                <span className="text-zinc-100">Hire</span>
              </h1>
              <p className="mono-label mt-2">skill intelligence</p>
            </div>

            {/* Live status + Stats — at the top */}
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-white/[0.04]">
              <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot" />
              <span className="text-xs text-zinc-400 font-medium">Live</span>
              {lastRefreshed && (
                <span className="text-[10px] text-zinc-600 font-mono ml-auto">
                  {lastRefreshed}
                </span>
              )}
            </div>

            {stats && (
              <div className="mb-5 pb-4 border-b border-white/[0.04]">
                <StatRow label="Total jobs" value={stats.total_jobs} />
                <StatRow label="Skill mentions" value={stats.total_skill_mentions} />
                <StatRow label="Skills tracked" value={stats.skills_tracked} />
              </div>
            )}

            {/* Filters */}
            <div className="mb-4">
              <FilterPanel
                days={days} onDaysChange={setDays}
                source={source} onSourceChange={setSource}
                skill={skill} onSkillChange={setSkill}
                skills={skills}
              />
            </div>

            {/* Naukri demo mode notice */}
            {source === 'naukri' && (
              <div className="mb-4 rounded-lg bg-sky-500/[0.06] border border-sky-500/10 px-4 py-3">
                <p className="text-[11px] text-sky-300/80 leading-relaxed">
                  <span className="mr-1">&#x1F4A1;</span>
                  Naukri is currently operating in demo/mock mode.
                  Switch the source to <span className="font-semibold text-sky-200">Indeed</span> to trigger the live Web Unlocker scraper!
                </p>
              </div>
            )}

            {/* Refresh + TEE — at the bottom */}
            <div className="mt-auto pt-4 space-y-3">
              <RefreshButton
                onRefreshed={() => setRefreshTick((n) => n + 1)}
                source={source || 'indeed'}
              />

              {/* TEE Secure Enclave Toggle */}
              <div className="rounded-lg bg-emerald-500/[0.06] border border-emerald-500/10 px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    <span className="text-[11px] text-emerald-300/90 font-semibold uppercase tracking-wider">TEE Secure Enclave</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setTeeMode((v) => !v)}
                    className={teeMode ? 'relative w-10 h-5 rounded-full bg-emerald-500/30 border border-emerald-400/40 transition-colors' : 'relative w-10 h-5 rounded-full bg-white/[0.06] border border-white/[0.08] transition-colors'}
                  >
                    <span className={teeMode ? 'absolute top-0.5 left-[22px] w-3.5 h-3.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.4)] transition-all' : 'absolute top-0.5 left-0.5 w-3.5 h-3.5 rounded-full bg-zinc-500 transition-all'} />
                  </button>
                </div>
                {teeMode && (
                  <p className="text-[10px] text-emerald-400/60 mt-2 font-mono">
                    Privacy-First Mode Active: Parsing isolated in secure hardware enclave.
                  </p>
                )}
              </div>
            </div>
          </div>
        </aside>

        {/* ═══════════════ RIGHT CONTENT ═══════════════ */}
        <main className="flex-1 p-6 lg:p-8 min-w-0 stagger">

          {/* Charts row */}
          <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 mb-8">
            <div className="xl:col-span-3 glass-card glass-glow-hover p-6 relative noise-overlay">
              <SectionHead
                title="Top Skills"
                sub={`Mentioned across job postings \u00b7 last ${days} days`}
                hint="click a bar to explore"
              />
              <TopSkillsChart
                key={`top-${days}-${source || 'all'}`}
                days={days}
                source={source}
                onSkillSelect={(s) => setSkill(s)}
                selectedSkill={skill}
              />
            </div>
            <div className="xl:col-span-2 glass-card glass-glow-hover p-6 relative noise-overlay">
              <SectionHead
                title="Skill Trend"
                sub={skill ? `Week-over-week for ${skill}` : 'Select a skill to begin'}
              />
              <SkillTrendChart key={`trend-${skill}-${source}-${days}`} skill={skill} days={days} source={source} />
            </div>
          </div>

          {/* Job Listings */}
          <JobList skill={skill} source={source} limit={50} teeMode={teeMode} onRefresh={() => triggerRefresh({ source: source || "indeed" }).then(() => setRefreshTick(n => n + 1))} />

          {/* Footer */}
          <footer className="mt-16 pb-8 border-t border-white/[0.04] pt-6">
            <div className="flex items-center justify-between text-[11px] text-zinc-600 font-mono">
              <span>Built for the Into the Scrape-Verse Hackathon</span>
              <span>Powered by Bright Data Web Unlocker + Dataset API</span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  )
}

/* ── Stat row (sidebar) ──────────────────────────────────────────────── */
function StatRow({ label, value }) {
  const [displayed, setDisplayed] = useState(0)
  useEffect(() => {
    if (value == null) return
    let start = null
    const duration = 700
    const tick = (now) => {
      if (!start) start = now
      const p = Math.min((now - start) / duration, 1)
      setDisplayed(Math.round(value * (1 - Math.pow(1 - p, 3))))
      if (p < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [value])

  return (
    <div className="flex items-baseline justify-between py-1.5">
      <span className="text-[11px] text-zinc-500 uppercase tracking-wider">{label}</span>
      <span className="text-sm font-bold font-mono text-zinc-200 tabular-nums">
        {displayed.toLocaleString()}
      </span>
    </div>
  )
}

/* ── Section heading ─────────────────────────────────────────────────── */
function SectionHead({ title, sub, hint }) {
  return (
    <div className="mb-5 flex items-end justify-between">
      <div>
        <h2 className="heading-section text-sm text-zinc-200 uppercase tracking-wider">{title}</h2>
        {sub && <p className="text-[11px] text-zinc-500 mt-0.5 font-mono">{sub}</p>}
      </div>
      {hint && (
        <span className="text-[10px] text-zinc-600 font-mono italic hidden sm:block">{hint}</span>
      )}
    </div>
  )
}
