'use client'

import { useState } from 'react'
import { apiClient, CreditProfile } from '@/lib/api'
import toast from 'react-hot-toast'

interface RecommendationsPanelProps {
  profile: CreditProfile
}

interface Recommendation {
  action: string
  account?: string
  current_balance?: number
  target_balance?: number
  amount_to_pay?: number
  score_gain?: number
  priority?: string
  item?: string
  date?: string
  years_remaining?: number
  note?: string
}

export default function RecommendationsPanel({ profile }: RecommendationsPanelProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [potentialGain, setPotentialGain] = useState(0)
  const [loading, setLoading] = useState(false)

  const handleGetRecommendations = async () => {
    try {
      setLoading(true)
      const result = await apiClient.getRecommendations(profile)
      setRecommendations(result.recommendations)
      setPotentialGain(result.estimated_potential_gain)
      toast.success('Recommendations generated!')
    } catch (err) {
      toast.error('Failed to get recommendations')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6 text-white">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">Recommendations</h3>
        <button
          onClick={handleGetRecommendations}
          disabled={loading || profile.accounts.length === 0}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded font-semibold transition"
        >
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {potentialGain > 0 && (
        <div className="mb-6 p-4 bg-green-900 rounded border border-green-600">
          <div className="text-sm text-green-200">Estimated Potential Gain</div>
          <div className="text-3xl font-bold text-green-400">+{potentialGain} points</div>
        </div>
      )}

      <div className="space-y-4">
        {recommendations.length === 0 ? (
          <p className="text-slate-400 text-center py-8">Click "Get Recommendations" to see optimization strategies</p>
        ) : (
          recommendations.map((rec, idx) => (
            <div
              key={idx}
              className="p-4 bg-slate-600 rounded border-l-4 border-blue-500"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold">
                    {rec.action === 'paydown' ? `Pay down ${rec.account}` : rec.note}
                  </h4>
                </div>
                {rec.priority && (
                  <span className={`text-xs px-2 py-1 rounded ${
                    rec.priority === 'high' ? 'bg-red-600' : 'bg-yellow-600'
                  }`}>
                    {rec.priority.toUpperCase()}
                  </span>
                )}
              </div>

              {rec.action === 'paydown' && (
                <div className="space-y-1 text-sm text-slate-300">
                  <div>Current: ${rec.current_balance?.toFixed(2)}</div>
                  <div>Target: ${rec.target_balance?.toFixed(2)}</div>
                  <div className="font-semibold text-green-400">
                    Impact: +{rec.score_gain} points
                  </div>
                </div>
              )}

              {rec.action === 'wait' && (
                <div className="text-sm text-slate-300">
                  {rec.years_remaining} years remaining
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
