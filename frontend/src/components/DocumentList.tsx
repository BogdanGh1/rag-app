import { useState } from 'react'
import { useDocuments } from '../hooks/useDocuments'
import { getDocumentChunks } from '../api/documents'
import { ChunksModal } from './ChunksModal'
import type { DocumentChunk, DocumentListItem } from '../types/api'

interface DocumentListProps {
  dbId: string
}

export function DocumentList({ dbId }: DocumentListProps) {
  const { documents, isLoading, deleteDocument, isDeleting } = useDocuments(dbId)
  const [selectedDoc, setSelectedDoc] = useState<DocumentListItem | null>(null)
  const [chunks, setChunks] = useState<DocumentChunk[]>([])
  const [chunksLoading, setChunksLoading] = useState(false)

  const openChunks = async (doc: DocumentListItem) => {
    setSelectedDoc(doc)
    setChunks([])
    setChunksLoading(true)
    try {
      const data = await getDocumentChunks({ documentId: doc.document_id, dbId })
      setChunks(data)
    } finally {
      setChunksLoading(false)
    }
  }

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading documents...</div>
  }

  return (
    <>
      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-gray-800">
          Indexed Documents {documents.length > 0 && `(${documents.length})`}
        </h2>
        {documents.length === 0 ? (
          <p className="text-sm text-gray-500 py-4 text-center border border-dashed border-gray-200 rounded-lg">
            No documents indexed yet.
          </p>
        ) : (
          <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden">
            {documents.map(doc => (
              <div
                key={doc.document_id}
                className="flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50 cursor-pointer"
                onClick={() => openChunks(doc)}
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                  <p className="text-xs text-gray-500">{doc.chunk_count} chunks</p>
                </div>
                <button
                  onClick={e => { e.stopPropagation(); deleteDocument(doc.document_id) }}
                  disabled={isDeleting}
                  className="text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedDoc && (
        <ChunksModal
          filename={selectedDoc.filename}
          chunks={chunks}
          isLoading={chunksLoading}
          onClose={() => setSelectedDoc(null)}
        />
      )}
    </>
  )
}
