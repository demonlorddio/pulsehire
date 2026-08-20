import { useEffect, useMemo, useState } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'
import { getSkillTrend } from '../api'

function classify(points) {
  if (!points || points.length < 14) return { direction: 'flat', delta: 0 }
  const last7 = points.slice(-7).reduce((s, p) => s + p.count, 0) / 7
  const prev7 = points.slice(-14, -7).reduce((s, p) => s + p.count, 0) / 7
  if (prev7 === 0) return { direction: last7 > 0 ? 'up' : 'flat', delta: last7 > 0 ? 100 : 0 }
  const delta = ((last7 - prev7) / prev7) * 100
  if (delta > 10) return { direction: 'up', delta }
  if (delta < -10) return { direction: 'down', delta }
  return { direction: 'flat', delta }
}

const BADGE = {
  up:   { label: 'Rising',  cls: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' },
  down: { label: 'Falling', cls: 'text-red-400 bg-red-400/10 border-red-400/20' },
  flat: { label: 'Stable',  cls: 'text-zinc-400 bg-zinc-400/10 border-zinc-400/20' },
}

function SkeletonLoader() {
  return (
    <div className="space-y-3 py-4">
      <div className="skeleton h-3 w-36 rounded" />
      <div className="skeleton h-48 w-full rounded mt-4" />
    </div>
  )
}

/* ── Floating glassmorphism tooltip ──────────────────────────────────── */
function GlassTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const val = payload[0].value
  return (
    <div className="px-4 py-3 rounded-xl
                    bg-slate-900/80 backdrop-blur-xl
                    border border-white/[0.08]
                    shadow-[0_8px_32px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.04)]">
      <p className="text-[10px] text-zinc-500 font-mono tracking-wide uppercase mb-1">{label}</p>
      <p className="text-lg font-bold font-mono text-zinc-100 tabular-nums">
        {val}
        <span className="text-[11px] text-zinc-500 font-normal ml-1.5">mentions</span>
      </p>
    </div>
  )
}

export default function SkillTrendChart({ skill, days = 30, source }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!skill) { setLoading(false); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    getSkillTrend({ skill, days, source })
      .then((res) => { if (!cancelled) setData(res.points || []) })
      .catch((e) => { if (!cancelled) setError(e.message || 'Failed to load') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [skill, days, source])

  const summary = useMemo(() => classify(data), [data])
  const badge = BADGE[summary.direction]

  if (!skill) {
    return (
      <div className="h-64 flex flex-col items-center justify-center gap-2">
        <span className="text-[11px] text-zinc-600 uppercase tracking-widest font-mono">
          Select a skill to view trend
        </span>
      </div>
    )
  }

  if (loading) return <SkeletonLoader />
  if (error) {
    return (
      <div className="h-64 flex items-center justify-center">
        <span className="text-sm text-zinc-500 font-mono">{error}</span>
      </div>
    )
  }
  if (!data.length) {
    return (
      <div className="h-64 flex items-center justify-center">
        <span className="text-sm text-zinc-600">No data for this skill yet</span>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-zinc-300 font-medium">{skill}</span>
        {data.length >= 14 && (
          <span className={`inline-flex items-center gap-1 text-[11px] font-mono font-medium
                           rounded-md border px-2 py-0.5 ${badge.cls}`}>
            {badge.label} {Math.abs(summary.delta).toFixed(0)}%
          </span>
        )}
      </div>

      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgba(99, 102, 241, 0.25)" />
                <stop offset="100%" stopColor="rgba(99, 102, 241, 0)" />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="rgba(255,255,255,0.06)"
              tick={{ fontSize: 10, fill: '#52525b', fontFamily: 'JetBrains Mono' }}
              tickFormatter={(d) => d.slice(5)}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              stroke="rgba(255,255,255,0.06)"
              tick={{ fontSize: 10, fill: '#52525b', fontFamily: 'JetBrains Mono' }}
              allowDecimals={false}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={<GlassTooltip />}
              cursor={{ stroke: 'rgba(99, 102, 241, 0.3)', strokeWidth: 1 }}
              wrapperStyle={{ outline: 'none' }}
            />
            <ReferenceLine y={0} stroke="rgba(255,255,255,0.04)" />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#colorCount)"
              dot={{
                r: 2,
                fill: '#6366f1',
                stroke: '#030712',
                strokeWidth: 2,
              }}
              activeDot={{
                r: 5,
                fill: '#6366f1',
                stroke: '#ffffff',
                strokeWidth: 2,
              }}
              animationBegin={0}
              animationDuration={800}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
