import { apiClient } from './client'

export const getModels = async (): Promise<string[]> => {
  const response = await apiClient.get<string[]>('/models')
  return response.data
}
