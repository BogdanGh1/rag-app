import { apiClient } from './client'
import type { QueryRequest, QueryResponse } from '../types/api'

export const queryDocuments = async (request: QueryRequest): Promise<QueryResponse> => {
  const response = await apiClient.post<QueryResponse>('/query', request)
  return response.data
}
