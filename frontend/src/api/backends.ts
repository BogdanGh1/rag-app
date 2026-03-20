import { apiClient } from './client'
import type { BackendsResponse } from '../types/api'

export const getBackends = async (): Promise<BackendsResponse> => {
  const response = await apiClient.get<BackendsResponse>('/backends')
  return response.data
}

export const setActiveBackend = async (backend: string): Promise<void> => {
  await apiClient.put('/backends/active', { backend })
}
