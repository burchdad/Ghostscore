// Download action plan PDF for the current profile
const downloadActionPlan = async (profileId: string) => {
  if (!profileId) return
  try {
    const blob = await apiClient.downloadActionPlanPdf(profileId)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `action_plan_${profileId}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    toast.success('Action plan PDF downloaded!')
  } catch (err) {
    toast.error('Failed to download action plan PDF')
  }
}
'use client'

import { useEffect, useState } from 'react'
// Download PDF report for the current profile
const downloadProfileReport = async (profileId: string) => {
  if (!profileId) return
  try {
    const blob = await apiClient.downloadProfilePdf(profileId)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `profile_${profileId}_report.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    toast.success('PDF report downloaded!')
  } catch (err) {
    toast.error('Failed to download PDF report')
  }
}

import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import ScoreCard from './ScoreCard'
import SubscoreChart from './SubscoreChart'
import RecommendationsPanel from './RecommendationsPanel'
import AccountsList from './AccountsList'
import ScenarioSimulator from './ScenarioSimulator'
import ScoreTrends from './ScoreTrends'
import ScoreTrajectoryChart from './ScoreTrajectoryChart'

// ML Score Forecast Chart
import { useEffect as useEffectML, useState as useStateML } from 'react'
  // ML Score Forecast state
  const [mlForecast, setMlForecast] = useStateML<number[] | null>(null)
  const [mlForecastWeeks, setMlForecastWeeks] = useStateML<number>(16)
  // Fetch ML score forecast when profile changes
  useEffectML(() => {
    const fetchForecast = async () => {
      if (!profile || profile.accounts.length === 0) {
        setMlForecast(null)
        return
      }
      try {
        const resp = await apiClient.forecastScore(profile, mlForecastWeeks)
        setMlForecast(resp.forecast)
        setMlForecastWeeks(resp.weeks)
      } catch (err) {
        setMlForecast(null)
      }
    }
    fetchForecast()
  }, [profile, mlForecastWeeks])
import ScoreFactorsRadar from './ScoreFactorsRadar'
import ScenarioHistory from './ScenarioHistory'
import ActionPriorityList from './ActionPriorityList'
import type { Action } from './ActionPriorityList'
import SimulatorSlider from './SimulatorSlider'
import toast, { Toaster } from 'react-hot-toast'
import { useRef, useCallback } from 'react'

// CalibrationPanel: Modal for calibration actions
function CalibrationPanel({ open, onClose, onCalibrate, loading, result }: { open: boolean, onClose: () => void, onCalibrate: () => void, loading: boolean, result: string | null }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Calibration Engine</h2>
        <p className="mb-4 text-slate-700 text-sm">Run calibration on your current profile to improve score accuracy using your real credit report data.</p>
        {result && <div className="mb-4 p-3 bg-green-100 text-green-800 rounded text-sm">{result}</div>}
        <div className="flex gap-3">
          <button
            onClick={onCalibrate}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded font-semibold transition"
          >
            {loading ? 'Calibrating...' : 'Run Calibration'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded font-semibold transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

interface ScoreTrend {
  date: string
  score: number
}

interface TimelinePoint {
  week: number
  score: number
  milestone: string
}



interface OptimizeResponse {
  current_score: number
  scorecard: string
  scorecard_description: string
  recommended_actions: Action[]
  improvement_timeline: TimelinePoint[]
  total_potential_gain: number
}

// Save a score snapshot after calculating score
const saveScoreSnapshot = async (profileId: string, scoreData: any) => {
  if (!profileId) return
  try {
    await apiClient.saveScoreSnapshot(profileId, scoreData)
  } catch (err) {
    console.log('Failed to save score snapshot')
  }
}

// Save scenario run to backend after simulation
const saveScenarioRun = async (profileId: string, actions: any[], originalScore: number, simulatedScore: number, timeline: any[] = [], notes: string = '') => {
  if (!profileId) return
  try {
    await apiClient.saveScenarioHistory(profileId, {
      actions,
      original_score: originalScore,
      simulated_score: simulatedScore,
      actual_gain: simulatedScore - originalScore,
      timeline,
      notes,
    })
    toast.success('Scenario saved to history!')
  } catch (err) {
    toast.error('Failed to save scenario history')
  }
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
  // Calibration modal state
  const [calibOpen, setCalibOpen] = useState(false)
  const [calibLoading, setCalibLoading] = useState(false)
  const [calibResult, setCalibResult] = useState<string | null>(null)

  useEffect(() => {
    calculateScore()
    if (currentProfileId) {
      fetchScoreTrends()
    }
  }, [profile, currentProfileId])

  useEffect(() => {
    runOptimizer()
  }, [profile, score])

  // Calibration handler
  const handleCalibrate = useCallback(async () => {
    if (!currentProfileId) return
    setCalibLoading(true)
    setCalibResult(null)
    try {
      const resp = await apiClient.calibrateProfile(currentProfileId)
      setCalibResult(resp?.message || 'Calibration complete!')
      toast.success('Calibration complete!')
    } catch (err) {
      setCalibResult('Calibration failed.')
      toast.error('Calibration failed')
    } finally {
      setCalibLoading(false)
    }
  }, [currentProfileId])

  const calculateScore = async () => {
    if (profile.accounts.length === 0) return

    try {
      setLoading(true)
      const result = await apiClient.calculateScore(profile)
      setScore(result)
      setError(null)
      // Save score snapshot for persistent tracking
      await saveScoreSnapshot(currentProfileId, result)
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
      const response = await fetch('/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      }).then(res => res.json())
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
      const trends = await apiClient.getScoreHistoryFull(currentProfileId)
      setScoreTrends(trends.map(e => ({ date: e.created_at, score: e.score })))
    } catch (err) {
      console.log('No score history yet')
    }
  }

  const handleActionToggle = (actionIndex: number) => {
    setSelectedActions(prev =>
      prev.includes(actionIndex)
        ? prev.filter(i => i !== actionIndex)
        : [...prev, actionIndex]
    );
  };

  const simulateMultiActionScenario = async () => {
    if (selectedActions.length === 0) {
      toast.error('Select at least one action');
      return;
    }

    try {
      let simulatedProfile = { ...profile };
      let totalGain = 0;
      let actionsApplied: any[] = [];
      for (const actionIdx of selectedActions) {
        const action = optimizeData?.recommended_actions[actionIdx];
        if (!action) continue;
        simulatedProfile.accounts = simulatedProfile.accounts.map(acc => {
          if (acc.name === action.account_name) {
            if (action.type === 'paydown') {
              return { ...acc, balance: action.estimated_gain };
            } else if (action.type === 'payoff') {
              return { ...acc, balance: 0 };
            }
          }
          return acc;
        });
        totalGain += action.estimated_gain;
        actionsApplied.push(action);
      }
      const result = await apiClient.calculateScore(simulatedProfile);
      setScenarioScore(result.score);
      toast.success(`Projected score: ${result.score} (+${totalGain} points)`);
      // Save scenario run to backend
      await saveScenarioRun(currentProfileId, actionsApplied, score?.score ?? 0, result.score);
    } catch (err) {
      toast.error('Failed to calculate scenario');
    }
  };

  return (
    <div className="space-y-8">
      {/* Download Report, Action Plan, and Calibration Buttons */}
      {currentProfileId && (
        <div className="flex justify-end gap-2">
          <button
            onClick={() => downloadProfileReport(currentProfileId)}
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-4 py-2 rounded shadow mb-2"
          >
            Download Report (PDF)
          </button>
          <button
            onClick={() => downloadActionPlan(currentProfileId)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded shadow mb-2"
          >
            Download Action Plan (PDF)
          </button>
          <button
            onClick={() => setCalibOpen(true)}
            className="bg-orange-600 hover:bg-orange-700 text-white font-semibold px-4 py-2 rounded shadow mb-2"
          >
            Calibrate
          </button>
        </div>
      )}
      <CalibrationPanel open={calibOpen} onClose={() => setCalibOpen(false)} onCalibrate={handleCalibrate} loading={calibLoading} result={calibResult} />
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
          <ScoreFactorsRadar
            subscores={score}
            scorecard={optimizeData?.scorecard || ''}
            totalScore={score.score}
          />
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

      {/* Improvement Timeline & ML Forecast */}
      {optimizeData && (
        <div>
          <ScoreTrajectoryChart
            timeline={optimizeData.improvement_timeline}
            currentScore={optimizeData.current_score}
            potentialGain={optimizeData.total_potential_gain}
          />
          {mlForecast && mlForecast.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-purple-700 mb-2">ML Predicted Score Trajectory</h3>
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <ul className="grid grid-cols-4 gap-2">
                  {mlForecast.map((score, idx) => (
                    <li key={idx} className="text-center text-purple-900 text-sm">
                      <span className="font-bold">Week {idx + 1}:</span> {score.toFixed(0)}
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-purple-700">Powered by ML regression model. Actual results may vary.</p>
              </div>
            </div>
          )}
        </div>
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
              actions={optimizeData.recommended_actions.map((a, idx) => ({ ...a, _idx: idx }))}
              onSelectAction={(action: Action & { _idx?: number }) => {
                if (typeof action._idx === 'number') handleActionToggle(action._idx)
              }}
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

      {/* Scenario History */}
      {currentProfileId && (
        <ScenarioHistory profileId={currentProfileId} />
      )}
    </div>
  )
}
