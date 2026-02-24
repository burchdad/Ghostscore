'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface AddAccountFormProps {
  onClose: () => void
}

export default function AddAccountForm({ onClose }: AddAccountFormProps) {
  const { addAccount, currentProfileId } = useStore()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    type: 'credit_card',
    name: '',
    balance: 0,
    limit: 0,
    open_date: new Date().toISOString().split('T')[0],
    status: 'active',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!currentProfileId) {
      toast.error('Please create and select a profile first')
      return
    }

    if (!formData.name.trim()) {
      toast.error('Account name is required')
      return
    }

    try {
      setLoading(true)
      const account = {
        id: `acc_${Date.now()}`,
        ...formData,
        balance: parseFloat(formData.balance.toString()),
        limit: formData.type === 'credit_card' ? parseFloat(formData.limit.toString()) : undefined,
      }

      // Save to API
      await apiClient.addAccount(currentProfileId, account)
      
      // Update local state
      addAccount(account)
      
      // Reset form
      setFormData({
        type: 'credit_card',
        name: '',
        balance: 0,
        limit: 0,
        open_date: new Date().toISOString().split('T')[0],
        status: 'active',
      })
      
      toast.success('Account added!')
      onClose()
    } catch (err) {
      toast.error('Failed to add account')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">Add Credit Account</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Account Type
            </label>
            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
            >
              <option value="credit_card">Credit Card</option>
              <option value="loan">Personal Loan</option>
              <option value="mortgage">Mortgage</option>
              <option value="auto_loan">Auto Loan</option>
              <option value="student_loan">Student Loan</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Account Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Chase Sapphire"
              className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Current Balance ($)
            </label>
            <input
              type="number"
              name="balance"
              value={formData.balance}
              onChange={handleChange}
              step="0.01"
              className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Credit Limit ($)
            </label>
            <input
              type="number"
              name="limit"
              value={formData.limit}
              onChange={handleChange}
              step="0.01"
              placeholder="Leave 0 for loans"
              disabled={formData.type !== 'credit_card'}
              className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Open Date
            </label>
            <input
              type="date"
              name="open_date"
              value={formData.open_date}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Status
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
            >
              <option value="active">Active</option>
              <option value="closed">Closed</option>
              <option value="charged_off">Charged Off</option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 pt-4">
          <button
            type="submit"
            disabled={loading || !currentProfileId}
            title={!currentProfileId ? 'Create and select a profile first' : ''}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 disabled:cursor-not-allowed text-white rounded font-semibold transition"
          >
            {!currentProfileId ? 'Create a profile first' : loading ? 'Adding...' : 'Add Account'}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded font-semibold transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
