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
  const { databases, isLoading, createDatabase, isCreating, createError, updateDatabase, isUpdating, updateError, deleteDatabase } = useDatabase()
  const { backends } = useBackend()

  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [newBackend, setNewBackend] = useState('vector')

  const [editingDb, setEditingDb] = useState<Database | null>(null)
  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')

  const [confirmDeleteDb, setConfirmDeleteDb] = useState<Database | null>(null)

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    const db = await createDatabase({
      name: newName.trim(),
      description: newDescription.trim() || undefined,
      backend_type: newBackend,
    })
    setNewName('')
    setNewDescription('')
    setShowCreate(false)
    onChange(db)
  }

  const closeModal = () => {
    setShowCreate(false)
    setNewName('')
    setNewDescription('')
    setNewBackend('vector')
  }

  const openEdit = (e: React.MouseEvent, db: Database) => {
    e.stopPropagation()
    setEditingDb(db)
    setEditName(db.name)
    setEditDescription(db.description ?? '')
  }

  const closeEdit = () => {
    setEditingDb(null)
    setEditName('')
    setEditDescription('')
  }

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingDb || !editName.trim()) return
    await updateDatabase({ dbId: editingDb.id, name: editName.trim(), description: editDescription.trim() })
    closeEdit()
  }

  const handleDelete = (e: React.MouseEvent, db: Database) => {
    e.stopPropagation()
    setConfirmDeleteDb(db)
  }

  const confirmDelete = () => {
    if (!confirmDeleteDb) return
    deleteDatabase(confirmDeleteDb.id)
    if (confirmDeleteDb.id === selectedDbId) onDeleteSelected?.()
    setConfirmDeleteDb(null)
  }

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading databases...</div>
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Databases</span>
        <button
          onClick={() => setShowCreate(true)}
          className="px-3 py-1.5 text-sm font-medium rounded-md bg-green-100 text-green-700 hover:bg-green-200 transition-colors"
        >
          + New
        </button>
      </div>

      {showCreate && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={closeModal}
        >
          <div
            className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6 flex flex-col gap-4"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-base font-semibold text-gray-800">New database</h2>
            <form onSubmit={handleCreate} className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-gray-600">Name</label>
                <input
                  type="text"
                  placeholder="e.g. research-papers"
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                  autoFocus
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-gray-600">Description <span className="text-gray-400 font-normal">(optional)</span></label>
                <textarea
                  placeholder="What is this database for?"
                  value={newDescription}
                  onChange={e => setNewDescription(e.target.value)}
                  rows={2}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-gray-600">Backend</label>
                <select
                  value={newBackend}
                  onChange={e => setNewBackend(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                  {backends.map(b => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>
              {createError && (
                <p className="text-xs text-red-600">
                  {(createError as any)?.response?.data?.detail ?? createError.message}
                </p>
              )}
              <div className="flex gap-2 pt-1">
                <button
                  type="submit"
                  disabled={isCreating || !newName.trim()}
                  className="flex-1 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isCreating ? 'Creating...' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 py-2 text-sm font-medium bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editingDb && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={closeEdit}
        >
          <div
            className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6 flex flex-col gap-4"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-base font-semibold text-gray-800">Edit database</h2>
            <form onSubmit={handleEdit} className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-gray-600">Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={e => setEditName(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                  autoFocus
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-gray-600">Description <span className="text-gray-400 font-normal">(optional)</span></label>
                <textarea
                  placeholder="What is this database for?"
                  value={editDescription}
                  onChange={e => setEditDescription(e.target.value)}
                  rows={2}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
                />
              </div>
              {updateError && (
                <p className="text-xs text-red-600">
                  {(updateError as any)?.response?.data?.detail ?? updateError.message}
                </p>
              )}
              <div className="flex gap-2 pt-1">
                <button
                  type="submit"
                  disabled={isUpdating || !editName.trim()}
                  className="flex-1 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isUpdating ? 'Saving...' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={closeEdit}
                  className="flex-1 py-2 text-sm font-medium bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDeleteDb && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => setConfirmDeleteDb(null)}
        >
          <div
            className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6 flex flex-col gap-4"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-base font-semibold text-gray-800">Delete database?</h2>
            <p className="text-sm text-gray-600">
              <span className="font-medium">"{confirmDeleteDb.name}"</span> and all its documents will be permanently deleted.
            </p>
            <div className="flex gap-2 pt-1">
              <button
                onClick={confirmDelete}
                className="flex-1 py-2 text-sm font-medium bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete
              </button>
              <button
                onClick={() => setConfirmDeleteDb(null)}
                className="flex-1 py-2 text-sm font-medium bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
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
                {db.description && (
                  <span className={`text-xs font-normal truncate ${db.id === selectedDbId ? 'text-blue-200' : 'text-gray-400'}`}>
                    {db.description}
                  </span>
                )}
                <span className={`text-xs font-normal ${db.id === selectedDbId ? 'text-blue-200' : 'text-gray-400'}`}>
                  {db.backend_type}
                </span>
              </div>
              <div className="ml-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                <button
                  onClick={e => openEdit(e, db)}
                  className={`text-lg leading-none px-1.5 py-0.5 rounded ${
                    db.id === selectedDbId ? 'text-blue-200 hover:text-white' : 'text-gray-400 hover:text-blue-600'
                  }`}
                  title="Edit database"
                >
                  ✎
                </button>
                <button
                  onClick={e => handleDelete(e, db)}
                  className={`text-xl leading-none px-1.5 py-0.5 rounded ${
                    db.id === selectedDbId ? 'text-blue-200 hover:text-white' : 'text-gray-400 hover:text-red-600'
                  }`}
                  title="Delete database"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
