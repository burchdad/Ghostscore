'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface StabilityData {
  stability_index: number
  confidence: number
  payment_history_stability: number
  utilization_stability: number
  account_age_stability: number
  derogatory_volatility: number
}

interface ScoreStabilityPanelProps {
  profileId: string
}

export default function ScoreStabilityPanel({ profileId }: ScoreStabilityPanelProps) {
  const [stability, setStability] = useState<StabilityData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!profileId) return

    const fetchStability = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await fetch(`/api/profiles/${profileId}/stability`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (!response.ok) {
          // Stability endpoint may not be available, which is okay
          setLoading(false)
          return
        }
        
        const data = await response.json()
        setStability(data)
      } catch (err) {
        // Silently fail if stability endpoint is not available
        console.log('Stability index not available')
      } finally {
        setLoading(false)
      }
    }

    fetchStability()
  }, [profileId])

  if (loading) {
    return (
      <div className="bg-slate-700 rounded-lg p-6 text-white">
        <div className="animate-pulse">
          <div className="h-4 bg-slate-600 rounded w-1/3 mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-slate-600 rounded w-2/3"></div>
            <div className="h-3 bg-slate-600 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!stability) {
    return null
  }

  const getStabilityColor = (index: number) => {
    if (index >= 60) return 'from-green-600 to-green-400'
    if (index >= 30) return 'from-yellow-600 to-yellow-400'
    return 'from-red-600 to-red-400'
  }

  const getStabilityLabel = (index: number) => {
    if (index >= 60) return 'Stable'
    if (index >= 30) return 'Moderate'
    return 'Volatile'
  }

  const getConfidenceLabel = (conf: number) => {
    if (conf >= 0.8) return 'Very High'
    if (conf >= 0.6) return 'High'
    if (conf >= 0.4) return 'Moderate'
    return 'Low'
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6 text-white mb-8">
      <h3 className="text-xl font-bold mb-6">Score Stability Index</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Stability Index Card */}
        <div className={`bg-gradient-to-br ${getStabilityColor(stability.stability_index)} rounded-lg p-6 shadow-lg`}>
          <div className="text-sm opacity-90 mb-2">Stability Index</div>
          <div className="text-4xl font-bold mb-2">{Math.round(stability.stability_index)}</div>
          <div className="text-lg opacity-90">{getStabilityLabel(stability.stability_index)}</div>
          <div className="text-xs opacity-75 mt-3">Range: 0-100 (Higher is better)</div>
        </div>

        {/* Confidence Card */}
        <div className="bg-slate-600 rounded-lg p-6">
          <div className="text-sm opacity-90 mb-2">Overall Confidence</div>
          <div className="text-4xl font-bold mb-2">{Math.round(stability.confidence * 100)}%</div>
          <div className="text-lg opacity-90">{getConfidenceLabel(stability.confidence)}</div>
          <div className="text-xs opacity-75 mt-3">Prediction reliability</div>
        </div>
      </div>

      {/* Stability Metrics Breakdown */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-600 bg-opacity-50 rounded p-4">
          <div className="text-sm text-slate-300 mb-2">Payment History Stability</div>
          <div className="flex items-center">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, stability.payment_history_stability * 100)}%` }}
              ></div>
            </div>
            <span className="ml-3 text-sm font-semibold">{Math.round(stability.payment_history_stability * 100)}%</span>
          </div>
        </div>

        <div className="bg-slate-600 bg-opacity-50 rounded p-4">
          <div className="text-sm text-slate-300 mb-2">Utilization Stability</div>
          <div className="flex items-center">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-purple-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, stability.utilization_stability * 100)}%` }}
              ></div>
            </div>
            <span className="ml-3 text-sm font-semibold">{Math.round(stability.utilization_stability * 100)}%</span>
          </div>
        </div>

        <div className="bg-slate-600 bg-opacity-50 rounded p-4">
          <div className="text-sm text-slate-300 mb-2">Account Age Stability</div>
          <div className="flex items-center">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, stability.account_age_stability * 100)}%` }}
              ></div>
            </div>
            <span className="ml-3 text-sm font-semibold">{Math.round(stability.account_age_stability * 100)}%</span>
          </div>
        </div>

        <div className="bg-slate-600 bg-opacity-50 rounded p-4">
          <div className="text-sm text-slate-300 mb-2">Derogatory Volatility</div>
          <div className="flex items-center">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-red-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, stability.derogatory_volatility * 100)}%` }}
              ></div>
            </div>
            <span className="ml-3 text-sm font-semibold">{Math.round(stability.derogatory_volatility * 100)}%</span>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-slate-600 bg-opacity-50 rounded text-sm text-slate-300">
        <p className="text-xs text-slate-400 mb-2">💡 What does this mean?</p>
        <p>
          A higher stability index means your credit profile is more predictable and less volatile. 
          This gives more confidence in credit score forecasts and model predictions.
        </p>
      </div>
    </div>
  )
}
