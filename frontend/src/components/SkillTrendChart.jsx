import { useEffect, useMemo, useState } from 'react'
import {
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
  up:   { icon: '📈', label: 'Rising',  cls: 'text-emerald-400 bg-emerald-400/10' },
  down: { icon: '📉', label: 'Falling', cls: 'text-rose-400    bg-rose-400/10' },
  flat: { icon: '➡️', label: 'Stable',  cls: 'text-slate-300    bg-slate-400/10' },
}

export default function SkillTrendChart({ skill, days = 30 }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!skill) return
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
    return () => {
      cancelled = true
    }
  }, [skill, days])

  const summary = useMemo(() => classify(data), [data])
  const badge = BADGE[summary.direction]

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-slate-400">
          {skill ? <>Trend for <span className="font-semibold text-slate-200">{skill}</span></> : 'Pick a skill to see its trend'}
        </div>
        {data.length >= 14 && (
          <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${badge.cls}`}>
            <span>{badge.icon}</span>
            <span>{badge.label}</span>
            <span className="opacity-70">{Math.abs(summary.delta).toFixed(0)}%</span>
          </span>
        )}
      </div>

      <div className="h-72">
        {loading ? (
          <div className="h-full flex items-center justify-center text-slate-400">Loading trend…</div>
        ) : error ? (
          <div className="h-full flex items-center justify-center text-rose-400">⚠ {error}</div>
        ) : !data.length ? (
          <div className="h-full flex items-center justify-center text-slate-500">No data for this skill yet.</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
                tickFormatter={(d) => d.slice(5)} // MM-DD
              />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 8,
                  color: '#e2e8f0',
                }}
              />
              <ReferenceLine y={0} stroke="#334155" />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#818cf8"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#818cf8' }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
