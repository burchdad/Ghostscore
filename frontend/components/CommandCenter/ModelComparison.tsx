'use client';

interface ModelComparisonProps {
  scores?: { [key: string]: number } | null;
  composite?: { [key: string]: number } | null;
}

export default function ModelComparison({ scores, composite }: ModelComparisonProps) {
  const ficoScores = scores || {};
  const maxScore = Math.max(
    ficoScores.fico8 || 0,
    ficoScores.fico9 || 0,
    ficoScores.fico10 || 0,
    composite?.composite || 0
  );

  const models = [
    { name: 'FICO 8', value: ficoScores.fico8 || 0, color: 'from-blue-500 to-blue-400' },
    { name: 'FICO 9', value: ficoScores.fico9 || 0, color: 'from-green-500 to-green-400' },
    { name: 'FICO 10', value: ficoScores.fico10 || 0, color: 'from-indigo-500 to-indigo-400' },
    { name: 'Composite', value: composite?.composite || 0, color: 'from-purple-500 to-purple-400' },
  ];

  const getScoreRange = (score: number) => {
    if (score >= 750) return 'Excellent';
    if (score >= 700) return 'Very Good';
    if (score >= 650) return 'Good';
    if (score >= 600) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Model Comparison</h2>

      <div className="space-y-4">
        {models.map((model) => (
          <div key={model.name}>
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-slate-800">{model.name}</span>
              <div className="text-right">
                <span className="text-2xl font-bold text-slate-900">{Math.round(model.value)}</span>
                <span className="text-xs text-slate-500 ml-2">{getScoreRange(model.value)}</span>
              </div>
            </div>
            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${model.color} transition-all duration-300`}
                style={{ width: `${(model.value / 850) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">Different models, different perspectives:</span> FICO 8 is most common for auto/personal
          loans. FICO 10 is newer and focuses on recent payment patterns. Compare all for best insights.
        </p>
      </div>
    </div>
  );
}
