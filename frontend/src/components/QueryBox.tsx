import { useState } from 'react'
import type { QueryRequest } from '../types/api'

interface QueryBoxProps {
  onAsk: (request: Omit<QueryRequest, 'db_id'>) => void
  isLoading: boolean
}

export function QueryBox({ onAsk, isLoading }: QueryBoxProps) {
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(4)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return
    onAsk({ question: question.trim(), top_k: topK })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <h2 className="text-lg font-semibold text-gray-800">Ask a Question</h2>
      <textarea
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="Ask something about your documents..."
        rows={8}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        onKeyDown={e => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit(e)
        }}
      />
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          Top-K:
          <input
            type="range"
            min={1}
            max={10}
            value={topK}
            onChange={e => setTopK(Number(e.target.value))}
            className="w-24"
          />
          <span className="w-4 text-center font-mono">{topK}</span>
        </label>
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="ml-auto px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Searching...' : 'Ask'}
        </button>
      </div>
    </form>
  )
}
