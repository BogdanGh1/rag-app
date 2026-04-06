import { useState } from 'react'
import { AnswerPanel } from './components/AnswerPanel'
import { AuthForm } from './components/AuthForm'
import { DatabaseSelector } from './components/DatabaseSelector'
import { DocumentList } from './components/DocumentList'
import { DocumentUploader } from './components/DocumentUploader'
import { QueryBox } from './components/QueryBox'
import { useAuth } from './contexts/AuthContext'
import { useDocumentQuery } from './hooks/useQuery'
import type { Database, QueryRequest } from './types/api'

function App() {
  const { token, username, logout } = useAuth()
  const [selectedDb, setSelectedDb] = useState<Database | null>(null)
  const { ask, result, isLoading } = useDocumentQuery()

  if (!token) {
    return <AuthForm />
  }

  const askWithDb = (request: Omit<QueryRequest, 'db_id'>) => {
    if (!selectedDb) return
    ask({ ...request, db_id: selectedDb.id })
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">RAG App</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{username}</span>
            <button
              onClick={logout}
              className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Left sidebar — database panel */}
        <aside className="w-72 shrink-0 bg-white border-r border-gray-200 p-5 flex flex-col gap-4">
          <DatabaseSelector selectedDbId={selectedDb?.id ?? null} onChange={setSelectedDb} onDeleteSelected={() => setSelectedDb(null)} />
        </aside>

        {/* Main content */}
        <main className="flex-1 px-8 py-8">
          {!selectedDb ? (
            <div className="text-center py-20 text-gray-500">
              <p className="text-lg">Select or create a database to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl">
              <div className="space-y-6">
                <DocumentUploader dbId={selectedDb.id} />
                <DocumentList dbId={selectedDb.id} />
              </div>
              <div className="space-y-6">
                <QueryBox onAsk={askWithDb} isLoading={isLoading} />
                <AnswerPanel result={result} isLoading={isLoading} />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
