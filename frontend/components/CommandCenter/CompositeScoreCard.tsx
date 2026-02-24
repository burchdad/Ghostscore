'use client';

interface CompositeScoreCardProps {
  scores?: { [key: string]: number } | null;
  composite?: { [key: string]: number } | null;
  stabilityIndex?: { stability_index: number; risk_level: string } | null;
}

export default function CompositeScoreCard({ scores, composite, stabilityIndex }: CompositeScoreCardProps) {
  const ficoScores = scores || {};
  const compositeScore = composite?.composite || ficoScores.composite || 0;
  const fico8 = ficoScores.fico8 || 0;
  const fico9 = ficoScores.fico9 || 0;
  const fico10 = ficoScores.fico10 || 0;
  const stability = stabilityIndex?.stability_index || 0;

  const getScoreColor = (score: number) => {
    if (score >= 750) return 'text-green-600';
    if (score >= 700) return 'text-blue-600';
    if (score >= 650) return 'text-amber-600';
    return 'text-red-600';
  };

  const getConfidenceLevel = (stability: number) => {
    if (stability >= 80) return 'HIGH';
    if (stability >= 60) return 'MEDIUM';
    return 'LOW';
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {/* Composite Score */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-purple-500">
        <p className="text-xs font-semibold text-slate-600 uppercase mb-2">Composite Score</p>
        <p className={`text-3xl font-bold ${getScoreColor(compositeScore)}`}>{Math.round(compositeScore)}</p>
        <p className="text-xs text-slate-500 mt-1">Your Overall</p>
      </div>

      {/* FICO 8 */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
        <p className="text-xs font-semibold text-slate-600 uppercase mb-2">FICO 8</p>
        <p className={`text-3xl font-bold ${getScoreColor(fico8)}`}>{Math.round(fico8)}</p>
        <p className="text-xs text-slate-500 mt-1">Classic</p>
      </div>

      {/* FICO 9 */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-green-500">
        <p className="text-xs font-semibold text-slate-600 uppercase mb-2">FICO 9</p>
        <p className={`text-3xl font-bold ${getScoreColor(fico9)}`}>{Math.round(fico9)}</p>
        <p className="text-xs text-slate-500 mt-1">Latest</p>
      </div>

      {/* FICO 10 */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-indigo-500">
        <p className="text-xs font-semibold text-slate-600 uppercase mb-2">FICO 10</p>
        <p className={`text-3xl font-bold ${getScoreColor(fico10)}`}>{Math.round(fico10)}</p>
        <p className="text-xs text-slate-500 mt-1">New</p>
      </div>

      {/* Stability Index */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-orange-500">
        <p className="text-xs font-semibold text-slate-600 uppercase mb-2">Stability</p>
        <p className="text-3xl font-bold text-orange-600">{Math.round(stability)}</p>
        <p className="text-xs text-slate-500 mt-1">/ 100</p>
      </div>

      {/* Confidence Level */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-cyan-500">
        <p className="text-xs font-semibold text-slate-600 uppercase mb-2">Confidence</p>
        <p className="text-2xl font-bold text-cyan-600">{getConfidenceLevel(stability)}</p>
        <p className="text-xs text-slate-500 mt-1">Risk Level</p>
      </div>
    </div>
  );
}
