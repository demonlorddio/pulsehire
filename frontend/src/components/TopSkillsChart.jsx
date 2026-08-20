import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { getTopSkills } from '../api'

const PALETTE = ['#f59e0b', '#d97706', '#b45309', '#92400e', '#78716c', '#78716c', '#78716c', '#78716c', '#78716c', '#78716c']

function SkeletonLoader() {
  return (
    <div className="space-y-3 py-4">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="skeleton h-3 w-16 rounded" />
          <div className="skeleton h-5 flex-1 rounded" style={{ width: `${60 - i * 5}%` }} />
        </div>
      ))}
    </div>
  )
}

/* ── Floating glassmorphism tooltip ──────────────────────────────────── */
function GlassTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="relative px-4 py-3 rounded-xl
                    bg-slate-900/80 backdrop-blur-xl
                    border border-white/[0.08]
                    shadow-[0_8px_32px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.04)]">
      {/* skill name */}
      <p className="text-sm font-semibold text-zinc-100 tracking-tight">{label}</p>

      {/* count + emerging */}
      <div className="flex items-center gap-2 mt-1">
        <span className="text-lg font-bold font-mono text-zinc-100 tabular-nums">
          {d.count}
        </span>
        <span className="text-[11px] text-zinc-500">mentions</span>
        {d.is_emerging && (
          <span className="ml-1 inline-flex items-center rounded-full
                           bg-indigo-500/15 border border-indigo-500/20
                           px-1.5 py-px text-[9px] font-semibold text-indigo-400
                           uppercase tracking-wider">
            emerging
          </span>
        )}
      </div>

      {/* category */}
      {d.category && (
        <p className="text-[10px] text-zinc-600 mt-1.5 font-mono">{d.category}</p>
      )}

      {/* hover hint */}
      <p className="text-[9px] text-zinc-700 mt-1.5 font-mono italic opacity-60">
        click to explore
      </p>
    </div>
  )
}

export default function TopSkillsChart({ days = 30, source, onSkillSelect, selectedSkill }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getTopSkills({ limit: 10, days, source })
      .then((rows) => { if (!cancelled) setData(rows) })
      .catch((e) => { if (!cancelled) setError(e.message || 'Failed to load') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [days, source])

  if (loading) return <SkeletonLoader />
  if (error) {
    return (
      <div className="h-80 flex items-center justify-center">
        <span className="text-sm text-zinc-500 font-mono">{error}</span>
      </div>
    )
  }
  if (!data.length) {
    return (
      <div className="h-80 flex items-center justify-center">
        <span className="text-sm text-zinc-600">No data yet. Try refreshing.</span>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={340}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 24, left: 4, bottom: 4 }}
        barCategoryGap="18%"
        onClick={(e) => {
          if (e?.activePayload?.[0]?.payload?.skill && onSkillSelect) {
            onSkillSelect(e.activePayload[0].payload.slug)
          }
        }}
        style={{ cursor: 'pointer' }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" horizontal={false} />
        <XAxis
          type="number"
          stroke="rgba(255,255,255,0.06)"
          tick={{ fontSize: 10, fill: '#52525b', fontFamily: 'JetBrains Mono' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="skill"
          stroke="rgba(255,255,255,0.06)"
          tick={({ x, y, payload }) => {
            const isSel = selectedSkill === payload.slug
            return (
              <text
                x={x} y={y}
                textAnchor="end"
                fill={isSel ? '#818cf8' : '#a1a1aa'}
                style={{
                  fontSize: 12,
                  fontWeight: isSel ? 600 : 400,
                  fontFamily: 'Inter, sans-serif',
                  transition: 'fill 0.2s, font-weight 0.2s',
                }}
              >
                {payload.value}
              </text>
            )
          }}
          width={100}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          content={<GlassTooltip />}
          cursor={{ fill: 'rgba(255, 255, 255, 0.02)' }}
          wrapperStyle={{ outline: 'none' }}
        />
        <Bar
          dataKey="count"
          radius={[0, 8, 8, 0]}
          animationBegin={0}
          animationDuration={600}
          animationEasing="ease-out"
        >
          {data.map((entry, i) => {
            const isSel = selectedSkill === entry.slug
            return (
              <Cell
                key={entry.skill_id}
                fill={isSel ? '#818cf8' : PALETTE[i % PALETTE.length]}
                fillOpacity={isSel ? 1 : entry.is_emerging ? 0.85 : 0.5}
                style={{
                  filter: isSel
                    ? 'drop-shadow(0 0 8px rgba(129, 140, 248, 0.5))'
                    : 'none',
                  transition: 'fill 0.2s, fill-opacity 0.25s, filter 0.25s',
                }}
              />
            )
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
