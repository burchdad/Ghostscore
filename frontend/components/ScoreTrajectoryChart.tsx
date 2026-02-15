'use client';

/**
 * ScoreTrajectoryChart
 * Visualizes week-by-week FICO score improvement trajectory
 * Shows the impact timeline of recommended credit actions
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TimelinePoint {
  week: number;
  score: number;
  milestone: string;
}

interface ScoreTrajectoryChartProps {
  timeline: TimelinePoint[];
  currentScore: number;
  potentialGain: number;
}

export default function ScoreTrajectoryChart({
  timeline,
  currentScore,
  potentialGain,
}: ScoreTrajectoryChartProps) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="w-full p-4 bg-slate-50 rounded-lg border border-slate-200">
        <p className="text-slate-600">No improvement trajectory available</p>
      </div>
    );
  }

  const data = timeline.map((point) => ({
    week: `Week ${point.week}`,
    score: point.score,
    milestone: point.milestone,
  }));

  return (
    <div className="w-full bg-white rounded-lg border border-slate-200 p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-900">
          Score Improvement Timeline
        </h3>
        <p className="text-sm text-slate-600 mt-1">
          Projected score improvement over 16 weeks
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-3 rounded-lg">
          <p className="text-xs text-slate-600">Current Score</p>
          <p className="text-2xl font-bold text-blue-600">{currentScore}</p>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-xs text-slate-600">Potential Gain</p>
          <p className="text-2xl font-bold text-green-600">+{potentialGain}</p>
        </div>
        <div className="bg-purple-50 p-3 rounded-lg">
          <p className="text-xs text-slate-600">Target Score</p>
          <p className="text-2xl font-bold text-purple-600">
            {currentScore + potentialGain}
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis domain={[300, 850]} />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
            formatter={(value) => [`${value}`, 'Score']}
            labelFormatter={(label) => label}
            cursor={{ stroke: '#ccc' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
            name="Estimated Score"
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <strong>Timeline:</strong> Score improvements typically appear within 2-4 months
          after implementing recommendations. Credit bureaus report updates monthly, and scoring
          models react as utilization and account age adjust.
        </p>
      </div>
    </div>
  );
}
