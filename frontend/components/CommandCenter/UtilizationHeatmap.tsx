'use client';

import { CreditProfile } from '@/lib/api';

interface UtilizationHeatmapProps {
  accounts: any[];
}

export default function UtilizationHeatmap({ accounts }: UtilizationHeatmapProps) {
  const getUtilizationColor = (utilization: number) => {
    if (utilization <= 8) return 'bg-blue-100 text-blue-900 border-blue-300';
    if (utilization <= 28) return 'bg-green-100 text-green-900 border-green-300';
    if (utilization <= 68) return 'bg-amber-100 text-amber-900 border-amber-300';
    return 'bg-red-100 text-red-900 border-red-300';
  };

  const getUtilizationBadge = (utilization: number) => {
    if (utilization <= 8) return '✓ Optimal';
    if (utilization <= 28) return '✓ Good';
    if (utilization <= 68) return '⚠ Improve';
    return '✗ Critical';
  };

  const cardAccounts = accounts.filter((acc) => ['credit_card', 'revolving'].includes(acc.type?.toLowerCase()));
  const totalBalance = cardAccounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);
  const totalLimit = cardAccounts.reduce((sum, acc) => sum + (acc.limit || 0), 0);
  const overallUtilization = totalLimit > 0 ? (totalBalance / totalLimit) * 100 : 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">Utilization Heatmap</h2>

      {/* Overall Utilization */}
      <div className="mb-6 p-4 bg-slate-50 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="font-semibold text-slate-800">Total Utilization</span>
          <span className="text-2xl font-bold text-slate-900">{Math.round(overallUtilization)}%</span>
        </div>
        <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 via-amber-500 to-red-500 transition-all"
            style={{ width: `${Math.min(100, overallUtilization)}%` }}
          />
        </div>
        <p className="text-xs text-slate-600 mt-2">Target: Keep under 30% for optimal score</p>
      </div>

      {/* Individual Cards */}
      <div className="space-y-3">
        {cardAccounts.map((account) => {
          const util = account.limit ? (account.balance / account.limit) * 100 : 0;
          return (
            <div key={account.id} className={`p-3 rounded-lg border-2 ${getUtilizationColor(util)}`}>
              <div className="flex justify-between items-center mb-2">
                <div>
                  <p className="font-semibold">{account.name}</p>
                  <p className="text-xs opacity-70">
                    ${account.balance || 0} / ${account.limit || 0}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">{Math.round(util)}%</p>
                  <p className="text-xs font-semibold">{getUtilizationBadge(util)}</p>
                </div>
              </div>
              <div className="h-2 bg-black/10 rounded-full overflow-hidden">
                <div className="h-full bg-current" style={{ width: `${Math.min(100, util)}%` }} />
              </div>
            </div>
          );
        })}
      </div>

      {cardAccounts.length === 0 && (
        <p className="text-center text-slate-500 py-4">No credit cards in profile</p>
      )}
    </div>
  );
}
