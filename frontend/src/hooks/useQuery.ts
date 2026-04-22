import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { queryDocuments, smartQueryDocuments } from '../api/query'
import type { QueryRequest, QueryResponse, SmartQueryRequest, SmartQueryResponse } from '../types/api'

export function useDocumentQuery() {
  const [lastResult, setLastResult] = useState<QueryResponse | null>(null)

  const mutation = useMutation({
    mutationFn: (request: QueryRequest) => queryDocuments(request),
    onSuccess: (data) => setLastResult(data),
  })

  return {
    ask: mutation.mutate,
    result: lastResult,
    isLoading: mutation.isPending,
    error: mutation.error,
  }
}

export function useSmartQuery() {
  const [lastResult, setLastResult] = useState<SmartQueryResponse | null>(null)

  const mutation = useMutation({
    mutationFn: (request: SmartQueryRequest) => smartQueryDocuments(request),
    onSuccess: (data) => setLastResult(data),
  })

  return {
    ask: mutation.mutate,
    result: lastResult,
    isLoading: mutation.isPending,
    error: mutation.error,
  }
}
