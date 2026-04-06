import { useState } from 'react'
import { useBackend } from '../hooks/useBackend'
import { useDatabase } from '../hooks/useDatabase'
import type { Database } from '../types/api'

interface DatabaseSelectorProps {
  selectedDbId: string | null
  onChange: (db: Database) => void
  onDeleteSelected?: () => void
}

export function DatabaseSelector({ selectedDbId, onChange, onDeleteSelected }: DatabaseSelectorProps) {
  const { databases, isLoading, createDatabase, isCreating, createError, deleteDatabase } = useDatabase()
  const { backends } = useBackend()

  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [newBackend, setNewBackend] = useState('vector')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    const db = await createDatabase({ name: newName.trim(), backend_type: newBackend })
    setNewName('')
    setShowCreate(false)
    onChange(db)
  }

  const handleDelete = (e: React.MouseEvent, dbId: string) => {
    e.stopPropagation()
    deleteDatabase(dbId)
    if (dbId === selectedDbId) onDeleteSelected?.()
  }

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading databases...</div>
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Databases</span>
        <button
          onClick={() => setShowCreate(v => !v)}
          className="px-3 py-1.5 text-sm font-medium rounded-md bg-green-100 text-green-700 hover:bg-green-200 transition-colors"
        >
          + New
        </button>
      </div>

      {showCreate && (
        <form
          onSubmit={handleCreate}
          className="flex flex-col gap-3 p-3 border border-gray-200 rounded-lg bg-gray-50"
        >
          <input
            type="text"
            placeholder="Database name"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            autoFocus
          />
          <select
            value={newBackend}
            onChange={e => setNewBackend(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            {backends.map(b => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
          {createError && (
            <p className="text-xs text-red-600">
              {(createError as any)?.response?.data?.detail ?? createError.message}
            </p>
          )}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isCreating || !newName.trim()}
              className="flex-1 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isCreating ? 'Creating...' : 'Create'}
            </button>
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="flex-1 py-2 text-sm font-medium bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {databases.length === 0 ? (
        <p className="text-xs text-gray-400">No databases yet. Create one to get started.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {databases.map(db => (
            <div
              key={db.id}
              onClick={() => onChange(db)}
              className={`group flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium cursor-pointer transition-colors ${
                db.id === selectedDbId
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="flex flex-col min-w-0">
                <span className="truncate">{db.name}</span>
                <span className={`text-xs font-normal ${db.id === selectedDbId ? 'text-blue-200' : 'text-gray-400'}`}>
                  {db.backend_type}
                </span>
              </div>
              <button
                onClick={e => handleDelete(e, db.id)}
                className={`ml-2 opacity-0 group-hover:opacity-100 transition-opacity text-base leading-none shrink-0 ${
                  db.id === selectedDbId ? 'text-blue-200 hover:text-white' : 'text-gray-400 hover:text-red-600'
                }`}
                title="Delete database"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
