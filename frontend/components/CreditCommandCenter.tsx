'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/lib/store';
import { apiClient } from '@/lib/api';
import toast from 'react-hot-toast';

import CompositeScoreCard from './CommandCenter/CompositeScoreCard';
import GoalTracker from './CommandCenter/GoalTracker';
import StabilityIndexCard from './CommandCenter/StabilityIndexCard';
import ModelComparison from './CommandCenter/ModelComparison';
import UtilizationHeatmap from './CommandCenter/UtilizationHeatmap';
import CalibrationStatus from './CommandCenter/CalibrationStatus';
import ProfileSummary from './CommandCenter/ProfileSummary';
import OptimizerActions from './CommandCenter/OptimizerActions';

interface CommandCenterData {
  compositeScores: { [key: string]: number } | null;
  stabilityIndex: { stability_index: number; risk_level: string } | null;
  optimizeData: any | null;
  forecastData: { forecast: number[]; weeks: number } | null;
  calibrationStatus: any | null;
  allScores: { [key: string]: number } | null;
}

export default function CreditCommandCenter() {
  const { profile, score, currentProfileId } = useStore();
  const [data, setData] = useState<CommandCenterData>({
    compositeScores: null,
    stabilityIndex: null,
    optimizeData: null,
    forecastData: null,
    calibrationStatus: null,
    allScores: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile || profile.accounts.length === 0 || !currentProfileId) {
      setLoading(false);
      return;
    }

    const fetchCommandCenterData = async () => {
      try {
        setLoading(true);

        // Fetch in parallel
        const [composite, stability, optimize, forecast, allScores] = await Promise.allSettled([
          apiClient.scoreComposite(profile),
          apiClient.getScoreStability(profile),
          apiClient.optimizeProfile(profile),
          apiClient.forecastScore(profile, 16),
          apiClient.scoreAllModels(profile),
        ]);

        setData({
          compositeScores: composite.status === 'fulfilled' ? composite.value : null,
          stabilityIndex: stability.status === 'fulfilled' ? stability.value : null,
          optimizeData: optimize.status === 'fulfilled' ? optimize.value : null,
          forecastData: forecast.status === 'fulfilled' ? { forecast: forecast.value, weeks: 16 } : null,
          allScores: allScores.status === 'fulfilled' ? allScores.value : null,
          calibrationStatus: null, // Will be added when calibration endpoint is available
        });
      } catch (err) {
        console.error('Error fetching command center data:', err);
        toast.error('Failed to load command center data');
      } finally {
        setLoading(false);
      }
    };

    fetchCommandCenterData();
  }, [profile, currentProfileId]);

  if (!currentProfileId || profile.accounts.length === 0) {
    return (
      <div className="w-full p-12 text-center bg-slate-50 rounded-lg border border-slate-200">
        <p className="text-slate-600 text-lg">
          Add accounts and upload a credit report to see your Credit Command Center
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ROW 1: Score Cards */}
      {(data.allScores || data.compositeScores || data.stabilityIndex) && (
        <CompositeScoreCard
          scores={data.allScores}
          composite={data.compositeScores}
          stabilityIndex={data.stabilityIndex}
        />
      )}

      {/* ROW 2: Goal Tracker & Calibration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {(data.optimizeData || data.forecastData || score) && (
          <GoalTracker
            currentScore={score?.score}
            optimizeData={data.optimizeData}
            forecastData={data.forecastData}
          />
        )}
        {data.calibrationStatus && (
          <CalibrationStatus calibrationData={data.calibrationStatus} profileId={currentProfileId} />
        )}
      </div>

      {/* ROW 3: Score Trajectory */}
      {data.forecastData && Array.isArray(data.forecastData.forecast) && data.forecastData.forecast.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Score Trajectory</h2>
          <div className="flex items-end justify-between gap-2">
            {data.forecastData.forecast.slice(0, 17).map((scoreVal, idx) => (
              <div key={idx} className="flex-1 text-center">
                <div
                  className="bg-gradient-to-t from-blue-500 to-blue-400 rounded-t mx-auto mb-2"
                  style={{
                    height: `${(scoreVal / 850) * 200}px`,
                    minHeight: '20px',
                    maxWidth: '100%',
                  }}
                />
                <p className="text-xs font-semibold text-slate-700">{Math.round(scoreVal)}</p>
                <p className="text-xs text-slate-500">W{idx}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ROW 4: Recommended Actions */}
      {data.optimizeData && data.optimizeData.recommended_actions && (
        <OptimizerActions actions={data.optimizeData.recommended_actions} currentScore={score?.score} />
      )}

      {/* ROW 5: Utilization & Model Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {profile.accounts && profile.accounts.length > 0 && (
          <UtilizationHeatmap accounts={profile.accounts} />
        )}
        {data.allScores && Object.keys(data.allScores).length > 0 && (
          <ModelComparison scores={data.allScores} composite={data.compositeScores} />
        )}
      </div>

      {/* ROW 6: Stability Index */}
      {data.stabilityIndex && <StabilityIndexCard stabilityIndex={data.stabilityIndex} />}

      {/* ROW 7: Profile Summary */}
      <ProfileSummary profile={profile} />
    </div>
  );
}
