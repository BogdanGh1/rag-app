import { apiClient } from './client'
import type { Database } from '../types/api'

export const getDatabases = async (): Promise<Database[]> => {
  const response = await apiClient.get<Database[]>('/databases')
  return response.data
}

export const createDatabase = async ({
  name,
  description,
  backend_type,
}: {
  name: string
  description?: string
  backend_type: string
}): Promise<Database> => {
  const response = await apiClient.post<Database>('/databases', { name, description, backend_type })
  return response.data
}

export const updateDatabase = async ({
  dbId,
  name,
  description,
}: {
  dbId: string
  name?: string
  description?: string
}): Promise<Database> => {
  const response = await apiClient.patch<Database>(`/databases/${dbId}`, { name, description })
  return response.data
}

export const deleteDatabase = async (dbId: string): Promise<void> => {
  await apiClient.delete(`/databases/${dbId}`)
}
