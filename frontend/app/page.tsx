'use client'

import { useEffect, useState } from 'react'
import Dashboard from '@/components/Dashboard'
import AddAccountForm from '@/components/AddAccountForm'
import ProfileSelector from '@/components/ProfileSelector'
import CreditReportUpload from '@/components/CreditReportUpload'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import toast, { Toaster } from 'react-hot-toast'

export default function Home() {
  const { profile, userEmail, setUserEmail, setAvailableProfiles, currentProfileId, setProfile, setLoading } = useStore()
  const [showAddForm, setShowAddForm] = useState(false)
  const [showUploadReport, setShowUploadReport] = useState(false)
  const [familyEmail, setFamilyEmail] = useState('family@ghostscore.local')
  const [initialized, setInitialized] = useState(false)

  // Load profiles on startup
  useEffect(() => {
    if (!initialized) {
      loadProfiles()
    }
  }, [initialized])

  // Load full profile when currentProfileId changes
  useEffect(() => {
    if (currentProfileId && initialized) {
      loadFullProfile(currentProfileId)
    }
  }, [currentProfileId, initialized])

  const loadProfiles = async () => {
    try {
      setLoading(true)
      const profiles = await apiClient.getProfiles(familyEmail)
      setUserEmail(familyEmail)
      setAvailableProfiles(profiles)
      
      if (profiles.length > 0) {
        useStore.setState({ currentProfileId: profiles[0].id })
      }
      
      setInitialized(true)
      toast.success(`Loaded ${profiles.length} profiles`)
    } catch (err) {
      toast.error('Failed to load profiles')
      setInitialized(true)
    }
  }

  const loadFullProfile = async (profileId: string) => {
    try {
      setLoading(true)
      const fullProfile = await apiClient.getFullProfile(profileId)
      setProfile(fullProfile)
    } catch (err) {
      toast.error('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleInitialize = async () => {
    if (!familyEmail.trim()) {
      toast.error('Email required')
      return
    }
    setInitialized(false)
  }

  if (!initialized) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        <Toaster position="top-right" />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <header className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">GhostScore</h1>
            <p className="text-slate-300">AI-powered FICO Simulator & Optimizer</p>
          </header>

          <div className="max-w-md mx-auto mt-20">
            <div className="bg-slate-700 rounded-lg p-8">
              <h2 className="text-2xl font-bold text-white mb-6">Welcome to the Family</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Family Email
                  </label>
                  <input
                    type="email"
                    value={familyEmail}
                    onChange={(e) => setFamilyEmail(e.target.value)}
                    placeholder="family@ghostscore.local"
                    className="w-full px-4 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
                  />
                  <p className="text-xs text-slate-400 mt-2">
                    This email groups all family credit profiles together
                  </p>
                </div>
                <button
                  onClick={handleInitialize}
                  className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold transition"
                >
                  Load Profiles
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <Toaster position="top-right" />
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">GhostScore</h1>
              <p className="text-slate-300">AI-powered FICO Simulator & Optimizer</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowUploadReport(!showUploadReport)}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition"
              >
                {showUploadReport ? 'Close' : '📄 Upload Report'}
              </button>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
              >
                {showAddForm ? 'Close' : '+ Add Account'}
              </button>
            </div>
          </div>

          {/* Profile Selector */}
          <ProfileSelector />
        </header>

        {/* Upload Report Form */}
        {showUploadReport && (
          <div className="mb-8">
            <CreditReportUpload onClose={() => setShowUploadReport(false)} />
          </div>
        )}

        {/* Add Account Form */}
        {showAddForm && (
          <div className="mb-8">
            <AddAccountForm onClose={() => setShowAddForm(false)} />
          </div>
        )}

        {/* Dashboard */}
        {profile.accounts.length > 0 ? (
          <Dashboard />
        ) : (
          <div className="text-center py-20">
            <p className="text-xl text-slate-400 mb-8">
              Start by adding credit accounts to this profile
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setShowUploadReport(true)}
                className="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition"
              >
                📄 Upload Credit Report
              </button>
              <button
                onClick={() => setShowAddForm(true)}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
              >
                ➕ Add Manually
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
