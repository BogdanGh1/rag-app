import { useEffect, useState } from 'react'
import { useModels } from '../hooks/useModels'
import type { QueryRequest } from '../types/api'

interface QueryBoxProps {
  onAsk: (request: Omit<QueryRequest, 'db_id'>) => void
  isLoading: boolean
}

export function QueryBox({ onAsk, isLoading }: QueryBoxProps) {
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(4)
  const [rerank, setRerank] = useState(false)
  const [rewriteQuestion, setRewriteQuestion] = useState(false)
  const [llmModel, setLlmModel] = useState('')
  const { models } = useModels()

  useEffect(() => {
    if (models.length > 0 && !llmModel) setLlmModel(models[0])
  }, [models, llmModel])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return
    onAsk({ question: question.trim(), top_k: topK, rerank, rewrite_question: rewriteQuestion, llm_model: llmModel || undefined })
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
      <div className="flex items-center gap-4 flex-wrap">
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
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={rerank}
            onChange={e => setRerank(e.target.checked)}
            className="w-4 h-4 accent-blue-600"
          />
          Rerank
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={rewriteQuestion}
            onChange={e => setRewriteQuestion(e.target.checked)}
            className="w-4 h-4 accent-blue-600"
          />
          Rewrite question
        </label>
        {models.length > 0 && (
          <select
            value={llmModel}
            onChange={e => setLlmModel(e.target.value)}
            className="border border-gray-300 rounded-lg px-2 py-1 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {models.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        )}
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
