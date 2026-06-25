import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { Clip } from '@/lib/api'

interface QualityChartProps {
  clips: Clip[]
}

export function QualityChart({ clips }: QualityChartProps) {
  const buckets = [
    { range: '90-100', count: 0, fill: '#00E5FF' },
    { range: '80-90', count: 0, fill: '#00B8D4' },
    { range: '70-80', count: 0, fill: '#8B5CF6' },
    { range: '60-70', count: 0, fill: '#A78BFA' },
    { range: '<60', count: 0, fill: '#F87171' },
  ]

  for (const clip of clips) {
    const q = clip.quality_score || 0
    if (q >= 90) buckets[0].count++
    else if (q >= 80) buckets[1].count++
    else if (q >= 70) buckets[2].count++
    else if (q >= 60) buckets[3].count++
    else buckets[4].count++
  }

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-muted mb-4">Quality Distribution</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={buckets}>
          <XAxis dataKey="range" tick={{ fill: '#8B949E', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8B949E', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: '#161B22', border: '1px solid #30363D', borderRadius: 8 }}
            labelStyle={{ color: '#fff' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {buckets.map((entry, i) => (
              <Cell key={`cell-${i}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
