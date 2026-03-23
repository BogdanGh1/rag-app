import { useState } from 'react'
import { AnswerPanel } from './components/AnswerPanel'
import { BackendSelector } from './components/BackendSelector'
import { DocumentList } from './components/DocumentList'
import { DocumentUploader } from './components/DocumentUploader'
import { QueryBox } from './components/QueryBox'
import { useDocumentQuery } from './hooks/useQuery'
import type { QueryRequest } from './types/api'

function App() {
  const [selectedBackend, setSelectedBackend] = useState('vector')
  const { ask, result, isLoading } = useDocumentQuery()

  const askWithBackend = (request: Omit<QueryRequest, 'backend'>) =>
    ask({ ...request, backend: selectedBackend })

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">RAG App</h1>
          <BackendSelector selected={selectedBackend} onChange={setSelectedBackend} />
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
