import { apiClient } from './client'
import type { DocumentListItem, UploadResponse } from '../types/api'

export const uploadDocuments = async ({
  files,
  dbId,
}: {
  files: File[]
  dbId: string
}): Promise<UploadResponse[]> => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  formData.append('db_id', dbId)
  const response = await apiClient.post<UploadResponse[]>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const getDocuments = async (dbId: string): Promise<DocumentListItem[]> => {
  const response = await apiClient.get<DocumentListItem[]>('/documents', { params: { db_id: dbId } })
  return response.data
}

export const deleteDocument = async ({
  documentId,
  dbId,
}: {
  documentId: string
  dbId: string
}): Promise<void> => {
  await apiClient.delete(`/documents/${documentId}`, { params: { db_id: dbId } })
}
