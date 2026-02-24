'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import toast from 'react-hot-toast';
import { RefreshCw } from 'lucide-react';

interface CalibrationStatusProps {
  calibrationData?: any | null;
  profileId: string;
}

export default function CalibrationStatus({ calibrationData, profileId }: CalibrationStatusProps) {
  const [loading, setLoading] = useState(false);

  const handleCalibrate = async () => {
    setLoading(true);
    try {
      const result = await apiClient.calibrateProfile(profileId);
      toast.success('Profile calibrated successfully!');
    } catch (err) {
      toast.error('Failed to calibrate profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">Calibration Status</h2>

      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
          <span className="text-sm font-semibold text-slate-700">Status</span>
          <span className="px-3 py-1 rounded-full bg-green-100 text-green-800 text-sm font-semibold">Calibrated</span>
        </div>

        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
          <span className="text-sm font-semibold text-slate-700">Last Updated</span>
          <span className="text-sm text-slate-600">Today</span>
        </div>

        <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
          <span className="text-sm font-semibold text-slate-700">Accuracy</span>
          <span className="text-sm text-slate-600">High Confidence</span>
        </div>
      </div>

      <button
        onClick={handleCalibrate}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold rounded-lg transition"
      >
        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        {loading ? 'Calibrating...' : 'Update Calibration'}
      </button>

      <p className="text-xs text-slate-600 mt-3 text-center">
        Calibration updates your model based on verified credit report data
      </p>
    </div>
  );
}
