'use client'

import { useEffect, useState } from 'react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import ScoreCard from './ScoreCard'
import SubscoreChart from './SubscoreChart'
import RecommendationsPanel from './RecommendationsPanel'
import AccountsList from './AccountsList'
import ScenarioSimulator from './ScenarioSimulator'
import ScoreTrends from './ScoreTrends'
import toast, { Toaster } from 'react-hot-toast'

interface ScoreTrend {
  date: string
  score: number
}



export default function Dashboard() {
  const { profile, score, setScore, setLoading, setError, currentProfileId } = useStore()
  const [scoreTrends, setScoreTrends] = useState<ScoreTrend[]>([])

  useEffect(() => {
    calculateScore()
    if (currentProfileId) {
      fetchScoreTrends()
    }
  }, [profile, currentProfileId])

  const calculateScore = async () => {
    if (profile.accounts.length === 0) return

    try {
      setLoading(true)
      const result = await apiClient.calculateScore(profile)
      setScore(result)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      toast.error('Failed to calculate score')
    } finally {
      setLoading(false)
    }
  }

  const fetchScoreTrends = async () => {
    if (!currentProfileId) return
    try {
      const trends = await apiClient.getScoreHistory(currentProfileId)
      setScoreTrends(trends)
    } catch (err) {
      console.log('No score history yet')
    }
  }

  return (
    <div className="space-y-8">
      <Toaster position="top-right" />

      {/* Score and Subscores */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          {score && <ScoreCard score={score} />}
        </div>
        <div className="lg:col-span-2">
          {score && <SubscoreChart score={score} />}
        </div>
      </div>

      {/* Score Trends */}
      {scoreTrends.length > 0 && (
        <div className="bg-slate-700 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Score History</h2>
          <ScoreTrends data={scoreTrends} />
        </div>
      )}

      {/* Accounts Overview */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Your Accounts</h2>
        <AccountsList accounts={profile.accounts} />
      </div>

      {/* Recommendations and Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <RecommendationsPanel profile={profile} />
        <ScenarioSimulator profile={profile} />
      </div>
    </div>
  )
}
