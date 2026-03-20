export interface BackendInfo {
  name: string
  active: boolean
}

export interface BackendsResponse {
  backends: BackendInfo[]
  active: string
}

export interface UploadResponse {
  document_id: string
  filename: string
  chunk_count: number
  backend: string
}

export interface DocumentListItem {
  document_id: string
  filename: string
  chunk_count: number
  created_at?: string
}

export interface SourceDocument {
  document_id: string
  filename: string
  content_preview: string
  score?: number
}

export interface QueryResponse {
  question: string
  answer: string
  sources: SourceDocument[]
  backend_used: string
  latency_ms: number
}

export interface QueryRequest {
  question: string
  backend?: string
  top_k?: number
  llm_model?: string
}
