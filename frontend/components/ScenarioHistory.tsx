function ScenarioAnalytics({ history }: { history: ScenarioHistoryEntry[] }) {
  if (!history.length) return null
  const gains = history.map(e => e.simulated_score - e.original_score)
  const best = Math.max(...gains)
  const worst = Math.min(...gains)
  const avg = gains.reduce((a, b) => a + b, 0) / gains.length
  const mostCommonActions = (() => {
    const freq: Record<string, number> = {}
    history.forEach(e => e.actions.forEach(a => {
      const key = a.description || a.type || 'Unknown'
      freq[key] = (freq[key] || 0) + 1
    }))
    return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 3)
  })()
  return (
    <div className="bg-slate-800 rounded-lg p-4 mb-4 flex flex-wrap gap-6 text-slate-100">
      <div>
        <div className="text-xs uppercase text-slate-400">Total Scenarios</div>
        <div className="text-lg font-bold">{history.length}</div>
      </div>
      <div>
        <div className="text-xs uppercase text-slate-400">Best Gain</div>
        <div className="text-lg font-bold text-green-400">+{best}</div>
      </div>
      <div>
        <div className="text-xs uppercase text-slate-400">Worst Gain</div>
        <div className="text-lg font-bold text-red-400">{worst}</div>
      </div>
      <div>
        <div className="text-xs uppercase text-slate-400">Average Gain</div>
        <div className="text-lg font-bold">{avg.toFixed(1)}</div>
      </div>
      <div>
        <div className="text-xs uppercase text-slate-400">Top Actions</div>
        <ul className="text-xs mt-1">
          {mostCommonActions.map(([action, count]) => (
            <li key={action}>{action} <span className="text-slate-400">({count})</span></li>
          ))}
        </ul>
      </div>
    </div>
  )
}
import { useEffect, useState } from 'react'
function EditableNotes({ profileId, entry, onUpdated }: { profileId: string, entry: ScenarioHistoryEntry, onUpdated: (notes: string, tags: string[], feedback?: string) => void }) {
  const [editing, setEditing] = useState(false)
  const [notes, setNotes] = useState(entry.notes || '')
  const [tags, setTags] = useState<string[]>(entry.tags || [])
  const [tagInput, setTagInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState(entry.feedback || '')

  const handleSave = async () => {
    setSaving(true)
    try {
      // @ts-ignore
      await apiClient.updateScenarioHistoryEntry(profileId, entry.id, { notes, tags })
      if (feedback !== entry.feedback) {
        // @ts-ignore
        await apiClient.updateScenarioFeedback(profileId, entry.id, feedback)
      }
      setEditing(false)
      onUpdated(notes, tags, feedback)
    } catch (err) {
      alert('Failed to update notes/tags/feedback')
    } finally {
      setSaving(false)
    }
  }

  const handleAddTag = () => {
    if (tagInput && !tags.includes(tagInput)) {
      setTags([...tags, tagInput])
      setTagInput('')
    }
  }
  const handleRemoveTag = (tag: string) => setTags(tags.filter(t => t !== tag))

  if (!editing) {
    return (
      <div>
        <div className="flex gap-1 flex-wrap mb-1">
          {tags.map(tag => (
            <span key={tag} className="bg-emerald-700 text-xs px-2 py-0.5 rounded mr-1">{tag}</span>
          ))}
        </div>
        <div className="text-xs text-slate-200 mb-1">{notes}</div>
        {entry.feedback && (
          <div className="text-xs text-amber-300 mb-1">Feedback: {entry.feedback}</div>
        )}
        <button className="text-xs text-blue-300 hover:underline" onClick={() => setEditing(true)}>Edit</button>
      </div>
    )
  }
  return (
    <div className="space-y-1">
      <textarea className="w-full text-xs p-1 rounded" rows={2} value={notes} onChange={e => setNotes(e.target.value)} />
      <div className="flex gap-1 flex-wrap">
        {tags.map(tag => (
          <span key={tag} className="bg-emerald-700 text-xs px-2 py-0.5 rounded mr-1 cursor-pointer" onClick={() => handleRemoveTag(tag)}>{tag} ×</span>
        ))}
        <input className="text-xs px-1 py-0.5 rounded border" value={tagInput} onChange={e => setTagInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddTag(); } }} placeholder="Add tag" />
        <button className="text-xs bg-emerald-600 text-white px-2 py-0.5 rounded" onClick={handleAddTag}>Add</button>
      </div>
      <div className="flex gap-2 mt-1 items-center">
        <button className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded" onClick={handleSave} disabled={saving}>Save</button>
        <button className="text-xs text-slate-400 hover:underline" onClick={() => setEditing(false)}>Cancel</button>
        <select className="text-xs px-2 py-0.5 rounded border ml-2" value={feedback} onChange={e => setFeedback(e.target.value)}>
          <option value="">Feedback...</option>
          <option value="worked">Worked as expected</option>
          <option value="not_realistic">Not realistic</option>
          <option value="uncertain">Uncertain</option>
        </select>
      </div>
    </div>
  )
}
import toast from 'react-hot-toast'
function CompareModal({ entries, onClose }: { entries: ScenarioHistoryEntry[]; onClose: () => void }) {
  if (!entries.length) return null
  const profileId = entries[0].profile_id
  // Only allow PDF download for 2 scenarios (backend limitation)
  const handleDownload = async () => {
    if (entries.length !== 2) return
    try {
      // @ts-ignore
      const blob = await apiClient.downloadScenarioComparisonPdf(profileId, [entries[0].id, entries[1].id])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `scenario_comparison_${entries[0].id}_${entries[1].id}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Scenario comparison PDF downloaded!')
    } catch (err) {
      toast.error('Failed to download scenario comparison PDF')
    }
  }
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white text-slate-900 rounded-lg shadow-lg p-6 min-w-[600px] relative max-w-5xl overflow-x-auto">
        <button onClick={onClose} className="absolute top-2 right-2 text-slate-500 hover:text-slate-800">✕</button>
        <h4 className="text-lg font-bold mb-4">Compare Scenarios</h4>
        <div className="mb-4 flex justify-end">
          <button
            onClick={handleDownload}
            className={`bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-4 py-2 rounded shadow ${entries.length !== 2 ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={entries.length !== 2}
          >
            Download Comparison (PDF)
          </button>
        </div>
        <div className={`grid grid-cols-${entries.length} gap-6`}>
          {entries.map((entry, idx) => (
            <div key={entry.id} className="border rounded p-3 bg-slate-50 min-w-[260px]">
              <div className="font-semibold mb-2">Scenario {String.fromCharCode(65 + idx)}</div>
              <div><b>Date:</b> {new Date(entry.created_at).toLocaleString()}</div>
              <div><b>Original Score:</b> {entry.original_score}</div>
              <div><b>Simulated Score:</b> {entry.simulated_score}</div>
              <div><b>Gain:</b> {entry.actual_gain ?? (entry.simulated_score - entry.original_score)}</div>
              <div><b>Actions:</b>
                <ul className="list-disc ml-4">
                  {entry.actions.map((a, i) => (
                    <li key={i}>{a.description || a.type}</li>
                  ))}
                </ul>
              </div>
              <div><b>Notes:</b> {entry.notes || ''}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
import { apiClient, ScenarioHistoryEntry } from '@/lib/api'
import ScenarioTimeline from './ScenarioTimeline'

interface ScenarioHistoryProps {
  profileId: string
}

export default function ScenarioHistory({ profileId }: ScenarioHistoryProps) {
  const [history, setHistory] = useState<ScenarioHistoryEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<string[]>([])
  const [showCompare, setShowCompare] = useState(false)
  const [search, setSearch] = useState('')
  const [tagFilter, setTagFilter] = useState('')

  useEffect(() => {
    if (!profileId) return
    setLoading(true)
    apiClient.getScenarioHistory(profileId)
      .then(setHistory)
      .catch(() => setError('Failed to load scenario history'))
      .finally(() => setLoading(false))
  }, [profileId])

  const handleSelect = (id: string) => {
    setSelected(prev => {
      if (prev.includes(id)) return prev.filter(x => x !== id)
      if (prev.length === 2) return [prev[1], id] // keep only last two
      return [...prev, id]
    })
  }

  const selectedEntries = selected.map(id => history.find(e => e.id === id)).filter(Boolean) as ScenarioHistoryEntry[]

  // Filtering logic
  let filtered = history
  if (search.trim()) {
    const s = search.trim().toLowerCase()
    filtered = filtered.filter(e =>
      (e.notes && e.notes.toLowerCase().includes(s)) ||
      (e.actions && e.actions.some(a => (a.description || a.type || '').toLowerCase().includes(s)))
    )
  }
  if (tagFilter.trim()) {
    filtered = filtered.filter(e => Array.isArray(e.tags) && e.tags.includes(tagFilter.trim()))
  }

  // Collect all tags for filter dropdown
  const allTags = Array.from(new Set(history.flatMap(e => Array.isArray(e.tags) ? e.tags : [])))

  // Pinned scenarios at the top
  const pinned = filtered.filter(e => e.pinned)
  const unpinned = filtered.filter(e => !e.pinned)

  if (!profileId) return null
  if (loading) return <div className="text-slate-400">Loading scenario history...</div>
  if (error) return <div className="text-red-400">{error}</div>
  if (!history.length) return <div className="text-slate-400">No scenario history yet.</div>

  return (
    <div className="bg-slate-700 rounded-lg p-6 text-white mt-6">
      <ScenarioTimeline history={history} />
      <ScenarioAnalytics history={history} />
      <h3 className="text-xl font-bold mb-4">Scenario History</h3>
      <div className="mb-2 flex flex-wrap gap-2 items-center">
        <span className="text-sm">Select scenarios to compare (up to 4):</span>
        {selected.length >= 2 && (
          <button
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-3 py-1 rounded"
            onClick={() => setShowCompare(true)}
          >Compare</button>
        )}
        {selected.length > 0 && (
          <button
            className="ml-2 text-xs text-slate-300 hover:text-red-400"
            onClick={() => setSelected([])}
          >Clear</button>
        )}
        <input
          className="ml-4 text-xs px-2 py-1 rounded border border-slate-400 bg-slate-800 text-white"
          placeholder="Search notes or actions..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          className="text-xs px-2 py-1 rounded border border-slate-400 bg-slate-800 text-white"
          value={tagFilter}
          onChange={e => setTagFilter(e.target.value)}
        >
          <option value="">Filter by tag</option>
          {allTags.map(tag => (
            <option key={tag} value={tag}>{tag}</option>
          ))}
        </select>
        {tagFilter && (
          <button className="text-xs text-slate-300 hover:text-red-400" onClick={() => setTagFilter('')}>Clear tag</button>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              <th className="px-2 py-1">Compare</th>
              <th className="px-2 py-1">Date</th>
              <th className="px-2 py-1">Original</th>
              <th className="px-2 py-1">Simulated</th>
              <th className="px-2 py-1">Gain</th>
              <th className="px-2 py-1">Actions</th>
              <th className="px-2 py-1">Notes</th>
            </tr>
          </thead>
          <tbody>
            {[...pinned, ...unpinned].map(entry => (
              <tr key={entry.id} className={`border-b border-slate-600 ${selected.includes(entry.id) ? 'bg-emerald-900/40' : ''}`}>
                <td className="px-2 py-1 text-center">
                  <input
                    type="checkbox"
                    checked={selected.includes(entry.id)}
                    onChange={() => handleSelect(entry.id)}
                    disabled={selected.length === 2 && !selected.includes(entry.id)}
                  />
                </td>
                <td className="px-2 py-1 whitespace-nowrap flex items-center gap-1">
                  {entry.pinned && <span title="Pinned" className="text-amber-300">★</span>}
                  {new Date(entry.created_at).toLocaleString()}
                  <button
                    className="ml-1 text-xs text-amber-300 hover:text-amber-400"
                    title={entry.pinned ? 'Unpin' : 'Pin'}
                    onClick={async () => {
                      // @ts-ignore
                      await apiClient.pinScenarioHistoryEntry(profileId, entry.id, !entry.pinned)
                      setHistory(h => h.map(e => e.id === entry.id ? { ...e, pinned: !entry.pinned } : e))
                    }}
                  >{entry.pinned ? 'Unpin' : 'Pin'}</button>
                </td>
                <td className="px-2 py-1 text-center">{entry.original_score}</td>
                <td className="px-2 py-1 text-center">{entry.simulated_score}</td>
                <td className="px-2 py-1 text-center">{entry.actual_gain ?? (entry.simulated_score - entry.original_score)}</td>
                <td className="px-2 py-1">
                  <ul className="list-disc ml-4">
                    {entry.actions.map((a, i) => (
                      <li key={i}>{a.description || a.type}</li>
                    ))}
                  </ul>
                </td>
                <td className="px-2 py-1">
                  <EditableNotes
                    profileId={profileId}
                    entry={entry}
                    onUpdated={(notes, tags) => {
                      setHistory(h => h.map(e => e.id === entry.id ? { ...e, notes, tags } : e))
                    }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showCompare && selectedEntries.length >= 2 && (
        <CompareModal entries={selectedEntries.slice(0, 4)} onClose={() => setShowCompare(false)} />
      )}
    </div>
  )
}
