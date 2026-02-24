'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

export default function ProfileSelector() {
  const { userEmail, availableProfiles, currentProfileId, setCurrentProfileId } = useStore()
  const [isCreating, setIsCreating] = useState(false)
  const [newProfileName, setNewProfileName] = useState('')

  const handleCreateProfile = async () => {
    if (!userEmail || !newProfileName.trim()) {
      toast.error('Profile name required')
      return
    }

    try {
      setIsCreating(true)
      const profile = await apiClient.createProfile(userEmail, newProfileName)
      useStore.setState((state) => ({
        availableProfiles: [...state.availableProfiles, profile],
        currentProfileId: profile.id, // Auto-select newly created profile
      }))
      setNewProfileName('')
      toast.success('Profile created!')
    } catch (err) {
      toast.error('Failed to create profile')
    } finally {
      setIsCreating(false)
    }
  }

  const currentProfile = availableProfiles.find((p) => p.id === currentProfileId)

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-400">👨‍👩‍👧‍👦 Profile:</span>
        <select
          value={currentProfileId || ''}
          onChange={(e) => setCurrentProfileId(e.target.value)}
          className="px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select a profile...</option>
          {availableProfiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="New profile name..."
          value={newProfileName}
          onChange={(e) => setNewProfileName(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleCreateProfile()}
          className="px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 placeholder-slate-400 focus:border-blue-400 focus:outline-none"
        />
        <button
          onClick={handleCreateProfile}
          disabled={isCreating || !newProfileName.trim()}
          className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded font-semibold transition"
        >
          {isCreating ? 'Creating...' : 'New'}
        </button>
      </div>
    </div>
  )
}
