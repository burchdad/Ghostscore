'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface ScoreTrend {
  date: string
  score: number
}

interface ScoreTrendsProps {
  data: ScoreTrend[]
}

export default function ScoreTrends({ data }: ScoreTrendsProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-slate-700 rounded-lg p-6 text-white text-center">
        <p className="text-slate-400">No score history yet. Make changes to see trends!</p>
      </div>
    )
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6 text-white">
      <h3 className="text-xl font-bold mb-6">Score Trends</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
          <XAxis 
            dataKey="date" 
            stroke="#cbd5e1"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#cbd5e1" 
            domain={[300, 850]}
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
            labelStyle={{ color: '#e2e8f0' }}
            formatter={(value) => [`${value}`, 'Score']}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="score" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
            name="FICO Score"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
