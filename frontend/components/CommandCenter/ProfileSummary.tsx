'use client';

import { CreditProfile } from '@/lib/api';
import { BarChart3, TrendingUp } from 'lucide-react';

interface ProfileSummaryProps {
  profile: CreditProfile;
}

export default function ProfileSummary({ profile }: ProfileSummaryProps) {
  const totalAccounts = profile.accounts?.length || 0;
  const derogatories = profile.derogatories?.length || 0;
  const avgAge = profile.accounts?.length
    ? profile.accounts.reduce((sum, acc) => {
        const openDate = new Date(acc.open_date);
        const ageYears = (Date.now() - openDate.getTime()) / (1000 * 60 * 60 * 24 * 365);
        return sum + ageYears;
      }, 0) / profile.accounts.length
    : 0;

  const totalBalance = profile.accounts?.reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0;
  const totalLimit = profile.accounts?.reduce((sum, acc) => (acc.limit ? sum + acc.limit : sum), 0) || 0;
  const utilization = totalLimit > 0 ? (totalBalance / totalLimit) * 100 : 0;

  const stats = [
    { label: 'Total Accounts', value: totalAccounts, icon: '📊' },
    { label: 'Average Age', value: `${avgAge.toFixed(1)}y`, icon: '📅' },
    { label: 'Utilization', value: `${utilization.toFixed(1)}%`, icon: '📈' },
    { label: 'Derogatories', value: derogatories, icon: '⚠️' },
  ];

  return (
    <div className="bg-gradient-to-r from-slate-700 to-slate-800 rounded-lg shadow-md p-6 border border-slate-600 text-white">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 size={24} />
        <h2 className="text-2xl font-bold">Credit Profile Summary</h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-slate-600/50 rounded-lg p-4 border border-slate-500">
            <p className="text-3xl mb-1">{stat.icon}</p>
            <p className="text-sm text-gray-300 mb-1">{stat.label}</p>
            <p className="text-2xl font-bold text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-slate-600/30 rounded border border-slate-500 text-sm text-gray-200">
        <p>
          {derogatories === 0
            ? '✓ Clean credit profile with no negative marks.'
            : `⚠ ${derogatories} negative item(s) on record. Focus on positive payment history.`}
        </p>
      </div>
    </div>
  );
}
