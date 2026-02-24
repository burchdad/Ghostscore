'use client';

import { useState, useEffect } from 'react';
import { TrendingUp } from 'lucide-react';

interface GoalTrackerProps {
  currentScore?: number;
  optimizeData?: any | null;
  forecastData?: { forecast: number[]; weeks: number } | null;
}

export default function GoalTracker({ currentScore = 0, optimizeData, forecastData }: GoalTrackerProps) {
  const [targetScore, setTargetScore] = useState(740);
  const projectedScore = forecastData?.forecast?.[16] || currentScore;
  const probability = optimizeData?.goal_success_probability || 0;
  const progressPercent = ((currentScore - 300) / (targetScore - 300)) * 100;
  const projectedPercent = ((projectedScore - 300) / (targetScore - 300)) * 100;

  const isAchievable = projectedScore >= targetScore;

  return (
    <div className="bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg shadow-lg p-6 border border-slate-600 text-white">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <TrendingUp size={24} />
          Goal Tracker
        </h2>
        <span className={`font-bold text-lg ${isAchievable ? 'text-green-400' : 'text-amber-400'}`}>
          {isAchievable ? '✓ ACHIEVABLE' : 'CHALLENGING'}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div>
          <p className="text-sm text-gray-300 mb-1">Target Score</p>
          <p className="text-3xl font-bold text-blue-300">{targetScore}</p>
        </div>
        <div>
          <p className="text-sm text-gray-300 mb-1">Current Score</p>
          <p className="text-3xl font-bold text-slate-200">{Math.round(currentScore)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-300 mb-1">Projected (16w)</p>
          <p className={`text-3xl font-bold ${isAchievable ? 'text-green-300' : 'text-orange-300'}`}>
            {Math.round(projectedScore)}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-300">Progress</span>
          <span className="text-gray-300">{Math.round(progressPercent)}% → {Math.round(projectedPercent)}%</span>
        </div>
        <div className="h-3 bg-slate-600 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-red-500 via-amber-500 to-green-500 transition-all duration-500"
            style={{ width: `${Math.max(0, Math.min(100, projectedPercent))}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>300 (Min)</span>
          <span>850 (Max)</span>
        </div>
      </div>

      {/* Probability */}
      <div className="bg-slate-800 rounded p-3">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-300">Success Probability</span>
          <span className={`font-bold ${probability >= 80 ? 'text-green-400' : probability >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
            {Math.round(probability)}%
          </span>
        </div>
        <div className="h-2 bg-slate-600 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${probability >= 80 ? 'bg-green-500' : probability >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
            style={{ width: `${Math.min(100, probability)}%` }}
          />
        </div>
      </div>

      {/* Recommendation */}
      <div className="mt-4 p-3 bg-blue-900 rounded border border-blue-600 text-sm">
        <p className="text-blue-100">
          {isAchievable
            ? `You can reach ${targetScore} in 16 weeks by following recommended actions.`
            : `Currently projected to reach ${Math.round(projectedScore)}. Increase target to be realistic.`}
        </p>
      </div>
    </div>
  );
}
