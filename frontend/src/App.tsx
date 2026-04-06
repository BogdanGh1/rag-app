import { useState } from 'react'
import { AnswerPanel } from './components/AnswerPanel'
import { AuthForm } from './components/AuthForm'
import { BackendSelector } from './components/BackendSelector'
import { DocumentList } from './components/DocumentList'
import { DocumentUploader } from './components/DocumentUploader'
import { QueryBox } from './components/QueryBox'
import { useAuth } from './contexts/AuthContext'
import { useDocumentQuery } from './hooks/useQuery'
import type { QueryRequest } from './types/api'

function App() {
  const { token, username, logout } = useAuth()
  const [selectedBackend, setSelectedBackend] = useState('vector')
  const { ask, result, isLoading } = useDocumentQuery()

  if (!token) {
    return <AuthForm />
  }

  const askWithBackend = (request: Omit<QueryRequest, 'backend'>) =>
    ask({ ...request, backend: selectedBackend })

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">RAG App</h1>
          <div className="flex items-center gap-4">
            <BackendSelector selected={selectedBackend} onChange={setSelectedBackend} />
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

      <main className="max-w-6xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <DocumentUploader backend={selectedBackend} />
          <DocumentList backend={selectedBackend} />
        </div>
        <div className="space-y-6">
          <QueryBox onAsk={askWithBackend} isLoading={isLoading} />
          <AnswerPanel result={result} isLoading={isLoading} />
        </div>
      </main>
    </div>
  )
}

export default App
