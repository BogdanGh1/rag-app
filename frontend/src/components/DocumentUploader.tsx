import { useRef, useState } from 'react'
import { useDocuments } from '../hooks/useDocuments'

export function DocumentUploader() {
  const { uploadFiles, isUploading, uploadError } = useDocuments()
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return
    uploadFiles(Array.from(files))
  }

  return (
    <div className="space-y-2">
      <h2 className="text-lg font-semibold text-gray-800">Upload Documents</h2>
      <div
        onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={e => { e.preventDefault(); setIsDragging(false); handleFiles(e.dataTransfer.files) }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={e => handleFiles(e.target.files)}
        />
        {isUploading ? (
          <p className="text-gray-600">Uploading and indexing...</p>
        ) : (
          <div>
            <p className="text-gray-600">Drag & drop files here, or click to select</p>
            <p className="text-sm text-gray-400 mt-1">PDF, DOCX, TXT supported</p>
          </div>
        )}
      </div>
      {uploadError && (
        <p className="text-sm text-red-600">Upload failed: {uploadError.message}</p>
      )}
    </div>
  )
}
