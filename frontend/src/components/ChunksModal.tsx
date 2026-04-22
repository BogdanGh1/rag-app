import { useEffect, useRef } from 'react'
import type { DocumentChunk } from '../types/api'

interface ChunksModalProps {
  filename: string
  chunks: DocumentChunk[]
  isLoading: boolean
  onClose: () => void
}

export function ChunksModal({ filename, chunks, isLoading, onClose }: ChunksModalProps) {
  const backdropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  return (
    <div
      ref={backdropRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={e => { if (e.target === backdropRef.current) onClose() }}
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col mx-4">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-base font-semibold text-gray-900">{filename}</h2>
            {!isLoading && (
              <p className="text-xs text-gray-500 mt-0.5">{chunks.length} chunks</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            &times;
          </button>
        </div>

        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-3">
          {isLoading ? (
            <p className="text-sm text-gray-500 text-center py-8">Loading chunks...</p>
          ) : chunks.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">No chunks found.</p>
          ) : (
            chunks.map(chunk => (
              <div key={chunk.chunk_index} className="border border-gray-200 rounded-lg p-3">
                <p className="text-xs font-medium text-gray-400 mb-1">Chunk {chunk.chunk_index + 1}</p>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{chunk.content}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
