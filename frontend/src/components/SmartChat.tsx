import { useState } from 'react'
import { useSmartQuery } from '../hooks/useQuery'
import type { SmartQueryResponse } from '../types/api'

function RoutingBadge({ result }: { result: SmartQueryResponse }) {
  return (
    <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm">
      <div className="flex flex-wrap gap-1.5 items-center mb-1">
        <span className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Routed to</span>
        {result.routed_databases.map(db => (
          <span
            key={db.id}
            className="px-2 py-0.5 bg-amber-100 text-amber-800 text-xs font-medium rounded-full border border-amber-300"
            title={db.description ?? undefined}
          >
            {db.name}
          </span>
        ))}
      </div>
      <p className="text-xs text-amber-700">{result.routing_explanation}</p>
    </div>
  )
}

function SmartAnswerPanel({ result, isLoading, error }: {
  result: SmartQueryResponse | null
  isLoading: boolean
  error: Error | null
}) {
  const [showSources, setShowSources] = useState(false)

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg animate-pulse">
          <div className="text-xs text-amber-600">Routing question to relevant databases...</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 animate-pulse">
          <div className="text-sm text-gray-400">Generating answer...</div>
        </div>
      </div>
    )
  }

  if (error) {
    const message = (error as any)?.response?.data?.detail ?? error.message
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-sm text-red-700">{message}</p>
      </div>
    )
  }

  if (!result) return null

  return (
    <div className="space-y-3">
      <RoutingBadge result={result} />
      <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-sm font-semibold text-blue-900">Answer</h3>
          <span className="text-xs text-blue-600 font-mono">{result.latency_ms}ms</span>
        </div>
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{result.answer}</p>
      </div>
      {result.sources.length > 0 && (
        <div>
          <button
            onClick={() => setShowSources(s => !s)}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {showSources ? 'Hide' : 'Show'} sources ({result.sources.length})
          </button>
          {showSources && (
            <div className="mt-2 space-y-2">
              {result.sources.map((source, i) => (
                <div key={i} className="p-3 bg-gray-50 rounded border border-gray-200">
                  <div className="flex justify-between items-center mb-1">
                    <p className="text-xs font-medium text-gray-700">{source.filename}</p>
                    {source.score != null && (
                      <p className="text-xs text-gray-400 font-mono">score: {source.score.toFixed(3)}</p>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 line-clamp-3">{source.content_preview}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function SmartChat() {
  const { ask, result, isLoading, error } = useSmartQuery()
  const [question, setQuestion] = useState('')
  const [rerank, setRerank] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim() || isLoading) return
    ask({ question: question.trim(), rerank })
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl mx-auto w-full">
      <div>
        <h2 className="text-lg font-bold text-gray-900">Smart Chat</h2>
        <p className="text-sm text-gray-500 mt-0.5">
          Ask anything — the right database(s) will be selected automatically based on your question.
        </p>
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ask a question across all your databases..."
          disabled={isLoading}
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-60"
        />
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none px-2">
          <input
            type="checkbox"
            checked={rerank}
            onChange={e => setRerank(e.target.checked)}
            className="w-4 h-4 accent-blue-600"
          />
          Rerank
        </label>
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors whitespace-nowrap"
        >
          {isLoading ? 'Thinking...' : 'Ask'}
        </button>
      </form>
      <SmartAnswerPanel result={result} isLoading={isLoading} error={error} />
    </div>
  )
}
