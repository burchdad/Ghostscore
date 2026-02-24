'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import toast from 'react-hot-toast'

interface PlaidAccountLinkProps {
  onClose: () => void
}

export default function PlaidAccountLink({ onClose }: PlaidAccountLinkProps) {
  const { currentProfileId, addAccount } = useStore()
  const [loading, setLoading] = useState(false)
  const [linkToken, setLinkToken] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Get link token from backend
  const handleGetLinkToken = async () => {
    if (!currentProfileId) {
      toast.error('Please select a profile first')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/plaid/create-link-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_id: currentProfileId,
          user_id: currentProfileId,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create link token')
      }

      const data = await response.json()
      setLinkToken(data.link_token)
      toast.success('Link token created! Copy below to use with Plaid hosted link.')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to initialize Plaid'
      setError(message)
      toast.error(message)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">Link Your Bank Accounts</h3>
      <p className="text-slate-300 mb-6">
        Connect your bank accounts securely to automatically import your credit cards, loans, and other accounts.
        We use Plaid to keep your data safe and encrypted.
      </p>

      <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-200">
          ✓ Secure & encrypted  
          ✓ Read-only access  
          ✓ Works with 11,000+ institutions  
          ✓ Your credentials are never stored
        </p>
      </div>

      {linkToken ? (
        <div className="bg-green-900/30 border border-green-600 rounded-lg p-4 mb-6">
          <p className="text-sm text-green-200 mb-3">
            ✓ Link token generated successfully!
          </p>
          <p className="text-xs text-green-100 mb-4 font-mono break-all bg-slate-800 p-3 rounded">
            {linkToken}
          </p>
          <p className="text-xs text-green-100 mb-4">
            Use this link token at:{` `}
            <a
              href={`https://plaid.com/link?token=${linkToken}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-300 hover:underline font-semibold"
            >
              https://plaid.com/link
            </a>
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(linkToken)
                toast.success('Link token copied to clipboard!')
              }}
              className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-semibold transition"
            >
              📋 Copy Token
            </button>
            <button
              onClick={() => setLinkToken(null)}
              className="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-sm font-semibold transition"
            >
              Reset
            </button>
          </div>
        </div>
      ) : (
        <>
          {error && (
            <div className="bg-red-900/30 border border-red-600 rounded-lg p-4 mb-6">
              <p className="text-sm text-red-200">⚠️ {error}</p>
            </div>
          )}
          <div className="flex gap-2 mb-6">
            <button
              onClick={handleGetLinkToken}
              disabled={loading}
              className="flex-1 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-400 text-white rounded font-semibold transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  Getting Link Token...
                </>
              ) : (
                <>
                  🏦 Get Plaid Link
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-3 bg-slate-600 hover:bg-slate-500 text-white rounded font-semibold transition"
            >
              Cancel
            </button>
          </div>
        </>
      )}

      <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4">
        <p className="text-sm text-blue-200 mb-2">
          ✓ Production Environment
        </p>
        <p className="text-xs text-blue-100">
          Connected to real Plaid production servers. Your family accounts will be securely linked and synced in real-time.
        </p>
      </div>

      <p className="text-xs text-slate-400 mt-4">
        By connecting your account, you agree to Plaid's{' '}
        <a
          href="https://plaid.com/legal/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:underline"
        >
          Terms of Service
        </a>
      </p>
    </div>
  )
}
