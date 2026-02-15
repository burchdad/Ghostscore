'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface ExtractedAccount {
  name: string
  type: string
  balance: number
  limit?: number
  open_date: string
  status: string
}

export default function CreditReportUpload({ onClose }: { onClose: () => void }) {
  const { currentProfileId, addAccount } = useStore()
  const [bureau, setBureau] = useState<'equifax' | 'experian' | 'transunion'>('equifax')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [extractedAccounts, setExtractedAccounts] = useState<ExtractedAccount[]>([])
  const [selectedAccounts, setSelectedAccounts] = useState<Set<number>>(new Set())
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const selectedFile = e.target.files[0]
      // Validate file type
      if (!selectedFile.name.match(/\.(pdf|txt)$/i)) {
        toast.error('Please upload a PDF or TXT file')
        return
      }
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file')
      return
    }

    if (!currentProfileId) {
      toast.error('Please select a profile first')
      return
    }

    try {
      setLoading(true)
      const result = await apiClient.uploadCreditReport(currentProfileId, bureau, file)
      
      // convert accounts to editable form
      setExtractedAccounts(result.accounts.map((a: any) => ({
        ...a,
      })))
      setUploadStatus(result.status)
      
      // Auto-select all accounts by default
      setSelectedAccounts(new Set(Array.from({ length: result.accounts.length }, (_, i) => i)))
      
      toast.success(`Extracted ${result.accounts.length} account(s)`)
    } catch (err) {
      toast.error('Failed to upload credit report')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const toggleAccountSelection = (index: number) => {
    const newSelected = new Set(selectedAccounts)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedAccounts(newSelected)
  }

  const handleImport = async () => {
    if (selectedAccounts.size === 0) {
      toast.error('Please select at least one account to import')
      return
    }

    try {
      setLoading(true)
      const selectedIndices = Array.from(selectedAccounts).sort((a, b) => a - b)
      
      // prepare payload with edited account data for selected indices
      const payloadAccounts = selectedIndices.map((i) => extractedAccounts[i])

      const result = await apiClient.importAccountsFromReport(
        currentProfileId!,
        payloadAccounts,
        undefined
      )

      // Add imported accounts to store using returned ids and our edited payload
      for (let idx = 0; idx < result.accounts.length; idx++) {
        const created = result.accounts[idx]
        const source = payloadAccounts[idx]
        addAccount({
          id: created.id,
          type: source.type,
          name: created.name || source.name,
          balance: source.balance || 0,
          limit: source.limit || undefined,
          open_date: source.open_date || new Date().toISOString().split('T')[0],
          status: source.status || 'active',
        })
      }
      
      toast.success(`Imported ${result.imported_count} accounts`)
      onClose()
    } catch (err) {
      toast.error('Failed to import accounts')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (extractedAccounts.length > 0) {
    return (
      <div className="bg-slate-700 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4">Review Extracted Accounts</h3>
        
        {uploadStatus && (
          <div className="mb-4 p-3 bg-blue-900 text-blue-100 rounded text-sm">
            {uploadStatus}
          </div>
        )}

        <div className="space-y-2 mb-6 max-h-96 overflow-y-auto">
          {extractedAccounts.map((account, idx) => (
              <div
                key={idx}
                className={`p-3 rounded border-2 transition ${
                  selectedAccounts.has(idx)
                    ? 'border-blue-400 bg-blue-900/20'
                    : 'border-slate-600 bg-slate-600/50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedAccounts.has(idx)}
                    onChange={() => toggleAccountSelection(idx)}
                    className="mt-1 w-4 h-4 cursor-pointer"
                  />
                  <div className="flex-1">
                    <div className="font-semibold text-white">
                      <input
                        value={account.name}
                        onChange={(e) => {
                          const copy = [...extractedAccounts]
                          copy[idx] = { ...copy[idx], name: e.target.value }
                          setExtractedAccounts(copy)
                        }}
                        className="w-full bg-transparent text-white font-semibold"
                      />
                    </div>
                    <div className="text-sm text-slate-300 grid grid-cols-3 gap-2 mt-2">
                      <select
                        value={account.type}
                        onChange={(e) => {
                          const copy = [...extractedAccounts]
                          copy[idx] = { ...copy[idx], type: e.target.value }
                          setExtractedAccounts(copy)
                        }}
                        className="px-2 py-1 bg-slate-700 rounded"
                      >
                        <option value="credit_card">Credit Card</option>
                        <option value="auto_loan">Auto Loan</option>
                        <option value="mortgage">Mortgage</option>
                        <option value="student_loan">Student Loan</option>
                        <option value="personal_loan">Personal Loan</option>
                        <option value="other">Other</option>
                      </select>
                      <input
                        value={account.balance}
                        onChange={(e) => {
                          const copy = [...extractedAccounts]
                          copy[idx] = { ...copy[idx], balance: parseFloat(e.target.value || '0') }
                          setExtractedAccounts(copy)
                        }}
                        className="px-2 py-1 bg-slate-700 rounded"
                      />
                      <input
                        value={account.limit || ''}
                        onChange={(e) => {
                          const copy = [...extractedAccounts]
                          copy[idx] = { ...copy[idx], limit: e.target.value ? parseFloat(e.target.value) : undefined }
                          setExtractedAccounts(copy)
                        }}
                        className="px-2 py-1 bg-slate-700 rounded"
                        placeholder="Limit"
                      />
                      <input
                        value={account.open_date}
                        onChange={(e) => {
                          const copy = [...extractedAccounts]
                          copy[idx] = { ...copy[idx], open_date: e.target.value }
                          setExtractedAccounts(copy)
                        }}
                        className="px-2 py-1 bg-slate-700 rounded"
                        placeholder="YYYY-MM-DD"
                      />
                      <select
                        value={account.status}
                        onChange={(e) => {
                          const copy = [...extractedAccounts]
                          copy[idx] = { ...copy[idx], status: e.target.value }
                          setExtractedAccounts(copy)
                        }}
                        className="px-2 py-1 bg-slate-700 rounded"
                      >
                        <option value="active">Active</option>
                        <option value="closed">Closed</option>
                        <option value="charged_off">Charged Off</option>
                        <option value="delinquent">Delinquent</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleImport}
            disabled={loading || selectedAccounts.size === 0}
            className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white rounded font-semibold transition"
          >
            {loading ? 'Importing...' : `Import ${selectedAccounts.size} Account(s)`}
          </button>
          <button
            onClick={() => {
              setExtractedAccounts([])
              setFile(null)
              setSelectedAccounts(new Set())
              setUploadStatus(null)
            }}
            className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded font-semibold transition"
          >
            Back
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded font-semibold transition"
          >
            Cancel
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-700 rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">Upload Credit Report</h3>
      <p className="text-slate-300 mb-6 text-sm">
        Upload your credit report from Equifax, Experian, or Transunion (PDF or TXT format)
      </p>

      <div className="space-y-4 mb-6">
        {/* Bureau Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-200 mb-2">
            Credit Bureau
          </label>
          <select
            value={bureau}
            onChange={(e) => setBureau(e.target.value as any)}
            className="w-full px-3 py-2 bg-slate-600 text-white rounded border border-slate-500 focus:border-blue-400 focus:outline-none"
          >
            <option value="equifax">Equifax</option>
            <option value="experian">Experian</option>
            <option value="transunion">Transunion</option>
          </select>
        </div>

        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-slate-200 mb-2">
            Upload Report File
          </label>
          <div
            className="border-2 border-dashed border-slate-500 rounded-lg p-6 text-center hover:border-blue-400 hover:bg-slate-600/50 transition cursor-pointer"
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            {file ? (
              <div>
                <div className="text-white font-semibold">{file.name}</div>
                <div className="text-slate-400 text-sm mt-1">
                  {(file.size / 1024).toFixed(1)} KB
                </div>
              </div>
            ) : (
              <div>
                <div className="text-slate-300 font-semibold">Click to upload or drag and drop</div>
                <div className="text-slate-400 text-sm mt-1">PDF or TXT files only (max 10MB)</div>
              </div>
            )}
          </div>
        </div>

        {/* File Size Note */}
        <div className="p-3 bg-slate-600/50 rounded text-sm text-slate-300">
          <div className="font-semibold text-slate-200 mb-1">Supported formats:</div>
          <ul className="list-disc list-inside space-y-1">
            <li>PDF files from your credit report</li>
            <li>Plain text credit report</li>
            <li>Works with Equifax, Experian, and Transunion reports</li>
          </ul>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white rounded font-semibold transition"
        >
          {loading ? 'Uploading...' : 'Upload & Extract'}
        </button>
        <button
          onClick={onClose}
          className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded font-semibold transition"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}
