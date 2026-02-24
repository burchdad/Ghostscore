'use client'

import { useEffect, useState } from 'react'
import Dashboard from '@/components/Dashboard'
import AddAccountForm from '@/components/AddAccountForm'
import ProfileSelector from '@/components/ProfileSelector'
import CreditReportUpload from '@/components/CreditReportUpload'
import PlaidAccountLink from '@/components/PlaidAccountLink'
import AccountsManager from '@/components/AccountsManager'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import toast, { Toaster } from 'react-hot-toast'

export default function Home() {
  const { profile, userEmail, setUserEmail, setAvailableProfiles, currentProfileId, setProfile, setLoading } = useStore()
  const [showAddForm, setShowAddForm] = useState(false)
  const [showUploadReport, setShowUploadReport] = useState(false)
  const [showPlaidLink, setShowPlaidLink] = useState(false)
  const [addAccountMethod, setAddAccountMethod] = useState<'bank' | 'manual' | null>(null)
  const [showAccountMethodMenu, setShowAccountMethodMenu] = useState(false)
  const [familyEmail, setFamilyEmail] = useState('family@ghostscore.local')
  const [initialized, setInitialized] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string>('init')
  const [loadAttempted, setLoadAttempted] = useState(false)
  
  useEffect(() => {
    setDebugInfo('effect1: mount')
    if (!loadAttempted) {
      setDebugInfo('effect1: starting load')
      setLoadAttempted(true)
      // Start the load
      console.log('Starting initial load...')
      loadProfiles()
    }
  }, [])

  // Load full profile when currentProfileId changes
  useEffect(() => {
    if (currentProfileId && initialized) {
      loadFullProfile(currentProfileId)
    }
  }, [currentProfileId, initialized])

  const loadProfiles = async () => {
    try {
      console.log('loadProfiles called with familyEmail:', familyEmail)
      setDebugInfo('loading...')
      setLoading(true)
      console.log('About to fetch from:', `${process.env.NEXT_PUBLIC_API_URL}/profiles/${encodeURIComponent(familyEmail)}`)
      const profiles = await apiClient.getProfiles(familyEmail)
      console.log('loadProfiles succeeded, profiles count:', profiles.length, 'profiles:', profiles)
      setDebugInfo('loaded: ' + profiles.length + ' profiles')
      setUserEmail(familyEmail)
      setAvailableProfiles(profiles)
      
      if (profiles.length > 0) {
        console.log('Setting currentProfileId to', profiles[0].id)
        useStore.setState({ currentProfileId: profiles[0].id })
      }
      
      console.log('About to call setInitialized(true)')
      setInitialized(true)
      console.log('Called setInitialized(true)')
      setDebugInfo('initialized!')
      setLoading(false)
      toast.success(`Loaded ${profiles.length} profiles`)
    } catch (err) {
      console.error('loadProfiles error:', err)
      setDebugInfo('error: ' + (err instanceof Error ? err.message : 'unknown'))
      toast.error('Failed to load profiles')
      setInitialized(true)
      setLoading(false)
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
    await loadProfiles()
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
              <div className="text-xs text-slate-400 mb-4 p-2 bg-slate-600 rounded">Debug: {debugInfo}</div>
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
              <div className="relative">
                <button
                  onClick={() => setShowAccountMethodMenu(!showAccountMethodMenu)}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
                >
                  {showAccountMethodMenu ? '✕ Close' : '+ Add Account'}
                </button>
                {showAccountMethodMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-slate-700 border border-slate-600 rounded-lg shadow-xl z-50">
                    <button
                      onClick={() => {
                        setShowPlaidLink(true)
                        setShowAccountMethodMenu(false)
                      }}
                      className="block w-full text-left px-4 py-3 text-white hover:bg-slate-600 rounded-t-lg transition"
                    >
                      🏦 Link Bank Account
                    </button>
                    <button
                      onClick={() => {
                        setShowAddForm(true)
                        setShowAccountMethodMenu(false)
                      }}
                      className="block w-full text-left px-4 py-3 text-white hover:bg-slate-600 rounded-b-lg transition border-t border-slate-600"
                    >
                      ✏️ Add Manually
                    </button>
                  </div>
                )}
              </div>
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

        {/* Plaid Account Link */}
        {showPlaidLink && (
          <div className="mb-8">
            <PlaidAccountLink onClose={() => {
              setShowPlaidLink(false)
              setShowAccountMethodMenu(false)
            }} />
          </div>
        )}

        {/* Add Account Form */}
        {showAddForm && (
          <div className="mb-8">
            <AddAccountForm onClose={() => {
              setShowAddForm(false)
              setShowAccountMethodMenu(false)
            }} />
          </div>
        )}

        {/* Dashboard */}
        {profile.accounts.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-3">
              <Dashboard />
            </div>
            <div className="lg:col-span-1">
              <AccountsManager profile={profile} onAccountsDeleted={() => loadFullProfile(profile.id)} />
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-xl text-slate-400 mb-8">
              Start by adding credit accounts to this profile
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <button
                onClick={() => setShowUploadReport(true)}
                className="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition"
              >
                📄 Upload Credit Report
              </button>
              <button
                onClick={() => {
                  setAddAccountMethod('bank')
                  setShowPlaidLink(true)
                }}
                className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition"
              >
                🏦 Link Bank Account
              </button>
              <button
                onClick={() => {
                  setAddAccountMethod('manual')
                  setShowAddForm(true)
                }}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
              >
                ✏️ Add Manually
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
