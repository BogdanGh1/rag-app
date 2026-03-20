import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { queryDocuments } from '../api/query'
import type { QueryRequest, QueryResponse } from '../types/api'

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
