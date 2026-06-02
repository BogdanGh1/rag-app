import { useState } from 'react'
import type { QueryResponse } from '../types/api'

interface AnswerPanelProps {
  result: QueryResponse | null
  isLoading: boolean
}

export function AnswerPanel({ result, isLoading }: AnswerPanelProps) {
  const [showSources, setShowSources] = useState(false)

  if (isLoading) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-sm text-gray-500 animate-pulse">Generating answer...</div>
      </div>
    )
  }

  if (!result) return null

  return (
    <div className="space-y-3">
      {result.rewritten_question && (
        <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
          <p className="text-xs font-semibold text-amber-700 mb-1">Rewritten question</p>
          <p className="text-sm text-amber-900 italic">{result.rewritten_question}</p>
        </div>
      )}
      <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-sm font-semibold text-blue-900">Answer</h3>
          <span className="text-xs text-blue-600 font-mono">
            {result.backend_used} · {result.latency_ms}ms
          </span>
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
                      <p className="text-xs text-gray-400 font-mono">
                        score: {source.score.toFixed(3)}
                      </p>
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
