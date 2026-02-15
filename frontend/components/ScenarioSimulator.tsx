'use client'

import { useState } from 'react'
import { apiClient, CreditProfile } from '@/lib/api'
import toast from 'react-hot-toast'

interface ScenarioSimulatorProps {
  profile: CreditProfile
}

export default function ScenarioSimulator({ profile }: ScenarioSimulatorProps) {
  const [selectedAccountId, setSelectedAccountId] = useState<string>('')
  const [targetBalance, setTargetBalance] = useState<number>(0)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    if (!selectedAccountId) {
      toast.error('Please select an account')
      return
    }

    try {
      setLoading(true)
      const simulationResult = await apiClient.simulatePaydown(
        profile,
        selectedAccountId,
        targetBalance
      )
      setResult(simulationResult)
      toast.success('Simulation complete!')
    } catch (err) {
      toast.error('Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6 text-white">
      <h3 className="text-xl font-bold mb-6">Scenario Simulator</h3>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Select Account
          </label>
          <select
            value={selectedAccountId}
            onChange={(e) => setSelectedAccountId(e.target.value)}
            className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
          >
            <option value="">Choose an account...</option>
            {profile.accounts.map((acc) => (
              <option key={acc.id} value={acc.id}>
                {acc.name} (Current: ${acc.balance.toFixed(2)})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Target Balance ($)
          </label>
          <input
            type="number"
            value={targetBalance}
            onChange={(e) => setTargetBalance(parseFloat(e.target.value) || 0)}
            step="10"
            className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
          />
        </div>

        <button
          onClick={handleSimulate}
          disabled={loading || !selectedAccountId}
          className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded font-semibold transition"
        >
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      {result && (
        <div className="space-y-4 border-t border-slate-600 pt-4">
          <div className="p-4 bg-slate-600 rounded">
            <div className="text-sm text-slate-300 mb-1">Current Score</div>
            <div className="text-2xl font-bold text-blue-400">{result.original_score}</div>
          </div>

          <div className="p-4 bg-slate-600 rounded">
            <div className="text-sm text-slate-300 mb-1">Potential Score</div>
            <div className="text-2xl font-bold text-green-400">{result.new_score}</div>
          </div>

          <div className={`p-4 rounded text-center ${
            result.score_delta >= 0
              ? 'bg-green-900 border border-green-600'
              : 'bg-red-900 border border-red-600'
          }`}>
            <div className="text-sm mb-1">Score Change</div>
            <div className="text-3xl font-bold">
              {result.score_delta >= 0 ? '+' : ''}{result.score_delta}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
