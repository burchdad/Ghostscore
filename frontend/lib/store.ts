import { create } from 'zustand'

interface Account {
  id: string
  type: string
  name: string
  balance: number
  limit?: number
  open_date: string
  status: string
}

interface Derogatory {
  id: string
  type: string
  date: string
  details?: string
}

interface CreditProfile {
  id?: string
  user_id?: string
  accounts: Account[]
  derogatories: Derogatory[]
}

interface ProfileSummary {
  id: string
  name: string
}

interface Score {
  score: number
  payment_history: number
  utilization: number
  age: number
  new_credit: number
  mix: number
}

interface StoreState {
  // User/Profile Management
  userEmail: string | null
  availableProfiles: ProfileSummary[]
  currentProfileId: string | null
  
  // Current profile data
  profile: CreditProfile
  score: Score | null
  loading: boolean
  error: string | null

  // Actions
  setUserEmail: (email: string) => void
  setAvailableProfiles: (profiles: ProfileSummary[]) => void
  setCurrentProfileId: (profileId: string) => void
  addProfile: (profile: ProfileSummary) => void
  
  addAccount: (account: Account) => void
  removeAccount: (accountId: string) => void
  updateAccount: (accountId: string, account: Account) => void
  
  addDerogatory: (derogatory: Derogatory) => void
  removeDerogatory: (derogId: string) => void
  
  setProfile: (profile: CreditProfile) => void
  setScore: (score: Score) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useStore = create<StoreState>((set) => ({
  // Initial state
  userEmail: null,
  availableProfiles: [],
  currentProfileId: null,
  profile: {
    accounts: [],
    derogatories: [],
  },
  score: null,
  loading: false,
  error: null,

  // User/Profile management
  setUserEmail: (email: string) => set({ userEmail: email }),
  
  setAvailableProfiles: (profiles: ProfileSummary[]) =>
    set({ availableProfiles: profiles }),
  
  setCurrentProfileId: (profileId: string) =>
    set({ currentProfileId: profileId }),
  
  addProfile: (profile: ProfileSummary) =>
    set((state: StoreState) => ({
      availableProfiles: [...state.availableProfiles, profile],
    })),

  // Account management
  addAccount: (account: Account) =>
    set((state: StoreState) => ({
      profile: {
        ...state.profile,
        accounts: [...state.profile.accounts, account],
      },
    })),

  removeAccount: (accountId: string) =>
    set((state: StoreState) => ({
      profile: {
        ...state.profile,
        accounts: state.profile.accounts.filter((acc: Account) => acc.id !== accountId),
      },
    })),

  updateAccount: (accountId: string, account: Account) =>
    set((state: StoreState) => ({
      profile: {
        ...state.profile,
        accounts: state.profile.accounts.map((acc: Account) =>
          acc.id === accountId ? account : acc
        ),
      },
    })),

  // Derogatory management
  addDerogatory: (derogatory: Derogatory) =>
    set((state: StoreState) => ({
      profile: {
        ...state.profile,
        derogatories: [...state.profile.derogatories, derogatory],
      },
    })),

  removeDerogatory: (derogId: string) =>
    set((state: StoreState) => ({
      profile: {
        ...state.profile,
        derogatories: state.profile.derogatories.filter((d: Derogatory) => d.id !== derogId),
      },
    })),

  // Profile/Score management
  setProfile: (profile: CreditProfile) => set({ profile }),
  setScore: (score: Score) => set({ score }),
  setLoading: (loading: boolean) => set({ loading }),
  setError: (error: string | null) => set({ error }),
}))
