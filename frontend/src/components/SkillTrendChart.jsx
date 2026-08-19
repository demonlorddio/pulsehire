import { useEffect, useMemo, useState } from 'react'
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { getSkillTrend } from '../api'

// Classify the trend: compare average of last 7 days vs prior 7 days.
function classify(points) {
  if (!points || points.length < 14) return { direction: 'flat', delta: 0 }
  const last7 = points.slice(-7).reduce((s, p) => s + p.count, 0) / 7
  const prev7 = points.slice(-14, -7).reduce((s, p) => s + p.count, 0) / 7
  if (prev7 === 0) {
    return { direction: last7 > 0 ? 'up' : 'flat', delta: last7 > 0 ? 100 : 0 }
  }
  const delta = ((last7 - prev7) / prev7) * 100
  if (delta > 10) return { direction: 'up', delta }
  if (delta < -10) return { direction: 'down', delta }
  return { direction: 'flat', delta }
}

const BADGE = {
  up:   { icon: '📈', label: 'Rising',  cls: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' },
  down: { icon: '📉', label: 'Falling', cls: 'text-rose-400    bg-rose-400/10    border-rose-400/20' },
  flat: { icon: '➡️',  label: 'Stable',  cls: 'text-slate-300    bg-slate-400/10    border-slate-400/20' },
}

function SkeletonLoader() {
  return (
    <div className="space-y-3 py-4">
      <div className="skeleton h-4 w-48 rounded" />
      <div className="skeleton h-56 w-full rounded-xl mt-4" />
    </div>
  )
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg bg-slate-800/95 border border-slate-700/50 backdrop-blur-sm px-3 py-2 shadow-xl">
      <p className="text-[11px] text-slate-400 mb-0.5">{label}</p>
      <p className="text-sm font-semibold text-indigo-300">
        {payload[0].value} <span className="text-slate-500 font-normal">mentions</span>
      </p>
    </div>
  )
}

export default function SkillTrendChart({ skill, days = 30 }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!skill) { setLoading(false); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    getSkillTrend({ skill, days })
      .then((res) => {
        if (!cancelled) setData(res.points || [])
      })
      .catch((e) => {
        if (!cancelled) setError(e.message || 'Failed to load')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [skill, days])

  const summary = useMemo(() => classify(data), [data])
  const badge = BADGE[summary.direction]

  if (!skill) {
    return (
      <div className="h-72 flex flex-col items-center justify-center gap-3">
        <span className="text-3xl">👆</span>
        <span className="text-sm text-slate-500">Select a skill above to see its trend</span>
      </div>
    )
  }

  if (loading) return <SkeletonLoader />

  if (error) {
    return (
      <div className="h-72 flex flex-col items-center justify-center gap-2">
        <span className="text-2xl">⚠️</span>
        <span className="text-sm text-rose-400">{error}</span>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="h-72 flex flex-col items-center justify-center gap-2">
        <span className="text-2xl">📭</span>
        <span className="text-sm text-slate-500">No data for this skill yet</span>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-slate-400">
          Trend for <span className="font-semibold text-slate-200">{skill}</span>
        </div>
        {data.length >= 14 && (
          <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-all ${badge.cls}`}>
            <span>{badge.icon}</span>
            <span>{badge.label}</span>
            <span className="opacity-60">{Math.abs(summary.delta).toFixed(0)}%</span>
          </span>
        )}
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
            <defs>
              <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#818cf8" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#818cf8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#475569"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickFormatter={(d) => d.slice(5)}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              stroke="#475569"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              allowDecimals={false}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#334155" />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#818cf8"
              strokeWidth={2.5}
              fill="url(#trendGradient)"
              dot={{ r: 3, fill: '#818cf8', stroke: '#0f172a', strokeWidth: 2 }}
              activeDot={{ r: 6, fill: '#818cf8', stroke: '#c7d2fe', strokeWidth: 2 }}
              animationBegin={0}
              animationDuration={1000}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
