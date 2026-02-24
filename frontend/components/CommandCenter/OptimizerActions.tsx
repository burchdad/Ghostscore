'use client';

import { CheckCircle2, AlertCircle, TrendingUp, DollarSign, XCircle } from 'lucide-react';

interface OptimizerActionsProps {
  actions: any[];
  currentScore?: number;
}

export default function OptimizerActions({ actions, currentScore = 0 }: OptimizerActionsProps) {
  if (!actions || actions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
        <p className="text-slate-600">No recommendations available</p>
      </div>
    );
  }

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'paydown':
        return <DollarSign className="text-blue-600" size={20} />;
      case 'payoff':
        return <CheckCircle2 className="text-green-600" size={20} />;
      case 'derogatory_removal':
        return <XCircle className="text-red-600" size={20} />;
      default:
        return <TrendingUp className="text-slate-600" size={20} />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-50 border-red-200';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200';
      case 'low':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-slate-50 border-slate-200';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Recommended Actions (Ranked)</h2>

      <div className="space-y-4">
        {actions.map((action, idx) => (
          <div key={idx} className={`p-4 rounded-lg border-2 ${getPriorityColor(action.priority)}`}>
            <div className="flex items-start gap-4">
              <div className="mt-1">{getActionIcon(action.type)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h3 className="font-semibold text-slate-900 capitalize">
                      {idx + 1}. {action.type.replace(/_/g, ' ')}
                    </h3>
                    <p className="text-sm text-slate-600 mt-1">{action.description}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
                      action.priority === 'high'
                        ? 'bg-red-100 text-red-700'
                        : action.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-blue-100 text-blue-700'
                    }`}>
                      {action.priority === 'high' ? '🔴' : action.priority === 'medium' ? '🟡' : '🔵'} {action.priority}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 mt-3 text-sm">
                  <div>
                    <p className="text-xs text-slate-600">Impact</p>
                    <p className="text-lg font-bold text-green-600">+{action.estimated_gain}</p>
                  </div>
                  {action.paydown_amount && (
                    <div>
                      <p className="text-xs text-slate-600">To Pay</p>
                      <p className="text-lg font-bold text-blue-600">  ${action.paydown_amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                      </p>
                    </div>
                  )}
                  {action.current_balance !== undefined && (
                    <div>
                      <p className="text-xs text-slate-600">Current</p>
                      <p className="text-lg font-bold text-slate-700">${action.current_balance.toLocaleString('en-US', { maximumFractionDigits: 0 })}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <p className="text-sm text-slate-700">
          <strong>Strategy:</strong> Start with high-priority actions first. Most people see significant gains by reducing
          credit utilization below 30%. Follow this plan for best results.
        </p>
      </div>
    </div>
  );
}
