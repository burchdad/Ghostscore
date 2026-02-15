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
import ScoreTrajectoryChart from './ScoreTrajectoryChart'
import ActionPriorityList from './ActionPriorityList'
import ScoreFactorsRadar from './ScoreFactorsRadar'
import SimulatorSlider from './SimulatorSlider'
import toast, { Toaster } from 'react-hot-toast'

interface ScoreTrend {
  date: string
  score: number
}

interface TimelinePoint {
  week: number
  score: number
  milestone: string
}

interface Action {
  type: string
  priority: string
  account_name: string
  estimated_gain: number
  description: string
}

interface OptimizeResponse {
  current_score: number
  scorecard: string
  scorecard_description: string
  recommended_actions: Action[]
  improvement_timeline: TimelinePoint[]
  total_potential_gain: number
}



export default function Dashboard() {
  const { profile, score, setScore, setLoading, setError, currentProfileId } = useStore()
  const [scoreTrends, setScoreTrends] = useState<ScoreTrend[]>([])
  const [optimizeData, setOptimizeData] = useState<OptimizeResponse | null>(null)
  const [selectedActions, setSelectedActions] = useState<number[]>([])
  const [scenarioScore, setScenarioScore] = useState<number | null>(null)
  const [confidenceScenarios, setConfidenceScenarios] = useState<{
    optimistic: number
    realistic: number
    conservative: number
  } | null>(null)

  useEffect(() => {
    calculateScore()
    if (currentProfileId) {
      fetchScoreTrends()
    }
  }, [profile, currentProfileId])

  useEffect(() => {
    runOptimizer()
  }, [profile, score])

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

  const runOptimizer = async () => {
    if (profile.accounts.length === 0) return

    try {
      const response = await apiClient.post('/optimize', profile)
      setOptimizeData(response)
      
      // Calculate confidence intervals
      const baseGain = response.total_potential_gain
      setConfidenceScenarios({
        optimistic: response.current_score + baseGain,
        realistic: response.current_score + (baseGain * 0.7),
        conservative: response.current_score + (baseGain * 0.4),
      })
    } catch (err) {
      console.log('Optimizer not available')
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

  const handleActionToggle = (actionIndex: number) => {
    setSelectedActions(prev =>
      prev.includes(actionIndex)
        ? prev.filter(i => i !== actionIndex)
        : [...prev, actionIndex]
    )
  }

  const simulateMultiActionScenario = async () => {
    if (selectedActions.length === 0) {
      toast.error('Select at least one action')
      return
    }

    try {
      // Simulate each selected action sequentially
      let simulatedProfile = { ...profile }
      let totalGain = 0

      for (const actionIdx of selectedActions) {
        const action = optimizeData?.recommended_actions[actionIdx]
        if (!action) continue

        // Apply action to profile
        simulatedProfile.accounts = simulatedProfile.accounts.map(acc => {
          if (acc.name === action.account_name) {
            if (action.type === 'paydown') {
              return { ...acc, balance: action.estimated_gain }
            } else if (action.type === 'payoff') {
              return { ...acc, balance: 0 }
            }
          }
          return acc
        })
        totalGain += action.estimated_gain
      }

      // Calculate new score
      const result = await apiClient.calculateScore(simulatedProfile)
      setScenarioScore(result.score)
      toast.success(`Projected score: ${result.score} (+${totalGain} points)`)
    } catch (err) {
      toast.error('Failed to calculate scenario')
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

      {/* Score Factors Radar */}
      {score && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <ScoreFactorsRadar score={score} />
        </div>
      )}

      {/* Confidence Intervals Section */}
      {confidenceScenarios && score && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <p className="text-xs font-semibold text-green-600 uppercase">Optimistic</p>
            <p className="text-2xl font-bold text-green-700 mt-2">
              {confidenceScenarios.optimistic.toFixed(0)}
            </p>
            <p className="text-xs text-green-600 mt-1">
              +{(confidenceScenarios.optimistic - score.score).toFixed(0)} points
            </p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <p className="text-xs font-semibold text-blue-600 uppercase">Realistic</p>
            <p className="text-2xl font-bold text-blue-700 mt-2">
              {confidenceScenarios.realistic.toFixed(0)}
            </p>
            <p className="text-xs text-blue-600 mt-1">
              +{(confidenceScenarios.realistic - score.score).toFixed(0)} points
            </p>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <p className="text-xs font-semibold text-amber-600 uppercase">Conservative</p>
            <p className="text-2xl font-bold text-amber-700 mt-2">
              {confidenceScenarios.conservative.toFixed(0)}
            </p>
            <p className="text-xs text-amber-600 mt-1">
              +{(confidenceScenarios.conservative - score.score).toFixed(0)} points
            </p>
          </div>
        </div>
      )}

      {/* Improvement Timeline */}
      {optimizeData && (
        <ScoreTrajectoryChart
          timeline={optimizeData.improvement_timeline}
          currentScore={optimizeData.current_score}
          potentialGain={optimizeData.total_potential_gain}
        />
      )}

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

      {/* Action Priority List with Multi-Select */}
      {optimizeData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-slate-900">Recommended Actions</h2>
            <button
              onClick={simulateMultiActionScenario}
              disabled={selectedActions.length === 0}
              className={`px-4 py-2 rounded font-semibold transition ${
                selectedActions.length === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              Simulate {selectedActions.length > 0 ? `(${selectedActions.length})` : ''}
            </button>
          </div>
          <ActionPriorityList
            actions={optimizeData.recommended_actions}
            onSelect={handleActionToggle}
            selectedIndexes={selectedActions}
          />
          {scenarioScore && (
            <div className="mt-4 p-4 bg-blue-50 rounded border border-blue-200">
              <p className="text-sm text-blue-700">
                Projected score after selected actions: <span className="font-bold text-lg">{scenarioScore}</span>
              </p>
            </div>
          )}
        </div>
      )}

      {/* Scenario Simulator and Live Adjustment */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Quick Actions</h2>
          <RecommendationsPanel profile={profile} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Manual Scenario</h2>
          <ScenarioSimulator profile={profile} />
        </div>
      </div>
    </div>
  )
}
