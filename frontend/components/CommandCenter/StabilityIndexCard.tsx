'use client';

import { Shield } from 'lucide-react';

interface StabilityIndexCardProps {
  stabilityIndex?: { stability_index: number; risk_level: string } | null;
}

export default function StabilityIndexCard({ stabilityIndex }: StabilityIndexCardProps) {
  if (!stabilityIndex) {
    return null;
  }

  const stability = stabilityIndex.stability_index;
  const riskLevel = stabilityIndex.risk_level || 'MEDIUM';

  const getRiskColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'LOW':
        return 'bg-green-50 border-green-200 text-green-900';
      case 'MEDIUM':
        return 'bg-amber-50 border-amber-200 text-amber-900';
      case 'HIGH':
        return 'bg-red-50 border-red-200 text-red-900';
      default:
        return 'bg-slate-50 border-slate-200 text-slate-900';
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'LOW':
        return 'bg-green-100 text-green-800';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800';
      case 'HIGH':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  return (
    <div className={`rounded-lg shadow-md p-6 border ${getRiskColor(riskLevel)}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield size={24} />
          <h2 className="text-2xl font-bold">Score Stability</h2>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRiskBadgeColor(riskLevel)}`}>
          {riskLevel} RISK
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm opacity-80 mb-1">Stability Index</p>
          <p className="text-4xl font-bold">{Math.round(stability)}</p>
          <p className="text-xs opacity-70 mt-1">/ 100</p>
        </div>
        <div>
          <p className="text-sm opacity-80 mb-1">Resilience</p>
          <div className="h-2 bg-current opacity-20 rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-current opacity-80 transition-all"
              style={{ width: `${stability}%` }}
            />
          </div>
          <p className="text-xs opacity-70">
            {stability >= 80 ? 'Very stable' : stability >= 60 ? 'Moderately stable' : 'Fluctuates'}
          </p>
        </div>
      </div>

      <div className="mt-4 p-3 rounded opacity-90 bg-current bg-opacity-10">
        <p className="text-sm">
          {riskLevel === 'LOW'
            ? '✓ Your score is expected to be resilient and unlikely to fluctuate unexpectedly.'
            : riskLevel === 'MEDIUM'
              ? '⚠ Monitor your credit activity closely over the next few weeks.'
              : '⚠ Your score may be more susceptible to sudden changes. Be proactive.'}
        </p>
      </div>
    </div>
  );
}
