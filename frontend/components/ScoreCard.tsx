'use client'

import { ScoreResponse } from '@/lib/api'

interface ScoreCardProps {
  score: ScoreResponse
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 750) return 'from-green-600 to-green-400'
    if (score >= 670) return 'from-blue-600 to-blue-400'
    if (score >= 580) return 'from-yellow-600 to-yellow-400'
    return 'from-red-600 to-red-400'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 750) return 'Excellent'
    if (score >= 670) return 'Good'
    if (score >= 580) return 'Fair'
    return 'Poor'
  }

  return (
    <div className={`bg-gradient-to-br ${getScoreColor(score.score)} rounded-lg p-8 text-white shadow-lg`}>
      <div className="text-sm opacity-90 mb-2">Estimated FICO Score</div>
      <div className="text-5xl font-bold mb-2">{score.score}</div>
      <div className="text-lg opacity-90">{getScoreLabel(score.score)}</div>
      <div className="text-xs opacity-75 mt-4">Range: 300-850</div>
    </div>
  )
}
