'use client'

import { useState } from 'react'
import { CreditProfile, Account } from '@/lib/api'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface AccountsManagerProps {
  profile: CreditProfile | null
  onAccountsDeleted?: () => void
}

export default function AccountsManager({ profile, onAccountsDeleted }: AccountsManagerProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deletingAccountId, setDeletingAccountId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  if (!profile) {
    return null
  }

  const accounts = profile.accounts || []

  const handleDeleteAccount = async (accountId: string) => {
    try {
      setIsDeleting(true)
      setDeletingAccountId(accountId)
      
      await apiClient.deleteAccount(profile.id, accountId)
      
      toast.success('Account deleted')
      onAccountsDeleted?.()
    } catch (err) {
      toast.error('Failed to delete account')
      console.error(err)
    } finally {
      setIsDeleting(false)
      setDeletingAccountId(null)
    }
  }

  const handleDeleteAllAccounts = async () => {
    try {
      setIsDeleting(true)
      
      const result = await apiClient.deleteAllAccounts(profile.id)
      
      toast.success(`Deleted ${result.deleted} accounts`)
      setShowDeleteConfirm(false)
      onAccountsDeleted?.()
    } catch (err) {
      toast.error('Failed to delete accounts')
      console.error(err)
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-white">Accounts ({accounts.length})</h3>
        {accounts.length > 0 && (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm font-semibold transition"
          >
            🗑️ Clear All
          </button>
        )}
      </div>

      {accounts.length === 0 ? (
        <p className="text-slate-300">No accounts yet</p>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {accounts.map((account) => (
            <div key={account.id} className="bg-slate-600 rounded p-3 flex justify-between items-start">
              <div className="flex-1">
                <p className="font-semibold text-white">{account.name}</p>
                <p className="text-sm text-slate-300">
                  {account.type} • Balance: ${account.balance?.toLocaleString() || '0'}
                  {account.limit && ` / $${account.limit.toLocaleString()}`}
                </p>
                <p className="text-xs text-slate-400">{account.status}</p>
              </div>
              <button
                onClick={() => handleDeleteAccount(account.id)}
                disabled={isDeleting && deletingAccountId === account.id}
                className="ml-3 px-2 py-1 bg-red-600 hover:bg-red-700 disabled:bg-slate-500 text-white rounded text-xs font-semibold transition whitespace-nowrap"
              >
                {isDeleting && deletingAccountId === account.id ? '...' : '✕'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Delete All Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-slate-700 rounded-lg shadow-lg p-6 w-full max-w-sm mx-4">
            <h3 className="text-lg font-bold text-white mb-4">Clear All Accounts?</h3>
            <p className="text-slate-300 mb-6">
              This will delete all <strong>{accounts.length}</strong> accounts from this profile. This cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded font-semibold transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAllAccounts}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-slate-400 text-white rounded font-semibold transition"
              >
                {isDeleting ? 'Deleting...' : 'Delete All'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
