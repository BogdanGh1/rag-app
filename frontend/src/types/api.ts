export interface ChunkSettings {
  chunk_size: number
  chunk_overlap: number
  section_based: boolean
}

export interface DatabaseSettings {
  chunk?: ChunkSettings
}

export interface Database {
  id: string
  name: string
  description?: string
  backend_type: string
  created_at?: string
  settings?: DatabaseSettings
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

export interface DocumentChunk {
  chunk_index: number
  content: string
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
  db_id: string
  top_k?: number
  llm_model?: string
}

export interface SmartQueryRequest {
  question: string
  top_k?: number
  llm_model?: string
}

export interface RoutedDatabase {
  id: string
  name: string
  description?: string
}

export interface SmartQueryResponse {
  question: string
  answer: string
  sources: SourceDocument[]
  routed_databases: RoutedDatabase[]
  routing_explanation: string
  latency_ms: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
  username: string
}

export interface MeResponse {
  id: string
  username: string
  email: string
}
