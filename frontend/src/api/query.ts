import { apiClient } from './client'
import type { QueryRequest, QueryResponse, SmartQueryRequest, SmartQueryResponse } from '../types/api'

export const queryDocuments = async (request: QueryRequest): Promise<QueryResponse> => {
  const response = await apiClient.post<QueryResponse>('/query', request)
  return response.data
}

export const smartQueryDocuments = async (request: SmartQueryRequest): Promise<SmartQueryResponse> => {
  const response = await apiClient.post<SmartQueryResponse>('/query/smart', request)
  return response.data
}
