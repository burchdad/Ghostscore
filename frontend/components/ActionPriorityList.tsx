'use client';

/**
 * ActionPriorityList
 * Displays ranked credit improvement recommendations
 * Shows priority, impact, and action details
 */

import { CheckCircle2, AlertCircle, TrendingUp, DollarSign, XCircle } from 'lucide-react';

export interface Action {
  type: 'paydown' | 'payoff' | 'derogatory_removal';
  priority: 'high' | 'medium' | 'low';
  account_name?: string;
  description: string;
  estimated_gain: number;
  current_balance?: number;
  target_balance?: number;
  paydown_amount?: number;
  rank?: number;
}

interface ActionPriorityListProps {
  actions: Action[];
  onSelectAction?: (action: Action) => void;
  selectedIndexes?: number[];
}

export default function ActionPriorityList({
  actions,
  onSelectAction,
  selectedIndexes,
}: ActionPriorityListProps) {
  if (!actions || actions.length === 0) {
    return (
      <div className="w-full p-6 bg-slate-50 rounded-lg border border-slate-200">
        <p className="text-slate-600">No recommendations available</p>
      </div>
    );
  }

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

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-red-100 text-red-700 text-sm font-medium">
            <AlertCircle size={14} />
            High Priority
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-yellow-100 text-yellow-700 text-sm font-medium">
            <TrendingUp size={14} />
            Medium Priority
          </span>
        );
      case 'low':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium">
            <CheckCircle2 size={14} />
            Low Priority
          </span>
        );
      default:
        return null;
    }
  };

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

  return (
    <div className="w-full bg-white rounded-lg border border-slate-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900">
          Recommended Actions
        </h3>
        <p className="text-sm text-slate-600 mt-1">
          Ranked by estimated score impact
        </p>
      </div>

      <div className="space-y-3">
        {actions.map((action, index) => {
          const isSelected = Array.isArray(selectedIndexes) && selectedIndexes.includes(index);
          return (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${getPriorityColor(
                action.priority
              )} ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
              onClick={() => onSelectAction?.(action)}
            >
              <div className="flex items-start gap-4">
                <div className="mt-1">{getActionIcon(action.type)}</div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <h4 className="font-semibold text-slate-900 capitalize">
                        {action.type.replace(/_/g, ' ')}
                      </h4>
                      <p className="text-sm text-slate-600 mt-1">
                        {action.description}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      {getPriorityBadge(action.priority)}
                    </div>
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
                    <div>
                      <p className="text-xs text-slate-600">Estimated Score Gain</p>
                      <p className="text-lg font-bold text-green-600">
                        +{action.estimated_gain}
                      </p>
                    </div>

                    {action.paydown_amount && (
                      <div>
                        <p className="text-xs text-slate-600">Amount to Pay</p>
                        <p className="text-lg font-bold text-blue-600">
                          ${action.paydown_amount.toLocaleString('en-US', {
                            maximumFractionDigits: 0,
                          })}
                        </p>
                      </div>
                    )}

                    {action.current_balance !== undefined && (
                      <div>
                        <p className="text-xs text-slate-600">Current Balance</p>
                        <p className="text-sm text-slate-700">
                          ${action.current_balance.toLocaleString('en-US', {
                            maximumFractionDigits: 0,
                          })}
                        </p>
                      </div>
                    )}

                    {action.target_balance !== undefined && (
                      <div>
                        <p className="text-xs text-slate-600">Target Balance</p>
                        <p className="text-sm text-slate-700">
                          ${action.target_balance.toLocaleString('en-US', {
                            maximumFractionDigits: 0,
                          })}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Rank Badge */}
                {action.rank && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                    <span className="font-bold text-slate-700 text-sm">
                      {action.rank}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <p className="text-sm text-slate-700">
          <strong>Tip:</strong> Start with high-priority actions first for the fastest score improvement.
          Most people see significant gains from reducing credit utilization below 30%.
        </p>
      </div>
    </div>
  );
}
