'use client';

/**
 * ScoreFactorsRadar
 * Radar chart visualization of the 5 FICO factors
 * Shows the breakdown by scorecard type
 */

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Subscores {
  payment_history?: number;
  utilization?: number;
  age?: number;
  new_credit?: number;
  mix?: number;
}

interface ScoreFactorsRadarProps {
  subscores: Subscores;
  scorecard: string;
  totalScore: number;
}

export default function ScoreFactorsRadar({
  subscores,
  scorecard,
  totalScore,
}: ScoreFactorsRadarProps) {
  // Prepare data for radar chart
  const data = [
    {
      factor: 'Payment History',
      value: subscores.payment_history || 0,
      fullMark: 100,
    },
    {
      factor: 'Utilization',
      value: subscores.utilization || 0,
      fullMark: 100,
    },
    {
      factor: 'Age of Credit',
      value: subscores.age || 0,
      fullMark: 100,
    },
    {
      factor: 'New Credit',
      value: subscores.new_credit || 0,
      fullMark: 100,
    },
    {
      factor: 'Credit Mix',
      value: subscores.mix || 0,
      fullMark: 100,
    },
  ];

  // Get weights based on scorecard type
  const getWeights = (type: string) => {
    switch (type) {
      case 'derogatory':
        return {
          payment_history: 50,
          utilization: 20,
          age: 15,
          new_credit: 10,
          mix: 5,
        };
      case 'thin':
        return {
          payment_history: 30,
          utilization: 20,
          age: 25,
          new_credit: 15,
          mix: 10,
        };
      case 'young':
        return {
          payment_history: 35,
          utilization: 25,
          age: 25,
          new_credit: 10,
          mix: 5,
        };
      case 'clean':
      default:
        return {
          payment_history: 35,
          utilization: 30,
          age: 15,
          new_credit: 10,
          mix: 10,
        };
    }
  };

  const weights = getWeights(scorecard);

  // Calculate weighted contribution (0-100)
  const weightedContributions = [
    (subscores.payment_history || 0) * (weights.payment_history / 100),
    (subscores.utilization || 0) * (weights.utilization / 100),
    (subscores.age || 0) * (weights.age / 100),
    (subscores.new_credit || 0) * (weights.new_credit / 100),
    (subscores.mix || 0) * (weights.mix / 100),
  ];

  const totalWeightedScore = weightedContributions.reduce((a, b) => a + b, 0);

  // Scorecard colors
  const scorecardColorMap = {
    clean: 'bg-green-100 text-green-700 border-green-300',
    young: 'bg-blue-100 text-blue-700 border-blue-300',
    thin: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    derogatory: 'bg-red-100 text-red-700 border-red-300',
  };

  const scorecardColor =
    (scorecardColorMap as Record<string, string>)[scorecard] ||
    scorecardColorMap.clean;

  return (
    <div className="w-full bg-white rounded-lg border border-slate-200 p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              Factor Breakdown
            </h3>
            <p className="text-sm text-slate-600 mt-1">
              How each factor contributes to your score
            </p>
          </div>
          <div className={`px-4 py-2 rounded-lg border-2 ${scorecardColor}`}>
            <p className="text-xs font-medium opacity-75">Profile Type</p>
            <p className="text-sm font-bold capitalize">{scorecard}</p>
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="mb-6">
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis
              dataKey="factor"
              tick={{ fontSize: 12, fill: '#64748b' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fontSize: 12, fill: '#94a3b8' }}
            />
            <Radar
              name="Score"
              dataKey="value"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.6}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              formatter={(value) => [`${value}/100`, 'Score']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Factor Details Table */}
      <div className="space-y-2 mb-6">
        <h4 className="font-semibold text-slate-900 text-sm">Score Details</h4>
        <div className="space-y-1">
          {data.map((item, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200"
            >
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">
                  {item.factor}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-xs text-slate-600">
                    {weights[item.factor.toLowerCase().replace(/ /g, '_') as keyof typeof weights]}%
                    weight
                  </p>
                  <p className="text-lg font-bold text-slate-900">
                    {item.value}
                  </p>
                </div>
                <div className="w-16 h-2 bg-slate-300 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all"
                    style={{ width: `${Math.min(item.value, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weighted Score Breakdown */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-2 border-blue-200">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-600">Your FICO Score</p>
            <p className="text-3xl font-bold text-slate-900">{totalScore}</p>
          </div>
          <div>
            <p className="text-xs text-slate-600">Weighted Impact</p>
            <p className="text-3xl font-bold text-blue-600">
              {totalWeightedScore.toFixed(1)}/100
            </p>
          </div>
        </div>
        <p className="text-sm text-slate-600 mt-3">
          Your {scorecard} profile uses custom factor weights to calculate your FICO score.
          The weighted impact shows how all factors combine to drive your final score.
        </p>
      </div>

      {/* Recommendations */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm font-semibold text-blue-900 mb-2">
          Improvement Opportunity
        </p>
        <ul className="text-sm text-blue-800 space-y-1">
          {(subscores.utilization || 0) > 30 && (
            <li>✓ Reduce credit utilization below 30% for quick gains</li>
          )}
          {(subscores.payment_history || 0) < 80 && (
            <li>✓ Keep all payments on-time to boost payment history</li>
          )}
          {(subscores.age || 0) < 70 && (
            <li>✓ Keep accounts open to increase average age</li>
          )}
          {(subscores.new_credit || 0) < 70 && (
            <li>✓ Avoid applying for new credit too frequently</li>
          )}
        </ul>
      </div>
    </div>
  );
}
