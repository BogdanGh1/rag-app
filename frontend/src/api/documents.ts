import { apiClient } from './client'
import type { DocumentListItem, UploadResponse } from '../types/api'

export const uploadDocuments = async (files: File[]): Promise<UploadResponse[]> => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  const response = await apiClient.post<UploadResponse[]>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const getDocuments = async (): Promise<DocumentListItem[]> => {
  const response = await apiClient.get<DocumentListItem[]>('/documents')
  return response.data
}

export const deleteDocument = async (documentId: string): Promise<void> => {
  await apiClient.delete(`/documents/${documentId}`)
}
