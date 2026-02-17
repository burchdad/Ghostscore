'use client';

/**
 * SimulatorSlider
 * Live credit score simulator - adjust balances and see score impact in real-time
 */

import { useState, useEffect } from 'react';
import { Minus, Plus } from 'lucide-react';

interface Account {
  id?: string;
  name?: string;
  type: string;
  balance: number;
  limit?: number;
}

interface SimulatorSliderProps {
  accounts: Account[];
  onSimulation?: (updatedAccounts: Account[], newScore: number) => void;
}

export default function SimulatorSlider({
  accounts,
  onSimulation,
}: SimulatorSliderProps) {
  const [simulatedAccounts, setSimulatedAccounts] = useState<Account[]>(accounts);
  const [simulatedScore, setSimulatedScore] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Calculate utilization for each account
  const getUtilization = (account: Account) => {
    if (!account.limit || account.limit === 0) return 0;
    return parseFloat(((account.balance / account.limit) * 100).toFixed(1));
  };

  // Handle balance slider change
  const handleBalanceChange = (index: number, newBalance: number) => {
    const updated = [...simulatedAccounts];
    updated[index] = { ...updated[index], balance: Math.max(0, newBalance) };
    setSimulatedAccounts(updated);
  };

  // Simulate score update
  useEffect(() => {
    const simulate = async () => {
      setIsLoading(true);
      try {
        // Convert to API format
        const profileData = {
          accounts: simulatedAccounts.map((acc) => ({
            type: acc.type,
            name: acc.name || 'Unknown',
            balance: acc.balance,
            limit: acc.limit || 0,
            open_date: new Date().toISOString().split('T')[0],
            status: 'active',
          })),
          derogatories: [],
        };

        const response = await fetch('/api/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profileData),
        });

        if (response.ok) {
          const data = await response.json();
          setSimulatedScore(data.score);
          onSimulation?.(simulatedAccounts, data.score);
        }
      } catch (error) {
        console.error('Simulation error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const timer = setTimeout(simulate, 500);
    return () => clearTimeout(timer);
  }, [simulatedAccounts, onSimulation]);

  // Reset to original
  const handleReset = () => {
    setSimulatedAccounts(accounts);
  };

  // Pay down to 9% utilization (sweet spot)
  const handleQuickWin = (index: number) => {
    const account = simulatedAccounts[index];
    if (account.limit) {
      const targetBalance = account.limit * 0.09;
      handleBalanceChange(index, targetBalance);
    }
  };

  // Pay off completely
  const handlePayOff = (index: number) => {
    handleBalanceChange(index, 0);
  };

  return (
    <div className="w-full bg-white rounded-lg border border-slate-200 p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              Score Simulator
            </h3>
            <p className="text-sm text-slate-600 mt-1">
              Adjust balances to see the impact on your credit score
            </p>
          </div>
          {simulatedScore !== null && (
            <div className="text-right">
              <p className="text-xs text-slate-600">Simulated Score</p>
              <p className="text-3xl font-bold text-blue-600">{simulatedScore}</p>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {simulatedAccounts.map((account, index) => (
          <div
            key={index}
            className="p-4 bg-slate-50 rounded-lg border border-slate-200"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="font-semibold text-slate-900">
                  {account.name || 'Account'}
                </h4>
                <p className="text-sm text-slate-600 capitalize">
                  {account.type.replace(/_/g, ' ')}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-600">Current Balance</p>
                <p className="text-lg font-bold text-slate-900">
                  ${account.balance.toLocaleString('en-US', {
                    maximumFractionDigits: 0,
                  })}
                </p>
              </div>
            </div>

            {/* Slider */}
            <div className="mb-4">
              <input
                type="range"
                min="0"
                max={account.limit || 10000}
                value={account.balance}
                onChange={(e) =>
                  handleBalanceChange(index, parseFloat(e.target.value))
                }
                className="w-full h-2 bg-slate-300 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Utilization Display */}
            {account.limit && (
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Utilization</span>
                  <span className="font-semibold text-slate-900">
                    {getUtilization(account)}%
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-300 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      getUtilization(account) <= 9
                        ? 'bg-green-500'
                        : getUtilization(account) <= 30
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                    }`}
                    style={{
                      width: `${Math.min(
                        getUtilization(account),
                        100
                      )}%`,
                    }}
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {getUtilization(account) <= 9
                    ? 'Excellent (< 10%)'
                    : getUtilization(account) <= 30
                      ? 'Good (< 30%)'
                      : 'Needs improvement (> 30%)'}
                </p>
              </div>
            )}

            {/* Quick Actions */}
            <div className="flex gap-2">
              {account.limit && (
                <button
                  onClick={() => handleQuickWin(index)}
                  className="flex-1 px-3 py-2 text-sm font-medium bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  Pay to 9%
                </button>
              )}
              <button
                onClick={() => handlePayOff(index)}
                className="flex-1 px-3 py-2 text-sm font-medium bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
              >
                Pay Off
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex gap-3">
        <button
          onClick={handleReset}
          className="flex-1 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
        >
          Reset
        </button>
        {isLoading && (
          <div className="flex items-center gap-2 px-4 py-2 text-sm text-slate-600">
            <div className="animate-spin w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full" />
            Calculating...
          </div>
        )}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <strong>Pro Tip:</strong> Aim for credit utilization below 9% for the best score
          impact. Even paying down to 30% shows significant improvement.
        </p>
      </div>
    </div>
  );
}
