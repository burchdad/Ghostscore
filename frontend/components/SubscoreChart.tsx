'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { ScoreResponse } from '@/lib/api'

interface SubscoreChartProps {
  score: ScoreResponse
}

export default function SubscoreChart({ score }: SubscoreChartProps) {
  const data = [
    { name: 'Payment\nHistory', value: score.payment_history, weight: '35%' },
    { name: 'Utilization', value: score.utilization, weight: '30%' },
    { name: 'Age', value: score.age, weight: '15%' },
    { name: 'New Credit', value: score.new_credit, weight: '10%' },
    { name: 'Credit Mix', value: score.mix, weight: '10%' },
  ]

  return (
    <div className="bg-slate-700 rounded-lg p-6 text-white">
      <h3 className="text-xl font-bold mb-6">Score Breakdown</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
          <XAxis dataKey="name" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" domain={[0, 100]} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-6 grid grid-cols-5 gap-2 text-sm">
        {data.map((item) => (
          <div key={item.name} className="text-center">
            <div className="text-slate-300">{item.weight}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
