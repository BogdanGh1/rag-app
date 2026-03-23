import { apiClient } from './client'

export const getBackends = async (): Promise<string[]> => {
  const response = await apiClient.get<string[]>('/backends')
  return response.data
}
