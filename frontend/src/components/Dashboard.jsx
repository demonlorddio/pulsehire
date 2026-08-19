import { useEffect, useState } from 'react'
import TopSkillsChart from './TopSkillsChart'
import SkillTrendChart from './SkillTrendChart'
import FilterPanel from './FilterPanel'
import RefreshButton from './RefreshButton'
import { listSkills, getStats } from '../api'

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

  return (
    <div className="min-h-screen px-4 sm:px-8 py-8 max-w-6xl mx-auto">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Pulse<span className="text-brand-400">Hire</span>
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Real-time pulse of the tech job market —{' '}
            <span className="italic">stop guessing, start tracking.</span>
          </p>
        </div>
        {stats && (
          <div className="flex gap-4 text-center">
            <Stat label="Jobs tracked" value={stats.total_jobs} />
            <Stat label="Mentions" value={stats.total_skill_mentions} />
            <Stat label="Skills" value={stats.skills_tracked} />
          </div>
        )}
      </header>

      <section className="mb-6">
        <FilterPanel
          days={days}
          onDaysChange={setDays}
          source={source}
          onSourceChange={setSource}
          skill={skill}
          onSkillChange={setSkill}
          skills={skills}
        />
      </section>

      <section className="mb-4">
        <RefreshButton onRefreshed={() => setRefreshTick((n) => n + 1)} />
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="🔥 Top skills" subtitle={`Mentioned across job postings · last ${days} days`}>
          <TopSkillsChart key={`top-${days}-${source || 'all'}`} days={days} source={source} />
        </Card>
        <Card title="📈 Skill trend over time" subtitle="Compare week-over-week momentum">
          <SkillTrendChart key={`trend-${skill}-${days}`} skill={skill} days={days} />
        </Card>
      </section>

      <footer className="mt-10 text-xs text-slate-500 text-center">
        Built for the Into the Scrape-Verse Hackathon · Sample data until Bright Data is connected.
      </footer>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-900 border border-slate-800 px-4 py-2 min-w-[90px]">
      <div className="text-2xl font-bold text-slate-100">{value ?? '—'}</div>
      <div className="text-[10px] uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  )
}

function Card({ title, subtitle, children }) {
  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-5 shadow-lg shadow-black/20">
      <div className="mb-3">
        <h2 className="text-lg font-semibold">{title}</h2>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}
