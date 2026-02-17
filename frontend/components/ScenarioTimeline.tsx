import { ScenarioHistoryEntry } from '@/lib/api'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts'

interface ScenarioTimelineProps {
  history: ScenarioHistoryEntry[]
}

export default function ScenarioTimeline({ history }: ScenarioTimelineProps) {
  // Sort by date
  const sorted = [...history].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  // Map to chart data
  const data = sorted.map(e => ({
    date: new Date(e.created_at).toLocaleDateString(),
    score: e.simulated_score,
    label: e.tags && e.tags.length ? e.tags.join(', ') : (e.notes || ''),
    pinned: !!e.pinned,
  }))
  return (
    <div className="bg-slate-800 rounded-lg p-4 mb-6">
      <h4 className="text-lg font-bold text-white mb-2">Scenario Timeline</h4>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <XAxis dataKey="date" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" />
          <Tooltip contentStyle={{ background: '#1e293b', color: '#fff' }} />
          <Legend />
          <Line type="monotone" dataKey="score" stroke="#38bdf8" strokeWidth={2} dot={{ r: 4, fill: '#fbbf24' }} />
        </LineChart>
      </ResponsiveContainer>
      <div className="text-xs text-slate-300 mt-2">Hover points for details. Pinned scenarios are highlighted.</div>
    </div>
  )
}
