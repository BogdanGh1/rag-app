import { apiClient } from './client'
import type { DocumentListItem, UploadResponse } from '../types/api'

export const uploadDocuments = async ({
  files,
  backend,
}: {
  files: File[]
  backend: string
}): Promise<UploadResponse[]> => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  formData.append('backend', backend)
  const response = await apiClient.post<UploadResponse[]>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const getDocuments = async (backend: string): Promise<DocumentListItem[]> => {
  const response = await apiClient.get<DocumentListItem[]>('/documents', { params: { backend } })
  return response.data
}

export const deleteDocument = async ({
  documentId,
  backend,
}: {
  documentId: string
  backend: string
}): Promise<void> => {
  await apiClient.delete(`/documents/${documentId}`, { params: { backend } })
}
