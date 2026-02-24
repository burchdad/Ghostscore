
// Use Next.js API proxy for all requests (routes through /api)
const API_BASE_URL = '/api'

export interface Account {
  id: string
  type: string
  name: string
  balance: number
  limit?: number
  open_date: string
  status: string
}

export interface Derogatory {
  id: string
  type: string
  date: string
  details?: string
}

export interface CreditProfile {
  id?: string
  user_id?: string
  accounts: Account[]
  derogatories: Derogatory[]
}

export interface ScoreResponse {
  score: number
  payment_history: number
  utilization: number
  age: number
  new_credit: number
  mix: number
}

export interface ProfileSummary {
  id: string
  name: string
}

export interface ScoreHistoryEntry {
  id: string
  profile_id: string
  score: number
  payment_history?: number
  utilization?: number
  age?: number
  new_credit?: number
  mix?: number
  created_at: string
}

export interface ScenarioHistoryEntry {
  id: string
  profile_id: string
  actions: any[]
  original_score: number
  simulated_score: number
  actual_gain?: number
  timeline?: any[]
  notes?: string
  tags?: string[]
  pinned?: boolean
  feedback?: string
  created_at: string
}

export const apiClient = {
    async downloadActionPlanPdf(profileId: string): Promise<Blob> {
      const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/action_plan/pdf`)
      if (!response.ok) throw new Error('Failed to download action plan PDF')
      return response.blob()
    },
    async downloadProfilePdf(profileId: string): Promise<Blob> {
      const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/export/pdf`)
      if (!response.ok) throw new Error('Failed to download PDF')
      return response.blob()
    },
  // Profile endpoints
  async createProfile(email: string, profileName: string = 'My Profile'): Promise<ProfileSummary> {
    const response = await fetch(`${API_BASE_URL}/profiles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, profile_name: profileName }),
    })
    if (!response.ok) throw new Error('Failed to create profile')
    return response.json()
  },

  async getProfiles(email: string): Promise<ProfileSummary[]> {
    const url = `${API_BASE_URL}/profiles/${encodeURIComponent(email)}`
    console.log('Fetching profiles from:', url)
    try {
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      })
      console.log('Response status:', response.status, response.statusText)
      console.log('Response headers:', response.headers)
      if (!response.ok) {
        const text = await response.text()
        console.error('Error response body:', text)
        throw new Error(`Failed to get profiles: ${response.status} ${response.statusText}`)
      }
      const data = await response.json()
      console.log('Profiles loaded:', data)
      return data
    } catch (err) {
      console.error('getProfiles error:', err)
      throw err
    }
  },

  async getFullProfile(profileId: string): Promise<CreditProfile> {
    const url = `${API_BASE_URL}/profiles/${profileId}/full`
    console.log('Fetching full profile from:', url)
    try {
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      })
      console.log('Full profile response status:', response.status)
      if (!response.ok) {
        const text = await response.text()
        console.error('Error response body:', text)
        throw new Error(`Failed to get profile: ${response.status} ${response.statusText}`)
      }
      const data = await response.json()
      console.log('Full profile loaded:', data)
      return data
    } catch (err) {
      console.error('getFullProfile error:', err)
      throw err
    }
  },

  // Account endpoints
  async addAccount(profileId: string, account: Account): Promise<{ id: string; name: string }> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/accounts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(account),
    })
    if (!response.ok) throw new Error('Failed to add account')
    return response.json()
  },

  async deleteAccount(profileId: string, accountId: string): Promise<{ deleted: boolean }> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/accounts/${accountId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!response.ok) throw new Error('Failed to delete account')
    return response.json()
  },

  async deleteAllAccounts(profileId: string): Promise<{ deleted: number; message: string }> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/accounts-all`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!response.ok) throw new Error('Failed to delete all accounts')
    return response.json()
  },

  async addDerogatory(profileId: string, derog: Derogatory): Promise<{ id: string; type: string }> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/derogatories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(derog),
    })
    if (!response.ok) throw new Error('Failed to add derogatory')
    return response.json()
  },

  // Scoring endpoints
  async calculateScore(profile: CreditProfile): Promise<ScoreResponse> {
    const response = await fetch(`${API_BASE_URL}/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!response.ok) throw new Error('Failed to calculate score')
    return response.json()
  },

  async simulatePaydown(
    profile: CreditProfile,
    accountId: string,
    newBalance: number
  ) {
    const response = await fetch(`${API_BASE_URL}/simulate/paydown`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, account_id: accountId, new_balance: newBalance }),
    })
    if (!response.ok) throw new Error('Failed to simulate paydown')
    return response.json()
  },

  async getRecommendations(profile: CreditProfile) {
    const response = await fetch(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!response.ok) throw new Error('Failed to get recommendations')
    return response.json()
  },

  async getScoreHistory(profileId: string): Promise<Array<{ date: string; score: number }>> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/score-history`)
    if (!response.ok) throw new Error('Failed to get score history')
    return response.json()
  },

  async getScoreHistoryFull(profileId: string, limit = 100): Promise<ScoreHistoryEntry[]> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/score_history?limit=${limit}`)
    if (!response.ok) throw new Error('Failed to get score history')
    return response.json()
  },

  async saveScoreSnapshot(profileId: string, data: Partial<ScoreHistoryEntry>): Promise<ScoreHistoryEntry> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/score_history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to save score snapshot')
    return response.json()
  },

  async uploadCreditReport(profileId: string, bureau: string, file: File): Promise<any> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('bureau', bureau)
      
      const url = `${API_BASE_URL}/profiles/${profileId}/upload-credit-report`
      console.log('Uploading credit report to:', url, {bureau, fileName: file.name, fileSize: file.size})
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Let the browser set Content-Type header automatically for FormData
      })
      
      console.log('Upload response status:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Upload error response:', errorText)
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`)
      }
      
      const result = await response.json()
      console.log('Upload successful:', result)
      return result
    } catch (err) {
      console.error('uploadCreditReport error:', err)
      throw err
    }
  },

  async importAccountsFromReport(profileId: string, accounts: any[], selectedIndices?: number[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/import-accounts-from-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accounts, selected_indices: selectedIndices }),
    })
    if (!response.ok) throw new Error('Failed to import accounts')
    return response.json()
  },

  async health() {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) throw new Error('API unavailable')
    return response.json()
  },

  async getScenarioHistory(profileId: string, limit = 100): Promise<ScenarioHistoryEntry[]> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/scenario_history?limit=${limit}`)
    if (!response.ok) throw new Error('Failed to get scenario history')
    return response.json()
  },

  async saveScenarioHistory(profileId: string, data: Partial<ScenarioHistoryEntry>): Promise<ScenarioHistoryEntry> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/scenario_history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to save scenario history')
    return response.json()
  },

  // Calibration endpoint
  async calibrateProfile(profileId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/calibrate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!response.ok) throw new Error('Failed to calibrate profile')
    return response.json()
  },

  // Composite score endpoint
  async scoreComposite(profile: CreditProfile): Promise<{ composite: number }> {
    const response = await fetch(`${API_BASE_URL}/score/composite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!response.ok) throw new Error('Failed to get composite score')
    return response.json()
  },

  // All models scores
  async scoreAllModels(profile: CreditProfile): Promise<{ fico8: number; fico9: number; fico10: number }> {
    const response = await fetch(`${API_BASE_URL}/score/all`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!response.ok) throw new Error('Failed to get all model scores')
    return response.json()
  },

  // Stability index
  async getScoreStability(profile: CreditProfile): Promise<{ stability_index: number; risk_level: string }> {
    const response = await fetch(`${API_BASE_URL}/score/stability`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!response.ok) throw new Error('Failed to get stability index')
    return response.json()
  },

  // Forecast score
  async forecastScore(profile: CreditProfile, weeks: number = 16): Promise<number[]> {
    const response = await fetch(`${API_BASE_URL}/score/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, weeks }),
    })
    if (!response.ok) throw new Error('Failed to forecast score')
    return response.json()
  },

  // Optimize endpoint
  async optimizeProfile(profile: CreditProfile): Promise<{ recommended_actions: any[] }> {
    const response = await fetch(`${API_BASE_URL}/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!response.ok) throw new Error('Failed to optimize profile')
    return response.json()
  },
}
